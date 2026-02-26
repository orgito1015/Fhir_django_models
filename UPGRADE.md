# Upgrade Plan — FHIR Django Models

This document describes a phased, step-by-step plan for upgrading the FHIR Django Models project to a more modern, secure, and maintainable state.

---

## Table of Contents

1. [Phase 1 — Dependency & Python Upgrades](#phase-1--dependency--python-upgrades)
2. [Phase 2 — Security Hardening](#phase-2--security-hardening)
3. [Phase 3 — Settings & Configuration Cleanup](#phase-3--settings--configuration-cleanup)
4. [Phase 4 — Docker & Container Improvements](#phase-4--docker--container-improvements)
5. [Phase 5 — Developer Tooling & Code Quality](#phase-5--developer-tooling--code-quality)
6. [Phase 6 — Testing Infrastructure](#phase-6--testing-infrastructure)
7. [Phase 7 — CI/CD Pipeline](#phase-7--cicd-pipeline)
8. [Phase 8 — API Completion](#phase-8--api-completion)
9. [Phase 9 — Missing FHIR Resources](#phase-9--missing-fhir-resources)
10. [Phase 10 — Django 6.x Migration](#phase-10--django-6x-migration)
11. [Rollback Strategy](#rollback-strategy)

---

## Phase 1 — Dependency & Python Upgrades

### Python Runtime

| Current | Target | Notes |
|---------|--------|-------|
| Python 3.11 (Dockerfile) | Python 3.13 | EOL for 3.11 is Oct 2027; 3.13 is the latest stable release |

Steps:
1. Update `Dockerfile` base image from `python:3.11-slim` to `python:3.13-slim`.
2. Update `README.md` prerequisites section to require Python 3.13+.
3. Verify all dependencies are compatible with Python 3.13 (`pip check`).

### Python Package Upgrades

Update `requirements.txt` with the following changes:

| Package | Current | Recommended | Notes |
|---------|---------|-------------|-------|
| `Django` | 5.2.3 | **5.2.11** | Latest security-patched LTS-compatible release in the 5.2 series |
| `djangorestframework` | 3.16.0 | **3.16.1** | Minor bug-fix release |
| `gunicorn` | 20.1.0 | **25.1.0** | Major version upgrade with Python 3.12/3.13 support and security fixes |
| `whitenoise` | 6.5.0 | **6.11.0** | Many improvements including brotli support |
| `django-cors-headers` | 4.7.0 | **latest** | Run `pip index versions django-cors-headers` to confirm latest |
| `psycopg2-binary` | ≥2.9.7 | **psycopg[binary]≥3.2** | psycopg3 is the current generation; better async support, improved performance |
| `Pillow` | 11.3.0 | **12.1.1** | Contains important security fixes |
| `bleach` | (unpinned) | **6.3.0** | Must be pinned; unpinned packages are a security risk |
| `drf-yasg` | 1.21.5 | Replace with **drf-spectacular 0.29.0** | `drf-yasg` is minimally maintained; `drf-spectacular` has active support and OpenAPI 3.1 |
| `djangorestframework-simplejwt` | 5.5.0 | **latest 5.x** | Check for security patches |
| `boto3` | ≥1.34.0 | **pin to current** e.g. `boto3==1.38.0` | Avoid unbounded `>=` in production |
| `django-storages` | 1.14.2 | **latest** | Run `pip index versions django-storages` |
| `qrcode[pil]` | 8.2 | **latest** | Run `pip index versions qrcode` |

#### Steps to apply:

```bash
# 1. Create a clean virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip itself
pip install --upgrade pip

# 3. Install upgraded dependencies
pip install -r requirements.txt

# 4. Verify no conflicts
pip check

# 5. Regenerate a pinned lockfile (recommended for reproducible builds)
pip freeze > requirements.lock
```

---

## Phase 2 — Security Hardening

### 2.1 Remove Hardcoded Secret Key

**Problem**: `fhir_demo/settings.py` contains a hardcoded `SECRET_KEY`.

**Fix**: Load it exclusively from the environment variable. Never fall back to a hard-coded insecure value.

```python
# fhir_demo/settings.py
import os

SECRET_KEY = os.environ["SECRET_KEY"]  # Raises KeyError if not set — that is intentional
```

Update `.env.example` to document the variable:
```env
SECRET_KEY=replace-with-a-long-random-string
```

Generate a strong key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.2 Enforce DEBUG=False in Production

```python
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
```

### 2.3 Pin `bleach` Version

`bleach` is listed in `requirements.txt` without a version. This means any version (including vulnerable ones) may be installed. Pin it:

```
bleach==6.3.0
```

### 2.4 Add Production Security Settings

Add the following block to `fhir_demo/settings.py`, activated when `DEBUG=False`:

```python
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000          # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
```

### 2.5 Restrict ALLOWED_HOSTS

Never use `ALLOWED_HOSTS = ['*']` in production:

```python
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

### 2.6 Replace drf-yasg with drf-spectacular

`drf-yasg` has known compatibility issues with newer Django versions and generates Swagger 2.0 (not OpenAPI 3). Replace it with `drf-spectacular`:

```bash
pip uninstall drf-yasg
pip install drf-spectacular==0.29.0
```

Update `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    "drf_spectacular",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FHIR Django Models API",
    "DESCRIPTION": "FHIR R5 REST API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
```

Update `fhir_demo/urls.py`:
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
```

---

## Phase 3 — Settings & Configuration Cleanup

### 3.1 Consolidate Settings Files

Currently there are two configuration files: `fhir_demo/settings.py` (minimal) and `fhir_demo/config.py` (extensive). They overlap and `config.py` references `arewa_backend` (a different project), which is confusing.

Recommended structure:
```
fhir_demo/
  settings/
    __init__.py       # imports from base; selects via DJANGO_ENV
    base.py           # shared settings
    local.py          # local dev overrides
    production.py     # production overrides
    test.py           # test-only overrides
```

Steps:
1. Create `fhir_demo/settings/` directory.
2. Move common settings to `base.py`.
3. Create `local.py` and `production.py` with environment-specific overrides.
4. Update `manage.py`, `wsgi.py`, and `asgi.py` to use the new module path.
5. Remove `fhir_demo/config.py` after its useful portions are migrated (database helpers, CORS helpers).

### 3.2 Load Environment Variables Early

Use `django-environ` (already in requirements) consistently to load `.env`:

```python
# fhir_demo/settings/base.py
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")  # only in local dev
```

### 3.3 Add WhiteNoise to Middleware

`whitenoise` is in requirements but not configured in `settings.py`. Add it:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # must be second
    # ...
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### 3.4 Add CORS Headers to Settings

`django-cors-headers` is in requirements but not in `INSTALLED_APPS` or middleware:

```python
INSTALLED_APPS = [
    # ...
    "corsheaders",
]

MIDDLEWARE = [
    # ...
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ...
]

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```

---

## Phase 4 — Docker & Container Improvements

### 4.1 Upgrade Base Image

```dockerfile
# Before
FROM python:3.11-slim

# After
FROM python:3.13-slim
```

### 4.2 Fix Missing CMD

The current `Dockerfile` has `ENTRYPOINT` but no `CMD`. Add a sensible default:

```dockerfile
ENTRYPOINT ["python", "/app/entrypoint.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "fhir_demo.wsgi:application"]
```

### 4.3 Add docker-compose.yml

Create a `docker-compose.yml` for local development with PostgreSQL:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: fhir_demo
      POSTGRES_USER: fhir_user
      POSTGRES_PASSWORD: fhir_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fhir_user -d fhir_demo"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      DEBUG: "True"
      SECRET_KEY: dev-only-secret-key
      DATABASE_URL: postgresql://fhir_user:fhir_pass@db:5432/fhir_demo
      DJANGO_SETTINGS_MODULE: fhir_demo.settings
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

### 4.4 Add .dockerignore

Create `.dockerignore` to reduce image size:

```
.git
.env
*.pyc
__pycache__
*.sqlite3
.venv
django_env
node_modules
staticfiles
media
```

### 4.5 Add Container Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1
```

---

## Phase 5 — Developer Tooling & Code Quality

### 5.1 Create requirements-dev.txt

```
# Code formatting
black==25.1.0
isort==6.0.1

# Linting
flake8==7.3.0
flake8-django==1.4.0

# Type checking
mypy==1.16.0
django-stubs==5.2.0

# Pre-commit
pre-commit==4.2.0

# Coverage
coverage[toml]==7.8.0
pytest-django==4.11.1
pytest-cov==6.2.0
factory-boy==3.3.3
```

Install with:
```bash
pip install -r requirements-dev.txt
```

### 5.2 Add pyproject.toml for Tool Configuration

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 119
target-version = ["py313"]

[tool.isort]
profile = "black"
line_length = 119
known_django = ["django"]
known_first_party = ["abstractClasses", "components", "patient", "practitioner",
                     "organization", "encounter", "observation", "location",
                     "endpoint", "healthcareservice", "citation", "core"]
sections = ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

[tool.flake8]
max-line-length = 119
extend-ignore = ["E203", "W503"]
exclude = ["migrations", ".venv", "django_env"]

[tool.mypy]
python_version = "3.13"
plugins = ["mypy_django_plugin.main"]
ignore_missing_imports = true

[tool.django-stubs]
django_settings_module = "fhir_demo.settings"

[tool.coverage.run]
source = ["."]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "manage.py",
    "entrypoint.py",
    ".venv/*",
    "django_env/*",
]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 70
```

### 5.3 Add .pre-commit-config.yaml

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 6.0.1
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
```

Install hooks:
```bash
pre-commit install
```

---

## Phase 6 — Testing Infrastructure

### 6.1 Current State

Each app contains a `tests.py` file but they are empty (`# Create your tests here.`). There is no test runner configuration, no fixtures, and no coverage setup.

### 6.2 Add pytest Configuration

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "fhir_demo.settings.test"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--strict-markers --tb=short"
```

### 6.3 Write Model Tests for Each App

For each Django app, replace the empty `tests.py` with meaningful unit tests. Example for `patient`:

```python
# patient/tests.py
from django.test import TestCase
from patient.models import Patient


class PatientModelTest(TestCase):
    def test_create_patient(self):
        patient = Patient.objects.create(active=True, gender="male")
        self.assertIsNotNone(patient.pk)
        self.assertTrue(patient.active)

    def test_deceased_validation(self):
        """Patient cannot have both deceased_boolean and deceased_datetime."""
        from django.core.exceptions import ValidationError
        patient = Patient(active=True, deceased_boolean=True)
        # deceased_datetime should not also be set
        # Add assertion once validation is implemented
```

Priority order for writing tests:
1. `abstractClasses` — base model behaviour
2. `components` — data types used across all apps
3. `patient`, `practitioner`, `organization` — core clinical resources
4. `encounter`, `observation` — workflow resources
5. `location`, `endpoint`, `healthcareservice`, `citation`

### 6.4 Run Tests and Measure Coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Open report
open htmlcov/index.html
```

**Target**: ≥70% line coverage before the 1.0 release.

---

## Phase 7 — CI/CD Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: fhir_test
          POSTGRES_USER: fhir_user
          POSTGRES_PASSWORD: fhir_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with flake8
        run: flake8 .

      - name: Check formatting with black
        run: black --check .

      - name: Check import order with isort
        run: isort --check-only .

      - name: Run migrations
        env:
          SECRET_KEY: ci-only-key
          DATABASE_URL: postgresql://fhir_user:fhir_pass@localhost:5432/fhir_test
          DJANGO_SETTINGS_MODULE: fhir_demo.settings.test
        run: python manage.py migrate

      - name: Run tests with coverage
        env:
          SECRET_KEY: ci-only-key
          DATABASE_URL: postgresql://fhir_user:fhir_pass@localhost:5432/fhir_test
          DJANGO_SETTINGS_MODULE: fhir_demo.settings.test
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        with:
          files: coverage.xml
```

---

## Phase 8 — API Completion

### 8.1 Current State

- `fhir_demo/urls.py` exists but FHIR resource endpoints are not registered.
- Each app has a `views.py` but they are largely empty.
- Serializers exist for `components` and `patient` but not all resources.

### 8.2 Implement ViewSets and Routers

For each FHIR resource app, add a `ViewSet` and register it with a DRF router:

```python
# patient/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["active", "gender"]
    search_fields = ["id"]
    ordering_fields = ["id"]
    ordering = ["-id"]
```

```python
# fhir_demo/urls.py
from rest_framework.routers import DefaultRouter
from patient.views import PatientViewSet
from practitioner.views import PractitionerViewSet
# ... other imports

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"practitioners", PractitionerViewSet, basename="practitioner")
# ... register all resource endpoints

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls")),
]
```

### 8.3 Add Pagination

```python
# fhir_demo/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

### 8.4 Add JWT Authentication Endpoints

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns += [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

### 8.5 Add a Health Check Endpoint

```python
# core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "error", "database": db_ok}, status=status)
```

```python
# fhir_demo/urls.py
from core.views import health_check
urlpatterns += [path("health/", health_check)]
```

---

## Phase 9 — Missing FHIR Resources

The following FHIR R5 resources are listed as "Planned" in the README. Implement them in priority order:

| Priority | Resource | Description |
|----------|----------|-------------|
| 1 | `Condition` | Patient diagnoses and problems |
| 2 | `AllergyIntolerance` | Allergy and intolerance records |
| 3 | `Medication` | Medication definitions |
| 4 | `MedicationRequest` | Medication prescriptions |
| 5 | `Procedure` | Clinical procedures performed |
| 6 | `DiagnosticReport` | Diagnostic test reports |
| 7 | `Appointment` | Scheduled appointments |
| 8 | `RelatedArtifact` | Currently commented out; complete and re-enable |

### Steps to add each new resource:
```bash
# 1. Create the Django app
python manage.py startapp condition

# 2. Implement models following FHIR R5 spec
# 3. Add to INSTALLED_APPS in settings.py
# 4. Create and apply migrations
python manage.py makemigrations condition
python manage.py migrate

# 5. Add serializer, viewset, and register router URL
# 6. Write tests
# 7. Update README and CHANGELOG
```

---

## Phase 10 — Django 6.x Migration

Django 6.0 was released in April 2025. Migrate after completing Phases 1–9.

### Breaking changes to address:

1. **`django.utils.encoding.force_text` removed** — already removed in 4.x; verify no third-party packages still use it.
2. **`Meta.default_related_name`** — review all `ForeignKey` and `ManyToManyField` usages.
3. **`urlpatterns` type hints** — Django 6 enforces stricter URL pattern types.
4. **Database function changes** — review any raw SQL or database functions used in models.
5. **Template engine updates** — verify templates render correctly.

### Migration Steps:

```bash
# 1. Update requirements
# Django==6.0.2

# 2. Run the system check framework
python manage.py check --deploy

# 3. Run all migrations against a fresh DB
python manage.py migrate

# 4. Run the full test suite
pytest

# 5. Review Django 6.0 release notes
# https://docs.djangoproject.com/en/6.0/releases/6.0/
```

---

## Rollback Strategy

For each phase, before applying changes:

1. **Tag the current state**:
   ```bash
   git tag pre-upgrade-phase-N
   git push origin pre-upgrade-phase-N
   ```

2. **Create a feature branch** per phase:
   ```bash
   git checkout -b upgrade/phase-1-dependencies
   ```

3. **Database backups** before running migrations:
   ```bash
   pg_dump fhir_demo > backup_$(date +%Y%m%d).sql
   ```

4. **To rollback a migration**:
   ```bash
   python manage.py migrate <app_name> <previous_migration_number>
   ```

5. **To rollback a dependency upgrade**:
   ```bash
   git checkout requirements.txt
   pip install -r requirements.txt
   ```

---

## Summary Table

| Phase | Effort | Risk | Priority |
|-------|--------|------|----------|
| 1 — Dependencies | Low | Low | 🔴 High |
| 2 — Security Hardening | Low | Low | 🔴 High |
| 3 — Settings Cleanup | Medium | Medium | 🔴 High |
| 4 — Docker | Low | Low | 🟡 Medium |
| 5 — Developer Tooling | Low | Low | 🟡 Medium |
| 6 — Testing | High | Low | 🔴 High |
| 7 — CI/CD | Medium | Low | 🟡 Medium |
| 8 — API Completion | High | Medium | 🟡 Medium |
| 9 — Missing FHIR Resources | High | Medium | 🟢 Low |
| 10 — Django 6.x | Medium | High | 🟢 Low |

> Start with Phases 1, 2, and 3 — they address active security risks and should be completed before any new feature work.

---

*Last updated: 2026-02-26*

"""
URL configuration for fhir_demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fhir/Patient/', include('patient.urls')),
    path('fhir/RelatedPerson/', include('patient.related_person_urls')),
    path('fhir/Organization/', include('organization.urls')),
    path('fhir/Practitioner/', include('practitioner.urls')),
    path('fhir/PractitionerRole/', include('practitioner.role_urls')),
    path('fhir/Encounter/', include('encounter.urls')),
    path('fhir/Observation/', include('observation.urls')),
    path('fhir/Location/', include('location.urls')),
    path('fhir/HealthcareService/', include('healthcareservice.urls')),
    path('fhir/Endpoint/', include('endpoint.urls')),
]


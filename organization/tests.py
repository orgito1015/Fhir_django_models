from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Organization, OrganizationQualification
from components.models import CodeableConcept


class OrganizationModelTest(TestCase):
    """Tests for FHIR R5 Organization model"""

    def test_create_organization_with_name(self):
        """Can create an Organization with a name"""
        org = Organization.objects.create(name='Test Hospital')
        self.assertEqual(org.name, 'Test Hospital')

    def test_organization_requires_name_or_identifier(self):
        """Organization must have at least a name or identifier (FHIR rule)"""
        org = Organization.objects.create()
        with self.assertRaises(ValidationError):
            org.clean()

    def test_organization_valid_with_name(self):
        """Organization with name passes validation"""
        org = Organization.objects.create(name='Test Clinic')
        org.clean()  # Should not raise

    def test_organization_str(self):
        """Organization __str__ returns useful representation"""
        org = Organization.objects.create(name='Test Hospital')
        self.assertIn('Test Hospital', str(org))

    def test_organization_active_flag(self):
        """Organization can be marked active or inactive"""
        org_active = Organization.objects.create(name='Active Hospital', active=True)
        org_inactive = Organization.objects.create(name='Inactive Hospital', active=False)
        self.assertTrue(org_active.active)
        self.assertFalse(org_inactive.active)

    def test_organization_part_of(self):
        """Organization can have a parent organization"""
        parent = Organization.objects.create(name='Parent Org')
        child = Organization.objects.create(name='Child Org', partOf=parent)
        self.assertEqual(child.partOf, parent)
        self.assertEqual(parent.child_organizations.count(), 1)

    def test_organization_alias_json_field(self):
        """Organization alias is stored as JSON array"""
        org = Organization.objects.create(
            name='Test Org',
            alias=['Alias 1', 'Alias 2'],
        )
        self.assertEqual(len(org.alias), 2)
        self.assertIn('Alias 1', org.alias)

    def test_organization_qualification_creation(self):
        """Can create an OrganizationQualification"""
        org = Organization.objects.create(name='Test Hospital')
        code = CodeableConcept.objects.create(text='JCAHO')
        qual = OrganizationQualification.objects.create(
            organization=org,
            code=code,
        )
        self.assertEqual(org.qualifications.count(), 1)
        self.assertEqual(qual.code, code)

    def test_organization_indexes(self):
        """Organization model has expected indexed fields"""
        field_names = [f.name for f in Organization._meta.get_fields()]
        self.assertIn('name', field_names)
        self.assertIn('active', field_names)


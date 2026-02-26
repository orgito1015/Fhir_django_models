from django.test import TestCase
from .models import HealthcareService, HealthcareServiceEligibility
from components.models import CodeableConcept
from organization.models import Organization
from location.models import Location


class HealthcareServiceModelTest(TestCase):
    """Tests for FHIR R5 HealthcareService model"""

    def test_create_minimal_healthcare_service(self):
        """Can create a minimal HealthcareService"""
        svc = HealthcareService.objects.create()
        self.assertIsNotNone(svc.pk)

    def test_healthcare_service_with_name(self):
        """Can create a HealthcareService with a name"""
        svc = HealthcareService.objects.create(name='Radiology', active=True)
        self.assertEqual(svc.name, 'Radiology')
        self.assertTrue(svc.active)

    def test_healthcare_service_str(self):
        """HealthcareService __str__ returns useful representation"""
        svc = HealthcareService.objects.create(name='Cardiology', active=True)
        self.assertIn('Cardiology', str(svc))

    def test_healthcare_service_provided_by(self):
        """HealthcareService can be provided by an Organization"""
        org = Organization.objects.create(name='Test Hospital')
        svc = HealthcareService.objects.create(
            name='Emergency',
            providedBy=org,
        )
        self.assertEqual(svc.providedBy, org)
        self.assertEqual(org.provided_healthcare_services.count(), 1)

    def test_healthcare_service_location(self):
        """HealthcareService can be linked to Locations"""
        loc = Location.objects.create(name='Main Building')
        svc = HealthcareService.objects.create(name='Lab')
        svc.location.add(loc)
        self.assertEqual(svc.location.count(), 1)

    def test_healthcare_service_offered_in(self):
        """HealthcareService can be offered within another HealthcareService"""
        parent_svc = HealthcareService.objects.create(name='Parent Service')
        child_svc = HealthcareService.objects.create(name='Child Service')
        parent_svc.offeredIn.add(child_svc)
        self.assertEqual(parent_svc.offeredIn.count(), 1)

    def test_healthcare_service_eligibility(self):
        """Can create a HealthcareServiceEligibility"""
        svc = HealthcareService.objects.create(name='Specialized Care')
        code = CodeableConcept.objects.create(text='Age >= 18')
        elig = HealthcareServiceEligibility.objects.create(
            healthcare_service=svc,
            code=code,
            comment='Adults only',
        )
        self.assertEqual(svc.eligibilities.count(), 1)
        self.assertEqual(elig.comment, 'Adults only')

    def test_healthcare_service_indexes(self):
        """HealthcareService model has expected indexed fields"""
        field_names = [f.name for f in HealthcareService._meta.get_fields()]
        self.assertIn('active', field_names)
        self.assertIn('name', field_names)
        self.assertIn('providedBy', field_names)


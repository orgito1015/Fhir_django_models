from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Practitioner, PractitionerRole, PractitionerQualification, PractitionerCommunication
from components.models import CodeableConcept, Period
from organization.models import Organization


class PractitionerModelTest(TestCase):
    """Tests for FHIR R5 Practitioner model"""

    def test_create_minimal_practitioner(self):
        """Can create a minimal Practitioner"""
        prac = Practitioner.objects.create()
        self.assertIsNotNone(prac.pk)

    def test_practitioner_gender_choices(self):
        """Practitioner gender must be a valid FHIR code"""
        for gender in ['male', 'female', 'other', 'unknown']:
            p = Practitioner.objects.create(gender=gender)
            self.assertEqual(p.gender, gender)

    def test_practitioner_deceased_both_invalid(self):
        """Only one deceased[x] can be set"""
        import datetime
        p = Practitioner(
            deceasedBoolean=True,
            deceasedDateTime=datetime.datetime.now(),
        )
        with self.assertRaises(ValidationError):
            p.clean()

    def test_practitioner_str(self):
        """Practitioner __str__ returns useful representation"""
        p = Practitioner.objects.create(fhir_id='pr-1', active=True)
        self.assertIn('pr-1', str(p))

    def test_practitioner_qualification_creation(self):
        """Can create a PractitionerQualification"""
        prac = Practitioner.objects.create()
        code = CodeableConcept.objects.create(text='MD')
        qual = PractitionerQualification.objects.create(
            practitioner=prac,
            code=code,
        )
        self.assertEqual(prac.qualifications.count(), 1)
        self.assertEqual(qual.code.text, 'MD')

    def test_practitioner_communication_creation(self):
        """Can create a PractitionerCommunication"""
        prac = Practitioner.objects.create()
        lang = CodeableConcept.objects.create(text='en')
        comm = PractitionerCommunication.objects.create(
            practitioner=prac,
            language=lang,
            preferred=True,
        )
        self.assertEqual(prac.communications.count(), 1)
        self.assertTrue(comm.preferred)


class PractitionerRoleModelTest(TestCase):
    """Tests for FHIR R5 PractitionerRole model"""

    def setUp(self):
        self.org = Organization.objects.create(name='Test Hospital')
        self.prac = Practitioner.objects.create()

    def test_create_practitioner_role(self):
        """Can create a PractitionerRole"""
        role = PractitionerRole.objects.create(
            practitioner=self.prac,
            organization=self.org,
            active=True,
        )
        self.assertEqual(role.practitioner, self.prac)
        self.assertEqual(role.organization, self.org)
        self.assertTrue(role.active)

    def test_practitioner_role_without_practitioner(self):
        """PractitionerRole can be created without a practitioner"""
        role = PractitionerRole.objects.create(active=True)
        self.assertIsNone(role.practitioner)

    def test_practitioner_role_indexes(self):
        """PractitionerRole model has expected fields"""
        field_names = [f.name for f in PractitionerRole._meta.get_fields()]
        self.assertIn('active', field_names)
        self.assertIn('practitioner', field_names)
        self.assertIn('organization', field_names)


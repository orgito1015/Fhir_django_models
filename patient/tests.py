from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Patient, RelatedPerson, PatientContact, PatientCommunication, PatientLink
from components.models import CodeableConcept, Period
from organization.models import Organization


class PatientModelTest(TestCase):
    """Tests for FHIR R5 Patient model"""

    def test_create_minimal_patient(self):
        """Can create a minimal Patient"""
        patient = Patient.objects.create()
        self.assertIsNotNone(patient.pk)

    def test_patient_gender_choices(self):
        """Patient gender must be a valid FHIR code"""
        for gender in ['male', 'female', 'other', 'unknown']:
            p = Patient.objects.create(gender=gender)
            self.assertEqual(p.gender, gender)

    def test_patient_deceased_both_invalid(self):
        """Only one deceased[x] can be set"""
        import datetime
        p = Patient(
            deceasedBoolean=True,
            deceasedDateTime=datetime.datetime.now(),
        )
        with self.assertRaises(ValidationError):
            p.clean()

    def test_patient_multiple_birth_both_invalid(self):
        """Only one multipleBirth[x] can be set"""
        p = Patient(
            multipleBirthBoolean=True,
            multipleBirthInteger=2,
        )
        with self.assertRaises(ValidationError):
            p.clean()

    def test_patient_str(self):
        """Patient __str__ returns useful representation"""
        p = Patient.objects.create(fhir_id='pt-1', active=True)
        self.assertIn('pt-1', str(p))

    def test_patient_indexes(self):
        """Patient model has expected indexed fields"""
        field_names = [f.name for f in Patient._meta.get_fields()]
        self.assertIn('active', field_names)
        self.assertIn('gender', field_names)
        self.assertIn('birthDate', field_names)


class RelatedPersonModelTest(TestCase):
    """Tests for FHIR R5 RelatedPerson model"""

    def setUp(self):
        self.patient = Patient.objects.create(fhir_id='pt-test')

    def test_create_related_person(self):
        """Can create a RelatedPerson linked to a Patient"""
        rp = RelatedPerson.objects.create(patient=self.patient)
        self.assertEqual(rp.patient, self.patient)

    def test_related_person_str(self):
        """RelatedPerson __str__ returns useful representation"""
        rp = RelatedPerson.objects.create(patient=self.patient, active=True)
        self.assertIn('active=True', str(rp))

    def test_related_person_cascade_delete(self):
        """Deleting a patient deletes related persons"""
        rp = RelatedPerson.objects.create(patient=self.patient)
        pk = rp.pk
        self.patient.delete()
        self.assertFalse(RelatedPerson.objects.filter(pk=pk).exists())


class PatientLinkModelTest(TestCase):
    """Tests for PatientLink model"""

    def setUp(self):
        self.p1 = Patient.objects.create(fhir_id='pt-1')
        self.p2 = Patient.objects.create(fhir_id='pt-2')

    def test_patient_link_requires_exactly_one_other(self):
        """PatientLink must reference exactly one other Patient or RelatedPerson"""
        link = PatientLink(patient=self.p1, type='refer')
        with self.assertRaises(ValidationError):
            link.clean()

    def test_patient_link_valid(self):
        """PatientLink is valid when referencing exactly one other"""
        link = PatientLink.objects.create(
            patient=self.p1,
            other_patient=self.p2,
            type='refer',
        )
        link.clean()  # Should not raise
        self.assertEqual(link.other_patient, self.p2)

    def test_patient_link_type_choices(self):
        """PatientLink type must be a valid code"""
        for link_type in ['replaced-by', 'replaces', 'refer', 'seealso']:
            link = PatientLink.objects.create(
                patient=self.p1,
                other_patient=self.p2,
                type=link_type,
            )
            self.assertEqual(link.type, link_type)


class PatientCommunicationModelTest(TestCase):
    """Tests for PatientCommunication model"""

    def test_patient_communication_creation(self):
        """Can create a PatientCommunication"""
        patient = Patient.objects.create()
        language = CodeableConcept.objects.create(text='English')
        comm = PatientCommunication.objects.create(
            patient=patient,
            language=language,
            preferred=True,
        )
        self.assertEqual(patient.communications.count(), 1)
        self.assertTrue(comm.preferred)


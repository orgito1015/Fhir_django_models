from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import (
    Encounter, EncounterParticipant, EncounterDiagnosis,
    EncounterAdmission, EncounterLocation, EncounterReason
)
from components.models import CodeableConcept, Period
from components.reference import Reference
import datetime


class EncounterModelTest(TestCase):
    """Tests for FHIR R5 Encounter model"""

    def setUp(self):
        self.class_concept = CodeableConcept.objects.create(text='inpatient')

    def test_create_minimal_encounter(self):
        """Can create a minimal Encounter with required fields"""
        enc = Encounter.objects.create(
            status='planned',
            class_field=self.class_concept,
        )
        self.assertEqual(enc.status, 'planned')
        self.assertEqual(enc.class_field, self.class_concept)

    def test_encounter_status_choices(self):
        """Encounter status must be a valid FHIR code"""
        valid_statuses = [
            'planned', 'in-progress', 'on-hold', 'discharged',
            'completed', 'cancelled', 'discontinued', 'entered-in-error', 'unknown'
        ]
        for s in valid_statuses:
            enc = Encounter.objects.create(status=s, class_field=self.class_concept)
            self.assertEqual(enc.status, s)

    def test_encounter_planned_dates_validation(self):
        """Encounter planned start must be before planned end"""
        enc = Encounter(
            status='planned',
            class_field=self.class_concept,
            plannedStartDate=datetime.datetime(2025, 1, 10, tzinfo=datetime.timezone.utc),
            plannedEndDate=datetime.datetime(2025, 1, 5, tzinfo=datetime.timezone.utc),
        )
        with self.assertRaises(ValidationError):
            enc.clean()

    def test_encounter_valid_dates(self):
        """Encounter with valid dates passes validation"""
        enc = Encounter.objects.create(
            status='planned',
            class_field=self.class_concept,
            plannedStartDate=datetime.datetime(2025, 1, 5, tzinfo=datetime.timezone.utc),
            plannedEndDate=datetime.datetime(2025, 1, 10, tzinfo=datetime.timezone.utc),
        )
        enc.clean()  # Should not raise

    def test_encounter_str(self):
        """Encounter __str__ returns useful representation"""
        enc = Encounter.objects.create(
            status='completed',
            class_field=self.class_concept,
        )
        self.assertIn('completed', str(enc))

    def test_encounter_type_many_to_many(self):
        """Encounter can have multiple types"""
        enc = Encounter.objects.create(status='final', class_field=self.class_concept)
        enc_type = CodeableConcept.objects.create(text='outpatient')
        enc.type.add(enc_type)
        self.assertEqual(enc.type.count(), 1)

    def test_encounter_participant_creation(self):
        """Can create an EncounterParticipant"""
        enc = Encounter.objects.create(status='in-progress', class_field=self.class_concept)
        participant = EncounterParticipant.objects.create(encounter=enc)
        self.assertEqual(enc.participants.count(), 1)

    def test_encounter_diagnosis_creation(self):
        """Can create an EncounterDiagnosis"""
        enc = Encounter.objects.create(status='in-progress', class_field=self.class_concept)
        ref = Reference.objects.create(reference='Condition/cond-1')
        diagnosis = EncounterDiagnosis.objects.create(
            encounter=enc,
            condition=ref,
        )
        self.assertEqual(enc.diagnoses.count(), 1)

    def test_encounter_admission_creation(self):
        """Can create an EncounterAdmission"""
        enc = Encounter.objects.create(status='in-progress', class_field=self.class_concept)
        admission = EncounterAdmission.objects.create(encounter=enc)
        self.assertEqual(enc.admission, admission)

    def test_encounter_location_status_choices(self):
        """EncounterLocation status must be valid"""
        enc = Encounter.objects.create(status='in-progress', class_field=self.class_concept)
        ref = Reference.objects.create(reference='Location/loc-1')
        for loc_status in ['planned', 'active', 'reserved', 'completed']:
            loc = EncounterLocation.objects.create(
                encounter=enc,
                location=ref,
                status=loc_status,
            )
            self.assertEqual(loc.status, loc_status)

    def test_encounter_indexes(self):
        """Encounter model has expected indexed fields"""
        field_names = [f.name for f in Encounter._meta.get_fields()]
        self.assertIn('status', field_names)
        self.assertIn('plannedStartDate', field_names)
        self.assertIn('plannedEndDate', field_names)


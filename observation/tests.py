from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Observation, ObservationComponent, ObservationReferenceRange, ObservationTriggeredBy
from components.models import CodeableConcept, Quantity, Period, Range


class ObservationModelTest(TestCase):
    """Tests for FHIR R5 Observation model"""

    def setUp(self):
        self.code = CodeableConcept.objects.create(text="Blood Pressure")
        self.category = CodeableConcept.objects.create(text="vital-signs")

    def test_create_minimal_observation(self):
        """Can create a minimal Observation with required fields only"""
        obs = Observation.objects.create(
            status='final',
            code=self.code,
        )
        self.assertEqual(obs.status, 'final')
        self.assertEqual(obs.code, self.code)

    def test_observation_status_choices(self):
        """Observation status must be a valid FHIR status code"""
        valid_statuses = [
            'registered', 'preliminary', 'final', 'amended',
            'corrected', 'cancelled', 'entered-in-error', 'unknown'
        ]
        for s in valid_statuses:
            obs = Observation.objects.create(status=s, code=self.code)
            self.assertEqual(obs.status, s)

    def test_observation_with_string_value(self):
        """Observation can hold a string value"""
        obs = Observation.objects.create(
            status='final',
            code=self.code,
            valueString='Normal',
        )
        self.assertEqual(obs.valueString, 'Normal')

    def test_observation_with_boolean_value(self):
        """Observation can hold a boolean value"""
        obs = Observation.objects.create(
            status='final',
            code=self.code,
            valueBoolean=True,
        )
        self.assertTrue(obs.valueBoolean)

    def test_observation_with_integer_value(self):
        """Observation can hold an integer value"""
        obs = Observation.objects.create(
            status='final',
            code=self.code,
            valueInteger=42,
        )
        self.assertEqual(obs.valueInteger, 42)

    def test_observation_with_quantity_value(self):
        """Observation can hold a Quantity value"""
        qty = Quantity.objects.create(value=120, unit='mmHg')
        obs = Observation.objects.create(
            status='final',
            code=self.code,
            valueQuantity=qty,
        )
        self.assertEqual(obs.valueQuantity, qty)

    def test_observation_multiple_values_invalid(self):
        """Observation cannot have multiple value[x] fields"""
        qty = Quantity.objects.create(value=120, unit='mmHg')
        obs = Observation(
            status='final',
            code=self.code,
            valueString='Normal',
            valueQuantity=qty,
        )
        with self.assertRaises(ValidationError):
            obs.clean()

    def test_observation_data_absent_reason_with_value_invalid(self):
        """dataAbsentReason is not allowed when value[x] is present"""
        absent_reason = CodeableConcept.objects.create(text='unknown')
        obs = Observation.objects.create(
            status='final',
            code=self.code,
            valueString='Normal',
            dataAbsentReason=absent_reason,
        )
        with self.assertRaises(ValidationError):
            obs.clean()

    def test_observation_multiple_effective_invalid(self):
        """Observation cannot have multiple effective[x] fields"""
        import datetime
        period = Period.objects.create()
        obs = Observation(
            status='final',
            code=self.code,
            effectiveDateTime=datetime.datetime.now(),
            effectivePeriod=period,
        )
        with self.assertRaises(ValidationError):
            obs.clean()

    def test_observation_str(self):
        """Observation __str__ returns useful representation"""
        obs = Observation.objects.create(status='final', code=self.code)
        self.assertIn('final', str(obs))

    def test_observation_component_creation(self):
        """Can create an ObservationComponent"""
        obs = Observation.objects.create(status='final', code=self.code)
        comp_code = CodeableConcept.objects.create(text='Systolic BP')
        comp = ObservationComponent.objects.create(
            observation=obs,
            code=comp_code,
            valueInteger=120,
        )
        self.assertEqual(comp.observation, obs)
        self.assertEqual(comp.valueInteger, 120)
        self.assertEqual(obs.components.count(), 1)

    def test_observation_component_multiple_values_invalid(self):
        """ObservationComponent cannot have multiple value[x] fields"""
        obs = Observation.objects.create(status='final', code=self.code)
        comp_code = CodeableConcept.objects.create(text='Systolic BP')
        comp = ObservationComponent(
            observation=obs,
            code=comp_code,
            valueInteger=120,
            valueString='high',
        )
        with self.assertRaises(ValidationError):
            comp.clean()

    def test_observation_reference_range_creation(self):
        """Can create an ObservationReferenceRange"""
        obs = Observation.objects.create(status='final', code=self.code)
        low = Quantity.objects.create(value=60, unit='mmHg')
        high = Quantity.objects.create(value=100, unit='mmHg')
        rr = ObservationReferenceRange.objects.create(
            observation=obs,
            low=low,
            high=high,
            text='Normal range'
        )
        self.assertEqual(obs.reference_ranges.count(), 1)
        self.assertEqual(rr.text, 'Normal range')

    def test_observation_triggered_by_creation(self):
        """Can create an ObservationTriggeredBy"""
        obs1 = Observation.objects.create(status='final', code=self.code)
        obs2 = Observation.objects.create(status='final', code=self.code)
        triggered = ObservationTriggeredBy.objects.create(
            observation=obs1,
            triggering_observation=obs2,
            type='reflex',
        )
        self.assertEqual(obs1.triggered_by.count(), 1)
        self.assertEqual(triggered.type, 'reflex')

    def test_observation_category_many_to_many(self):
        """Observation can have multiple categories"""
        obs = Observation.objects.create(status='final', code=self.code)
        obs.category.add(self.category)
        self.assertEqual(obs.category.count(), 1)

    def test_observation_has_member(self):
        """Observation can reference member observations"""
        obs1 = Observation.objects.create(status='final', code=self.code)
        obs2 = Observation.objects.create(status='final', code=self.code)
        obs1.hasMember.add(obs2)
        self.assertEqual(obs1.hasMember.count(), 1)

    def test_observation_indexes(self):
        """Observation model has correct indexes"""
        field_names = [f.name for f in Observation._meta.get_fields()]
        self.assertIn('status', field_names)
        self.assertIn('effectiveDateTime', field_names)
        self.assertIn('issued', field_names)


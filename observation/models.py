from django.db import models
from django.core.exceptions import ValidationError
from abstractClasses.models import DomainResource, BackboneElement


class ObservationTriggeredBy(BackboneElement):
    """Identifies the observation(s) that triggered the performance of this observation"""
    # Observation this triggered-by belongs to
    observation = models.ForeignKey('Observation', on_delete=models.CASCADE, related_name='triggered_by')
    # Reference to the triggering observation (1..1 Reference(Observation))
    triggering_observation = models.ForeignKey('Observation', on_delete=models.CASCADE, related_name='triggered_observations')
    # reflex | repeat | re-run (1..1 code)
    type = models.CharField(max_length=16, choices=[
        ('reflex', 'Reflex'), ('repeat', 'Repeat'), ('re-run', 'Re-run')
    ])
    # Reason the observation was triggered (0..1 string)
    reason = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        db_table = 'observation_triggered_by'


class ObservationReferenceRange(BackboneElement):
    """Provides guide for interpretation of component result"""
    # Observation this reference range belongs to
    observation = models.ForeignKey('Observation', on_delete=models.CASCADE, related_name='reference_ranges', null=True, blank=True)
    # Observation component this reference range belongs to (optional)
    component = models.ForeignKey('ObservationComponent', on_delete=models.CASCADE, related_name='reference_ranges', null=True, blank=True)
    # Low Range, if relevant (0..1 Quantity)
    low = models.ForeignKey('components.Quantity', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_ref_range_lows')
    # High Range, if relevant (0..1 Quantity)
    high = models.ForeignKey('components.Quantity', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_ref_range_highs')
    # Reference range population (0..1 CodeableConcept)
    normalValue = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_ref_range_normal_values')
    # Condition the observation applies to (0..1 CodeableConcept)
    type = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_ref_range_types')
    # Applicable age range, if relevant (0..* CodeableConcept)
    appliesTo = models.ManyToManyField('components.CodeableConcept', blank=True, related_name='obs_ref_range_applies_to')
    # Applicable age range, if relevant (0..1 Range)
    age = models.ForeignKey('components.Range', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_reference_ranges')
    # Text based reference range in an observation (0..1 markdown)
    text = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'observation_reference_range'


class ObservationComponent(BackboneElement):
    """Component results - used when reporting multi-component observations"""
    # Observation this component belongs to
    observation = models.ForeignKey('Observation', on_delete=models.CASCADE, related_name='components')
    # Type of component observation (1..1 CodeableConcept)
    code = models.ForeignKey('components.CodeableConcept', on_delete=models.CASCADE, related_name='observation_components')
    # Provides a reason why the expected value in the element was missing (0..1 CodeableConcept)
    dataAbsentReason = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_component_data_absent_reasons')
    # High, low, normal, etc. (0..* CodeableConcept)
    interpretation = models.ManyToManyField('components.CodeableConcept', blank=True, related_name='obs_component_interpretations')

    # value[x] choice type - only one should be set
    valueQuantity = models.ForeignKey('components.Quantity', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_component_values')
    valueCodeableConcept = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_component_value_cc')
    valueString = models.CharField(max_length=1024, null=True, blank=True)
    valueBoolean = models.BooleanField(null=True, blank=True)
    valueInteger = models.IntegerField(null=True, blank=True)
    valueRange = models.ForeignKey('components.Range', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_component_value_ranges')
    valuePeriod = models.ForeignKey('components.Period', null=True, blank=True, on_delete=models.SET_NULL, related_name='obs_component_value_periods')
    valueDateTime = models.DateTimeField(null=True, blank=True)
    valueTime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'observation_component'

    def clean(self):
        super().clean()
        value_fields = [
            'valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean',
            'valueInteger', 'valueRange', 'valuePeriod', 'valueDateTime', 'valueTime'
        ]
        set_values = [f for f in value_fields if getattr(self, f) is not None]
        if len(set_values) > 1:
            raise ValidationError("Only one value[x] can be set per ObservationComponent")


class Observation(DomainResource):
    """Measurements and simple assertions made about a patient, device or other subject"""

    # registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown (1..1 code)
    status = models.CharField(max_length=32, choices=[
        ('registered', 'Registered'),
        ('preliminary', 'Preliminary'),
        ('final', 'Final'),
        ('amended', 'Amended'),
        ('corrected', 'Corrected'),
        ('cancelled', 'Cancelled'),
        ('entered-in-error', 'Entered in Error'),
        ('unknown', 'Unknown'),
    ])

    # Classification of type of observation (0..* CodeableConcept)
    category = models.ManyToManyField('components.CodeableConcept', blank=True, related_name='observation_categories')

    # Type of observation (1..1 CodeableConcept)
    code = models.ForeignKey('components.CodeableConcept', on_delete=models.CASCADE, related_name='observations')

    # Who and/or what the observation is about (0..1 Reference)
    subject = models.ForeignKey('components.Reference', null=True, blank=True, on_delete=models.SET_NULL, related_name='subject_observations')

    # What the observation is about, when it is not about the subject of record (0..* Reference)
    focus = models.ManyToManyField('components.Reference', blank=True, related_name='focus_observations')

    # Healthcare event during which this observation is made (0..1 Reference(Encounter))
    encounter = models.ForeignKey('encounter.Encounter', null=True, blank=True, on_delete=models.SET_NULL, related_name='observations')

    # effective[x] - Clinically relevant time/time-period (0..1 choice)
    effectiveDateTime = models.DateTimeField(null=True, blank=True)
    effectiveInstant = models.DateTimeField(null=True, blank=True)
    effectivePeriod = models.ForeignKey('components.Period', null=True, blank=True, on_delete=models.SET_NULL, related_name='effective_observations')

    # Date/Time this version was made available (0..1 instant)
    issued = models.DateTimeField(null=True, blank=True)

    # Who is responsible for the observation (0..* Reference)
    performer = models.ManyToManyField('components.Reference', blank=True, related_name='performed_observations')

    # value[x] - Actual result (0..1 choice)
    valueQuantity = models.ForeignKey('components.Quantity', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_values')
    valueCodeableConcept = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_value_cc')
    valueString = models.CharField(max_length=1024, null=True, blank=True)
    valueBoolean = models.BooleanField(null=True, blank=True)
    valueInteger = models.IntegerField(null=True, blank=True)
    valueRange = models.ForeignKey('components.Range', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_value_ranges')
    valuePeriod = models.ForeignKey('components.Period', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_value_periods')
    valueDateTime = models.DateTimeField(null=True, blank=True)
    valueTime = models.TimeField(null=True, blank=True)

    # Why the result is missing (0..1 CodeableConcept)
    dataAbsentReason = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_data_absent_reasons')

    # High, low, normal, etc. (0..* CodeableConcept)
    interpretation = models.ManyToManyField('components.CodeableConcept', blank=True, related_name='observation_interpretations')

    # Comments about the observation (0..* Annotation stored as JSON)
    note = models.JSONField(null=True, blank=True)

    # Observed body part (0..1 CodeableConcept)
    bodySite = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_body_sites')

    # How it was done (0..1 CodeableConcept)
    method = models.ForeignKey('components.CodeableConcept', null=True, blank=True, on_delete=models.SET_NULL, related_name='observation_methods')

    # Specimen used for this observation (0..1 Reference)
    specimen = models.ForeignKey('components.Reference', null=True, blank=True, on_delete=models.SET_NULL, related_name='specimen_observations')

    # A reference to the device that generates the measurements (0..1 Reference)
    device = models.ForeignKey('components.Reference', null=True, blank=True, on_delete=models.SET_NULL, related_name='device_observations')

    # Related resource that belongs to the Observation group (0..* Reference(Observation))
    hasMember = models.ManyToManyField('self', blank=True, related_name='member_of', symmetrical=False)

    # Related measurements the observation is made from (0..* Reference)
    derivedFrom = models.ManyToManyField('components.Reference', blank=True, related_name='derived_observations')

    # Fulfills plan, proposal or order (0..* Reference)
    basedOn = models.ManyToManyField('components.Reference', blank=True, related_name='based_on_observations')

    # Part of referenced event (0..* Reference)
    partOf = models.ManyToManyField('components.Reference', blank=True, related_name='part_of_observations')

    class Meta:
        db_table = 'observation'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['effectiveDateTime']),
            models.Index(fields=['issued']),
        ]

    def clean(self):
        super().clean()
        # FHIR invariant: only one effective[x] can be set
        effective_fields = ['effectiveDateTime', 'effectiveInstant', 'effectivePeriod']
        set_effectives = [f for f in effective_fields if getattr(self, f) is not None]
        if len(set_effectives) > 1:
            raise ValidationError("Only one effective[x] field can be set")

        # FHIR invariant: only one value[x] can be set
        value_fields = [
            'valueQuantity', 'valueCodeableConcept', 'valueString', 'valueBoolean',
            'valueInteger', 'valueRange', 'valuePeriod', 'valueDateTime', 'valueTime'
        ]
        set_values = [f for f in value_fields if getattr(self, f) is not None]
        if len(set_values) > 1:
            raise ValidationError("Only one value[x] field can be set")

        # FHIR rule: dataAbsentReason only when value is absent
        if self.pk and set_values and self.dataAbsentReason:
            raise ValidationError("dataAbsentReason shall only be present if there is no value[x]")

    def __str__(self):
        return f"Observation(status={self.status}, code={self.code})"


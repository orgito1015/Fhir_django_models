from fhir.resources import observation as obs_module
from components.serializers import convert_codeable_concept, convert_period, convert_quantity
from . import models


def convert_observation_reference_range(django_rr):
    """Convert Django ObservationReferenceRange to FHIR Observation.referenceRange"""
    if not django_rr:
        return None

    data = {}
    if django_rr.low:
        data['low'] = convert_quantity(django_rr.low)
    if django_rr.high:
        data['high'] = convert_quantity(django_rr.high)
    if django_rr.type:
        data['type'] = convert_codeable_concept(django_rr.type)
    if django_rr.normalValue:
        data['normalValue'] = convert_codeable_concept(django_rr.normalValue)
    if django_rr.text:
        data['text'] = django_rr.text
    return data


def convert_observation_component(django_component):
    """Convert Django ObservationComponent to FHIR Observation.component"""
    if not django_component:
        return None

    data = {
        'code': convert_codeable_concept(django_component.code)
    }

    if django_component.valueQuantity:
        data['valueQuantity'] = convert_quantity(django_component.valueQuantity)
    elif django_component.valueCodeableConcept:
        data['valueCodeableConcept'] = convert_codeable_concept(django_component.valueCodeableConcept)
    elif django_component.valueString:
        data['valueString'] = django_component.valueString
    elif django_component.valueBoolean is not None:
        data['valueBoolean'] = django_component.valueBoolean
    elif django_component.valueInteger is not None:
        data['valueInteger'] = django_component.valueInteger
    elif django_component.valuePeriod:
        data['valuePeriod'] = convert_period(django_component.valuePeriod)
    elif django_component.valueDateTime:
        data['valueDateTime'] = django_component.valueDateTime.isoformat()
    elif django_component.valueTime:
        data['valueTime'] = django_component.valueTime.isoformat()

    if django_component.dataAbsentReason:
        data['dataAbsentReason'] = convert_codeable_concept(django_component.dataAbsentReason)

    interpretations = []
    for interp in django_component.interpretation.all():
        fhir_interp = convert_codeable_concept(interp)
        if fhir_interp:
            interpretations.append(fhir_interp)
    if interpretations:
        data['interpretation'] = interpretations

    reference_ranges = []
    for rr in django_component.reference_ranges.all():
        fhir_rr = convert_observation_reference_range(rr)
        if fhir_rr:
            reference_ranges.append(fhir_rr)
    if reference_ranges:
        data['referenceRange'] = reference_ranges

    return data


def convert_observation(django_obs):
    """Convert Django Observation to FHIR Observation"""
    if not django_obs:
        return None

    data = {
        'resourceType': 'Observation',
        'status': django_obs.status,
        'code': convert_codeable_concept(django_obs.code),
    }
    if django_obs.fhir_id:
        data['id'] = django_obs.fhir_id

    # Categories
    categories = []
    for cat in django_obs.category.all():
        fhir_cat = convert_codeable_concept(cat)
        if fhir_cat:
            categories.append(fhir_cat)
    if categories:
        data['category'] = categories

    # Subject
    if django_obs.subject:
        data['subject'] = {'reference': django_obs.subject.reference}

    # Encounter
    if django_obs.encounter:
        data['encounter'] = {'reference': f'Encounter/{django_obs.encounter.fhir_id}'}

    # effective[x]
    if django_obs.effectiveDateTime:
        data['effectiveDateTime'] = django_obs.effectiveDateTime.isoformat()
    elif django_obs.effectiveInstant:
        data['effectiveInstant'] = django_obs.effectiveInstant.isoformat()
    elif django_obs.effectivePeriod:
        data['effectivePeriod'] = convert_period(django_obs.effectivePeriod)

    if django_obs.issued:
        data['issued'] = django_obs.issued.isoformat()

    # value[x]
    if django_obs.valueQuantity:
        data['valueQuantity'] = convert_quantity(django_obs.valueQuantity)
    elif django_obs.valueCodeableConcept:
        data['valueCodeableConcept'] = convert_codeable_concept(django_obs.valueCodeableConcept)
    elif django_obs.valueString:
        data['valueString'] = django_obs.valueString
    elif django_obs.valueBoolean is not None:
        data['valueBoolean'] = django_obs.valueBoolean
    elif django_obs.valueInteger is not None:
        data['valueInteger'] = django_obs.valueInteger
    elif django_obs.valuePeriod:
        data['valuePeriod'] = convert_period(django_obs.valuePeriod)
    elif django_obs.valueDateTime:
        data['valueDateTime'] = django_obs.valueDateTime.isoformat()
    elif django_obs.valueTime:
        data['valueTime'] = django_obs.valueTime.isoformat()

    if django_obs.dataAbsentReason:
        data['dataAbsentReason'] = convert_codeable_concept(django_obs.dataAbsentReason)

    # Interpretations
    interpretations = []
    for interp in django_obs.interpretation.all():
        fhir_interp = convert_codeable_concept(interp)
        if fhir_interp:
            interpretations.append(fhir_interp)
    if interpretations:
        data['interpretation'] = interpretations

    if django_obs.note:
        data['note'] = django_obs.note

    if django_obs.bodySite:
        data['bodySite'] = convert_codeable_concept(django_obs.bodySite)

    if django_obs.method:
        data['method'] = convert_codeable_concept(django_obs.method)

    # Reference ranges
    reference_ranges = []
    for rr in django_obs.reference_ranges.all():
        fhir_rr = convert_observation_reference_range(rr)
        if fhir_rr:
            reference_ranges.append(fhir_rr)
    if reference_ranges:
        data['referenceRange'] = reference_ranges

    # Components
    obs_components = []
    for comp in django_obs.components.all():
        fhir_comp = convert_observation_component(comp)
        if fhir_comp:
            obs_components.append(fhir_comp)
    if obs_components:
        data['component'] = obs_components

    return obs_module.Observation(**data)

from fhir.resources import encounter as enc_module
from components.serializers import convert_codeable_concept, convert_period
from . import models


def convert_encounter_participant(django_participant):
    """Convert Django EncounterParticipant to FHIR Encounter.participant"""
    if not django_participant:
        return None

    data = {}
    types = []
    for t in django_participant.type.all():
        fhir_t = convert_codeable_concept(t)
        if fhir_t:
            types.append(fhir_t)
    if types:
        data['type'] = types

    if django_participant.period:
        data['period'] = convert_period(django_participant.period)

    if django_participant.actor:
        data['actor'] = {'reference': django_participant.actor.reference}

    return data


def convert_encounter_diagnosis(django_diagnosis):
    """Convert Django EncounterDiagnosis to FHIR Encounter.diagnosis"""
    if not django_diagnosis:
        return None

    data = {
        'condition': [{'reference': django_diagnosis.condition.reference}]
    }

    uses = []
    for u in django_diagnosis.use.all():
        fhir_u = convert_codeable_concept(u)
        if fhir_u:
            uses.append(fhir_u)
    if uses:
        data['use'] = uses

    return data


def convert_encounter_admission(django_admission):
    """Convert Django EncounterAdmission to FHIR Encounter.admission"""
    if not django_admission:
        return None

    data = {}
    if django_admission.admitSource:
        data['admitSource'] = convert_codeable_concept(django_admission.admitSource)
    if django_admission.reAdmission:
        data['reAdmission'] = convert_codeable_concept(django_admission.reAdmission)
    if django_admission.dischargeDisposition:
        data['dischargeDisposition'] = convert_codeable_concept(django_admission.dischargeDisposition)
    if django_admission.origin:
        data['origin'] = {'reference': django_admission.origin.reference}
    if django_admission.destination:
        data['destination'] = {'reference': django_admission.destination.reference}

    return data


def convert_encounter_location(django_loc):
    """Convert Django EncounterLocation to FHIR Encounter.location"""
    if not django_loc:
        return None

    data = {
        'location': {'reference': django_loc.location.reference}
    }
    if django_loc.status:
        data['status'] = django_loc.status
    if django_loc.form:
        data['form'] = convert_codeable_concept(django_loc.form)
    if django_loc.period:
        data['period'] = convert_period(django_loc.period)

    return data


def convert_encounter(django_encounter):
    """Convert Django Encounter to FHIR Encounter"""
    if not django_encounter:
        return None

    data = {
        'resourceType': 'Encounter',
        'status': django_encounter.status,
        'class': [convert_codeable_concept(django_encounter.class_field)],
    }
    if django_encounter.fhir_id:
        data['id'] = django_encounter.fhir_id

    if django_encounter.priority:
        data['priority'] = convert_codeable_concept(django_encounter.priority)

    if django_encounter.subject:
        data['subject'] = {'reference': django_encounter.subject.reference}

    if django_encounter.actualPeriod:
        data['actualPeriod'] = convert_period(django_encounter.actualPeriod)

    if django_encounter.plannedStartDate:
        data['plannedStartDate'] = django_encounter.plannedStartDate.isoformat()

    if django_encounter.plannedEndDate:
        data['plannedEndDate'] = django_encounter.plannedEndDate.isoformat()

    # Type
    types = []
    for t in django_encounter.type.all():
        fhir_t = convert_codeable_concept(t)
        if fhir_t:
            types.append(fhir_t)
    if types:
        data['type'] = types

    # Participants
    participants = []
    for participant in django_encounter.participants.all():
        fhir_p = convert_encounter_participant(participant)
        if fhir_p:
            participants.append(fhir_p)
    if participants:
        data['participant'] = participants

    # Diagnoses
    diagnoses = []
    for diagnosis in django_encounter.diagnoses.all():
        fhir_d = convert_encounter_diagnosis(diagnosis)
        if fhir_d:
            diagnoses.append(fhir_d)
    if diagnoses:
        data['diagnosis'] = diagnoses

    # Admission
    try:
        if django_encounter.admission:
            admission_data = convert_encounter_admission(django_encounter.admission)
            if admission_data:
                data['admission'] = admission_data
    except models.EncounterAdmission.DoesNotExist:
        pass

    # Locations
    locations = []
    for loc in django_encounter.locations.all():
        fhir_loc = convert_encounter_location(loc)
        if fhir_loc:
            locations.append(fhir_loc)
    if locations:
        data['location'] = locations

    return enc_module.Encounter(**data)

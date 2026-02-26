from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Patient, RelatedPerson
from .serializers import convert_patient, convert_related_person


class PatientListView(APIView):
    """FHIR Patient list and create endpoint"""

    def get(self, request):
        patients = Patient.objects.all()
        data = [convert_patient(p).model_dump() for p in patients]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class PatientDetailView(APIView):
    """FHIR Patient read endpoint"""

    def get(self, request, fhir_id):
        patient = get_object_or_404(Patient, fhir_id=fhir_id)
        return Response(convert_patient(patient).model_dump())


class RelatedPersonListView(APIView):
    """FHIR RelatedPerson list endpoint"""

    def get(self, request):
        persons = RelatedPerson.objects.all()
        data = [convert_related_person(p).model_dump() for p in persons]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class RelatedPersonDetailView(APIView):
    """FHIR RelatedPerson read endpoint"""

    def get(self, request, fhir_id):
        person = get_object_or_404(RelatedPerson, fhir_id=fhir_id)
        return Response(convert_related_person(person).model_dump())


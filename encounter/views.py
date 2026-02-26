from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Encounter
from .serializers import convert_encounter


class EncounterListView(APIView):
    """FHIR Encounter list endpoint"""

    def get(self, request):
        encounters = Encounter.objects.all()
        data = [convert_encounter(e).model_dump() for e in encounters]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class EncounterDetailView(APIView):
    """FHIR Encounter read endpoint"""

    def get(self, request, fhir_id):
        encounter = get_object_or_404(Encounter, fhir_id=fhir_id)
        return Response(convert_encounter(encounter).model_dump())


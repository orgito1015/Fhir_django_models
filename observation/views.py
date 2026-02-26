from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Observation
from .serializers import convert_observation


class ObservationListView(APIView):
    """FHIR Observation list endpoint"""

    def get(self, request):
        observations = Observation.objects.all()
        data = [convert_observation(o).model_dump() for o in observations]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class ObservationDetailView(APIView):
    """FHIR Observation read endpoint"""

    def get(self, request, fhir_id):
        obs = get_object_or_404(Observation, fhir_id=fhir_id)
        return Response(convert_observation(obs).model_dump())


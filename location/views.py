from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Location
from .serializers import convert_location


class LocationListView(APIView):
    """FHIR Location list endpoint"""

    def get(self, request):
        locations = Location.objects.all()
        data = [convert_location(loc).model_dump() for loc in locations]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class LocationDetailView(APIView):
    """FHIR Location read endpoint"""

    def get(self, request, fhir_id):
        location = get_object_or_404(Location, fhir_id=fhir_id)
        return Response(convert_location(location).model_dump())


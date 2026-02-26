from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Endpoint
from .serializers import convert_endpoint


class EndpointListView(APIView):
    """FHIR Endpoint list endpoint"""

    def get(self, request):
        endpoints = Endpoint.objects.all()
        data = [convert_endpoint(e).model_dump() for e in endpoints]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class EndpointDetailView(APIView):
    """FHIR Endpoint read endpoint"""

    def get(self, request, fhir_id):
        endpoint = get_object_or_404(Endpoint, fhir_id=fhir_id)
        return Response(convert_endpoint(endpoint).model_dump())


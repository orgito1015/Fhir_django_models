from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import HealthcareService
from .serializers import convert_healthcare_service


class HealthcareServiceListView(APIView):
    """FHIR HealthcareService list endpoint"""

    def get(self, request):
        services = HealthcareService.objects.all()
        data = [convert_healthcare_service(s).model_dump() for s in services]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class HealthcareServiceDetailView(APIView):
    """FHIR HealthcareService read endpoint"""

    def get(self, request, fhir_id):
        service = get_object_or_404(HealthcareService, fhir_id=fhir_id)
        return Response(convert_healthcare_service(service).model_dump())


from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Organization
from .serializers import convert_organization


class OrganizationListView(APIView):
    """FHIR Organization list endpoint"""

    def get(self, request):
        orgs = Organization.objects.all()
        data = [convert_organization(o).model_dump() for o in orgs]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class OrganizationDetailView(APIView):
    """FHIR Organization read endpoint"""

    def get(self, request, fhir_id):
        org = get_object_or_404(Organization, fhir_id=fhir_id)
        return Response(convert_organization(org).model_dump())


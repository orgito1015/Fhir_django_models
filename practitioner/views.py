from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Practitioner, PractitionerRole
from .serializers import convert_practitioner, convert_practitioner_role


class PractitionerListView(APIView):
    """FHIR Practitioner list endpoint"""

    def get(self, request):
        practitioners = Practitioner.objects.all()
        data = [convert_practitioner(p).model_dump() for p in practitioners]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class PractitionerDetailView(APIView):
    """FHIR Practitioner read endpoint"""

    def get(self, request, fhir_id):
        practitioner = get_object_or_404(Practitioner, fhir_id=fhir_id)
        return Response(convert_practitioner(practitioner).model_dump())


class PractitionerRoleListView(APIView):
    """FHIR PractitionerRole list endpoint"""

    def get(self, request):
        roles = PractitionerRole.objects.all()
        data = [convert_practitioner_role(r).model_dump() for r in roles]
        return Response({'resourceType': 'Bundle', 'type': 'searchset', 'entry': data})


class PractitionerRoleDetailView(APIView):
    """FHIR PractitionerRole read endpoint"""

    def get(self, request, fhir_id):
        role = get_object_or_404(PractitionerRole, fhir_id=fhir_id)
        return Response(convert_practitioner_role(role).model_dump())


from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Endpoint, EndpointPayload
from organization.models import Organization


class EndpointModelTest(TestCase):
    """Tests for FHIR R5 Endpoint model"""

    def test_create_minimal_endpoint(self):
        """Can create a minimal Endpoint with required fields"""
        ep = Endpoint.objects.create(
            status='active',
            address='https://example.com/fhir',
        )
        self.assertEqual(ep.status, 'active')
        self.assertEqual(ep.address, 'https://example.com/fhir')

    def test_endpoint_status_choices(self):
        """Endpoint status must be a valid FHIR code"""
        valid_statuses = ['active', 'suspended', 'error', 'off', 'entered-in-error', 'test']
        for s in valid_statuses:
            ep = Endpoint.objects.create(status=s, address='https://example.com/fhir')
            self.assertEqual(ep.status, s)

    def test_endpoint_str(self):
        """Endpoint __str__ returns useful representation"""
        ep = Endpoint.objects.create(
            status='active',
            address='https://example.com/fhir',
            name='FHIR Endpoint',
        )
        self.assertIn('FHIR Endpoint', str(ep))

    def test_endpoint_organization_relationship(self):
        """Endpoint can belong to an Organization"""
        org = Organization.objects.create(name='Test Hospital')
        ep = Endpoint.objects.create(
            status='active',
            address='https://example.com/fhir',
            organization=org,
        )
        self.assertEqual(ep.organization, org)
        self.assertEqual(org.endpoints.count(), 1)

    def test_endpoint_payload_creation(self):
        """Can create an EndpointPayload"""
        ep = Endpoint.objects.create(
            status='active',
            address='https://example.com/fhir',
        )
        payload = EndpointPayload.objects.create(
            endpoint=ep,
            mimeType=['application/fhir+json'],
        )
        self.assertEqual(ep.payloads.count(), 1)
        self.assertIn('application/fhir+json', payload.mimeType)


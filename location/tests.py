from django.test import TestCase
from .models import Location, LocationPosition
from components.models import Address
from organization.models import Organization
from endpoint.models import Endpoint


class LocationModelTest(TestCase):
    """Tests for FHIR R5 Location model"""

    def test_create_minimal_location(self):
        """Can create a minimal Location"""
        loc = Location.objects.create()
        self.assertIsNotNone(loc.pk)

    def test_location_with_name(self):
        """Can create a Location with a name"""
        loc = Location.objects.create(name='Main Clinic', status='active')
        self.assertEqual(loc.name, 'Main Clinic')
        self.assertEqual(loc.status, 'active')

    def test_location_status_choices(self):
        """Location status must be a valid code"""
        for status in ['active', 'suspended', 'inactive']:
            loc = Location.objects.create(status=status)
            self.assertEqual(loc.status, status)

    def test_location_mode_choices(self):
        """Location mode must be a valid code"""
        for mode in ['instance', 'kind']:
            loc = Location.objects.create(mode=mode)
            self.assertEqual(loc.mode, mode)

    def test_location_str(self):
        """Location __str__ returns useful representation"""
        loc = Location.objects.create(name='ICU', status='active')
        self.assertIn('ICU', str(loc))
        self.assertIn('active', str(loc))

    def test_location_part_of(self):
        """Location can have a parent location"""
        parent = Location.objects.create(name='Main Building')
        child = Location.objects.create(name='Room 101', partOf=parent)
        self.assertEqual(child.partOf, parent)
        self.assertEqual(parent.child_locations.count(), 1)

    def test_location_position_creation(self):
        """Can create a LocationPosition"""
        loc = Location.objects.create(name='Test Location')
        pos = LocationPosition.objects.create(
            location=loc,
            longitude=-122.084,
            latitude=37.422,
        )
        self.assertEqual(loc.position, pos)
        self.assertAlmostEqual(float(pos.longitude), -122.084, places=2)

    def test_location_managing_organization(self):
        """Location can have a managing organization"""
        org = Organization.objects.create(name='Test Hospital')
        loc = Location.objects.create(name='Ward A', managingOrganization=org)
        self.assertEqual(loc.managingOrganization, org)
        self.assertEqual(org.managed_locations.count(), 1)

    def test_location_alias_json_field(self):
        """Location alias is stored as JSON array"""
        loc = Location.objects.create(
            name='Test Location',
            alias=['Alias1', 'Alias2'],
        )
        self.assertEqual(len(loc.alias), 2)


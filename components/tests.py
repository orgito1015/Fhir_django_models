from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import (
    Identifier, CodeableConcept, Coding, ContactPoint, ContactDetail,
    Period, Quantity, Range, HumanName, Address, Narrative
)
from .reference import Reference


class IdentifierModelTest(TestCase):
    """Tests for FHIR Identifier model"""

    def test_create_identifier(self):
        """Can create an Identifier"""
        ident = Identifier.objects.create(
            use='official',
            system='http://example.com/ids',
            value='12345',
        )
        self.assertEqual(ident.use, 'official')
        self.assertEqual(ident.value, '12345')

    def test_identifier_use_choices(self):
        """Identifier use must be a valid FHIR code"""
        for use in ['usual', 'official', 'temp', 'secondary', 'old']:
            ident = Identifier.objects.create(use=use)
            self.assertEqual(ident.use, use)


class CodeableConceptModelTest(TestCase):
    """Tests for FHIR CodeableConcept model"""

    def test_create_codeable_concept(self):
        """Can create a CodeableConcept"""
        cc = CodeableConcept.objects.create(text='Blood pressure')
        self.assertEqual(cc.text, 'Blood pressure')

    def test_codeable_concept_with_coding(self):
        """CodeableConcept can have multiple Codings"""
        cc = CodeableConcept.objects.create(text='BP')
        Coding.objects.create(
            codeable_concept=cc,
            system='http://loinc.org',
            code='55284-4',
            display='Blood pressure systolic and diastolic',
        )
        self.assertEqual(cc.codings.count(), 1)


class ContactPointModelTest(TestCase):
    """Tests for FHIR ContactPoint model"""

    def test_create_contact_point(self):
        """Can create a ContactPoint"""
        cp = ContactPoint.objects.create(
            system='phone',
            value='+1-555-0100',
            use='work',
        )
        self.assertEqual(cp.system, 'phone')
        self.assertEqual(cp.value, '+1-555-0100')

    def test_contact_point_requires_system_when_value_present(self):
        """ContactPoint.system is required when value is provided"""
        cp = ContactPoint(value='+1-555-0100')
        with self.assertRaises(ValidationError):
            cp.clean()

    def test_contact_point_system_choices(self):
        """ContactPoint system must be a valid code"""
        for system in ['phone', 'fax', 'email', 'pager', 'url', 'sms', 'other']:
            cp = ContactPoint.objects.create(system=system)
            self.assertEqual(cp.system, system)


class PeriodModelTest(TestCase):
    """Tests for FHIR Period model"""

    def test_create_period(self):
        """Can create a Period"""
        import datetime
        start = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(2024, 12, 31, tzinfo=datetime.timezone.utc)
        period = Period.objects.create(start=start, end=end)
        self.assertEqual(period.start, start)
        self.assertEqual(period.end, end)


class QuantityModelTest(TestCase):
    """Tests for FHIR Quantity model"""

    def test_create_quantity(self):
        """Can create a Quantity"""
        qty = Quantity.objects.create(value=120, unit='mmHg', system='http://unitsofmeasure.org', code='mm[Hg]')
        self.assertEqual(qty.value, 120)
        self.assertEqual(qty.unit, 'mmHg')


class HumanNameModelTest(TestCase):
    """Tests for FHIR HumanName model"""

    def test_create_human_name(self):
        """Can create a HumanName"""
        name = HumanName.objects.create(
            use='official',
            family='Smith',
            given=['John'],
        )
        self.assertEqual(name.family, 'Smith')
        self.assertEqual(name.given, ['John'])

    def test_human_name_use_choices(self):
        """HumanName use must be a valid FHIR code"""
        for use in ['usual', 'official', 'temp', 'nickname', 'anonymous', 'old', 'maiden']:
            name = HumanName.objects.create(use=use)
            self.assertEqual(name.use, use)


class AddressModelTest(TestCase):
    """Tests for FHIR Address model"""

    def test_create_address(self):
        """Can create an Address"""
        addr = Address.objects.create(
            use='home',
            type='postal',
            city='Springfield',
            state='IL',
            postalCode='62701',
            country='US',
        )
        self.assertEqual(addr.city, 'Springfield')
        self.assertEqual(addr.country, 'US')


class ReferenceModelTest(TestCase):
    """Tests for FHIR Reference model"""

    def test_create_reference(self):
        """Can create a Reference"""
        ref = Reference.objects.create(reference='Patient/pt-123', display='John Smith')
        self.assertEqual(ref.reference, 'Patient/pt-123')
        self.assertEqual(ref.display, 'John Smith')


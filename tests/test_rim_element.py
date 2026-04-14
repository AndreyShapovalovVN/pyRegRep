"""
Unit tests for RIMElement module.

Tests cover:
- get_slot() function for creating slot objects
- AnyValueType serialization and deserialization
- All slot types creation and element generation
"""

import datetime
import pytest
from lxml import etree
from pyRegRep4.RIMElement import (
    get_slot,
    _StringValueType,
    _BooleanValueType,
    _TimeStamp,
    _CollectionValueType,
    _AnyValueType,
    _InternationalStringValueType,
    RegistryObject,
    RepositoryItemRef,
    QueryResponse,
    Classification,
)


class TestGetSlotFunction:
    """Test the get_slot() factory function."""

    def test_get_slot_string_value_type(self):
        """Test creating a StringValueType slot."""
        slot = get_slot("TestSlot", "StringValueType", "test value")
        assert slot is not None
        assert isinstance(slot, _StringValueType)
        assert slot.name == "TestSlot"
        assert slot.value == "test value"

    def test_get_slot_boolean_value_type(self):
        """Test creating a BooleanValueType slot."""
        slot = get_slot("BoolSlot", "BooleanValueType", True)
        assert slot is not None
        assert isinstance(slot, _BooleanValueType)
        assert slot.name == "BoolSlot"
        assert slot.value is True

    def test_get_slot_datetime_value_type(self):
        """Test creating a DateTimeValueType slot."""
        now = datetime.datetime.now()
        slot = get_slot("TimeSlot", "DateTimeValueType", now)
        assert slot is not None
        assert isinstance(slot, _TimeStamp)
        assert slot.name == "TimeSlot"
        assert slot.value == now

    def test_get_slot_any_value_type(self):
        """Test creating an AnyValueType slot."""
        elem = etree.Element("TestElement")
        elem.text = "test content"
        slot = get_slot("AnySlot", "AnyValueType", elem)
        assert slot is not None
        assert isinstance(slot, _AnyValueType)
        assert slot.name == "AnySlot"
        assert slot.value == elem

    def test_get_slot_international_string_value_type(self):
        """Test creating an InternationalStringValueType slot."""
        elem = etree.Element("LocalString")
        slot = get_slot("IntlSlot", "InternationalStringValueType", elem)
        assert slot is not None
        assert isinstance(slot, _InternationalStringValueType)
        assert slot.name == "IntlSlot"

    def test_get_slot_collection_value_type(self):
        """Test creating a CollectionValueType slot."""
        elem = etree.Element("Item")
        slot = get_slot("CollSlot", "CollectionValueType", elem)
        assert slot is not None
        assert isinstance(slot, _CollectionValueType)
        assert slot.name == "CollSlot"

    def test_get_slot_invalid_type(self):
        """Test that invalid slot type raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_slot("InvalidSlot", "InvalidValueType", "value")
        assert "Невідомий тип слота" in str(excinfo.value)
        assert "InvalidValueType" in str(excinfo.value)

    def test_get_slot_supported_types_listed(self):
        """Test that error message lists supported types."""
        with pytest.raises(ValueError) as excinfo:
            get_slot("Test", "Unknown", "val")
        error_msg = str(excinfo.value)
        assert "StringValueType" in error_msg
        assert "BooleanValueType" in error_msg
        assert "DateTimeValueType" in error_msg
        assert "AnyValueType" in error_msg


class TestAnyValueTypeSlot:
    """Test AnyValueType slot creation and XML element generation."""

    def test_any_value_type_with_simple_element(self):
        """Test AnyValueType with a simple XML element."""
        elem = etree.Element("CustomElement")
        elem.text = "custom content"

        slot = _AnyValueType(elem)
        slot.name = "CustomData"

        assert slot.element is not None
        assert slot.value == elem
        # Check that the slot element is created properly
        slot_elem = slot.element
        assert slot_elem.tag.endswith("Slot")
        assert slot_elem.attrib.get("name") == "CustomData"

    def test_any_value_type_with_complex_element(self):
        """Test AnyValueType with a complex nested XML element."""
        root = etree.Element("Root")
        child1 = etree.SubElement(root, "Child1")
        child1.text = "value1"
        child2 = etree.SubElement(root, "Child2")
        child2.text = "value2"

        slot = _AnyValueType(root)
        slot.name = "ComplexData"

        assert slot.element is not None
        # Verify the slot structure
        slot_elem = slot.element
        assert slot_elem.attrib.get("name") == "ComplexData"
        # Check SlotValue element
        slot_value = slot_elem.find(".//{*}SlotValue")
        assert slot_value is not None

    def test_any_value_type_serialization(self):
        """Test serialization of AnyValueType to XML bytes."""
        elem = etree.Element("TestData")
        elem.text = "test"
        elem.attrib["attr"] = "value"

        slot = _AnyValueType(elem)
        slot.name = "DataSlot"

        # Get serialized bytes
        xml_bytes = slot.text
        assert isinstance(xml_bytes, bytes)
        # Parse back to verify structure
        parsed = etree.fromstring(xml_bytes)
        assert parsed.attrib.get("name") == "DataSlot"

    def test_any_value_type_preserves_original_element(self):
        """Test that AnyValueType preserves the original element content."""
        original = etree.Element("Original")
        original.text = "original content"
        original.attrib["id"] = "123"

        slot = _AnyValueType(original)
        slot.name = "PreserveTest"

        # The value should be the original element
        assert slot.value is original
        assert slot.value.text == "original content"
        assert slot.value.attrib.get("id") == "123"


class TestStringValueType:
    """Test StringValueType slot creation."""

    def test_string_value_type_basic(self):
        """Test basic StringValueType creation."""
        slot = _StringValueType("hello world")
        slot.name = "StringSlot"

        assert slot.value == "hello world"
        assert slot.element is not None
        assert slot.element.attrib.get("name") == "StringSlot"

    def test_string_value_type_empty(self):
        """Test StringValueType with empty string."""
        slot = _StringValueType("")
        slot.name = "EmptySlot"

        assert slot.value == ""
        assert slot.element is not None

    def test_string_value_type_special_chars(self):
        """Test StringValueType with special characters."""
        special_text = "Special <>&\"' chars"
        slot = _StringValueType(special_text)
        slot.name = "SpecialSlot"

        assert slot.value == special_text


class TestBooleanValueType:
    """Test BooleanValueType slot creation."""

    def test_boolean_value_type_true(self):
        """Test BooleanValueType with True value."""
        slot = _BooleanValueType(True)
        slot.name = "BoolSlot"

        assert slot.value is True
        # XML should contain lowercase 'true'
        xml_text = slot.text.decode()
        assert "true" in xml_text.lower()

    def test_boolean_value_type_false(self):
        """Test BooleanValueType with False value."""
        slot = _BooleanValueType(False)
        slot.name = "BoolSlot"

        assert slot.value is False
        # XML should contain lowercase 'false'
        xml_text = slot.text.decode()
        assert "false" in xml_text.lower()


class TestDateTimeValueType:
    """Test DateTimeValueType (TimeStamp) slot creation."""

    def test_datetime_value_type_with_datetime(self):
        """Test DateTimeValueType with datetime object."""
        dt = datetime.datetime(2024, 3, 15, 10, 30, 45)
        slot = _TimeStamp(dt)
        slot.name = "TimeSlot"

        assert slot.value == dt
        assert slot.element is not None
        # Should contain ISO format datetime
        xml_text = slot.text.decode()
        assert "2024-03-15" in xml_text

    def test_datetime_value_type_with_string(self):
        """Test DateTimeValueType with ISO string."""
        iso_string = "2024-03-15T10:30:45"
        slot = _TimeStamp(iso_string)
        slot.name = "TimeSlot"

        assert slot.value == iso_string
        assert iso_string in slot.text.decode()


class TestCollectionValueType:
    """Test CollectionValueType slot creation."""

    def test_collection_value_type_with_element(self):
        """Test CollectionValueType with XML element."""
        elem = etree.Element("Item")
        elem.text = "item value"

        slot = _CollectionValueType(elem)
        slot.name = "CollSlot"

        assert slot.value == elem
        assert slot.element is not None
        xml_text = slot.text.decode()
        assert "CollectionValueType" in xml_text

    def test_collection_value_type_structure(self):
        """Test CollectionValueType has correct structure."""
        elem = etree.Element("Item")
        slot = _CollectionValueType(elem)
        slot.name = "Collection"

        slot_elem = slot.element
        slot_value = [child for child in slot_elem if "SlotValue" in child.tag][0]
        # Should have correct xsi:type
        assert "CollectionValueType" in str(slot_value.attrib)
        # Should have collectionType attribute
        assert "collectionType" in slot_value.attrib


class TestInternationalStringValueType:
    """Test InternationalStringValueType slot creation."""

    def test_single_element(self):
        """Single etree._Element is appended into Value."""
        elem = etree.Element("LocalizedString")
        elem.text = "English text"
        elem.attrib["lang"] = "en"

        slot = _InternationalStringValueType(elem)
        slot.name = "IntlSlot"

        assert slot.element is not None
        assert slot.value is elem

        # Value element should contain the child
        slot_value = slot.element.find(".//{*}SlotValue")
        assert slot_value is not None
        value_el = slot_value.find(".//{*}Value")
        assert value_el is not None
        assert len(value_el) == 1

    def test_list_of_elements(self):
        """List of etree._Element objects: each one appended into Value."""
        elems = []
        for lang, text in [("en", "English"), ("uk", "Українська"), ("de", "Deutsch")]:
            e = etree.Element("LocalizedString")
            e.attrib["lang"] = lang
            e.text = text
            elems.append(e)

        slot = _InternationalStringValueType(elems)
        slot.name = "IntlMultiSlot"

        assert slot.element is not None
        value_el = slot.element.find(".//{*}SlotValue/{*}Value")
        assert value_el is not None
        assert len(value_el) == 3

    def test_list_of_dicts(self):
        """List of dicts with 'lang'/'text' keys creates LocalizedString elements."""
        XML_NS = "http://www.w3.org/XML/1998/namespace"
        data = [
            {"lang": "en", "text": "Hello"},
            {"lang": "uk", "text": "Привіт"},
        ]

        slot = _InternationalStringValueType(data)
        slot.name = "DictSlot"

        value_el = slot.element.find(".//{*}SlotValue/{*}Value")
        assert value_el is not None
        assert len(value_el) == 2
        # lang is stored as {http://www.w3.org/XML/1998/namespace}lang attribute
        langs = {child.attrib.get(f"{{{XML_NS}}}lang") for child in value_el}
        assert langs == {"en", "uk"}
        # text is stored in "value" attribute (not .text)
        texts = {child.attrib.get("value") for child in value_el}
        assert "Hello" in texts
        assert "Привіт" in texts

    def test_list_of_dicts_invalid_items_skipped(self, caplog):
        """Dict items missing 'lang' or 'text' are skipped with a warning."""
        import logging
        data = [
            {"lang": "en", "text": "Good"},
            {"foo": "bar"},            # invalid – missing keys
            {"lang": "de"},            # invalid – missing text
        ]

        with caplog.at_level(logging.WARNING, logger="pyRegRep4.RIMElement"):
            slot = _InternationalStringValueType(data)
            slot.name = "PartialSlot"

        value_el = slot.element.find(".//{*}SlotValue/{*}Value")
        # Only the first valid dict should produce a child element
        assert len(value_el) == 1
        # Two distinct invalid items → at least 2 warnings (may double due to name setter)
        unique_messages = {r.message for r in caplog.records}
        assert len(unique_messages) == 2

    def test_list_mixed_elements_and_dicts(self):
        """List may contain both etree._Element and dict items."""
        XML_NS = "http://www.w3.org/XML/1998/namespace"
        e = etree.Element("LocalizedString")
        e.attrib["lang"] = "en"
        e.text = "From element"

        data = [e, {"lang": "uk", "text": "Від словника"}]

        slot = _InternationalStringValueType(data)
        slot.name = "MixedSlot"

        value_el = slot.element.find(".//{*}SlotValue/{*}Value")
        assert len(value_el) == 2
        # dict item stores lang as xml:lang attribute
        dict_child = value_el[1]
        assert dict_child.attrib.get(f"{{{XML_NS}}}lang") == "uk"
        assert dict_child.attrib.get("value") == "Від словника"

    def test_list_with_unsupported_type_skipped(self, caplog):
        """Non-Element, non-dict items in list are skipped with a warning."""
        import logging
        data = ["plain string", 42, None]

        with caplog.at_level(logging.WARNING, logger="pyRegRep4.RIMElement"):
            slot = _InternationalStringValueType(data)
            slot.name = "BadSlot"

        value_el = slot.element.find(".//{*}SlotValue/{*}Value")
        # No children added
        assert len(value_el) == 0
        # Three distinct unsupported types → 3 unique warning messages
        unique_messages = {r.message for r in caplog.records}
        assert len(unique_messages) == 3

    def test_xsi_type_attribute(self):
        """SlotValue must carry xsi:type=rim:InternationalStringValueType."""
        elem = etree.Element("LocalizedString")
        slot = _InternationalStringValueType(elem)
        slot.name = "TypeCheck"

        slot_value = slot.element.find(".//{*}SlotValue")
        assert slot_value is not None
        type_attrs = [v for k, v in slot_value.attrib.items() if "type" in k]
        assert any("InternationalStringValueType" in v for v in type_attrs)

    def test_serialization_to_bytes(self):
        """text property returns valid XML bytes containing InternationalStringValueType."""
        elem = etree.Element("LocalizedString")
        elem.text = "Test"
        slot = _InternationalStringValueType(elem)
        slot.name = "SerialSlot"

        xml_bytes = slot.text
        assert isinstance(xml_bytes, bytes)
        assert b"InternationalStringValueType" in xml_bytes

    def test_get_slot_international_string(self):
        """get_slot with InternationalStringValueType returns correct instance."""
        elem = etree.Element("LocalizedString")
        slot = get_slot("IntlSlot", "InternationalStringValueType", elem)
        assert isinstance(slot, _InternationalStringValueType)
        assert slot.name == "IntlSlot"

    def test_name_setter_rebuilds_element(self):
        """Setting name after creation rebuilds the XML element."""
        elem = etree.Element("LocalizedString")
        elem.text = "Hello"
        slot = _InternationalStringValueType(elem)
        slot.name = "First"
        assert slot.element.attrib.get("name") == "First"
        slot.name = "Second"
        assert slot.element.attrib.get("name") == "Second"


class TestSlotElementGeneration:
    """Test that slots generate proper XML elements."""

    def test_slot_has_name_attribute(self):
        """Test that generated slot elements have name attribute."""
        slot = _StringValueType("value")
        slot.name = "TestName"

        elem = slot.element
        assert elem.attrib.get("name") == "TestName"

    def test_slot_has_slot_value_child(self):
        """Test that slot elements have SlotValue child."""
        slot = _StringValueType("value")
        slot.name = "Test"

        elem = slot.element
        # Find SlotValue element (accounting for namespace)
        children = [child for child in elem if "SlotValue" in child.tag]
        assert len(children) > 0

    def test_slot_value_has_type_attribute(self):
        """Test that SlotValue has xsi:type attribute."""
        slot = _StringValueType("value")
        slot.name = "Test"

        elem = slot.element
        slot_value = [child for child in elem if "SlotValue" in child.tag][0]
        # Should have xsi:type attribute
        assert any("type" in attr for attr in slot_value.attrib.keys())

    def test_get_slot_preserves_all_metadata(self):
        """Test that get_slot preserves name and value correctly."""
        test_value = "test data"
        test_name = "metadata"

        slot = get_slot(test_name, "StringValueType", test_value)

        assert slot.name == test_name
        assert slot.value == test_value
        assert slot.element.attrib.get("name") == test_name


class TestSimpleElementContainers:
    """Regression tests for classes sharing common element/text behavior."""

    @pytest.mark.parametrize(
        "obj",
        [RegistryObject(), RepositoryItemRef(), QueryResponse(), Classification()],
    )
    def test_element_raises_before_create(self, obj):
        with pytest.raises(ValueError, match="XML element is not initialized"):
            _ = obj.element

    def test_registry_object_create_and_serialize(self):
        obj = RegistryObject()
        assert obj.create_element("rim:ExtrinsicObject", "urn:uuid:test") is obj
        assert b"RegistryObject" in obj.text

    def test_repository_item_ref_create_and_serialize(self):
        obj = RepositoryItemRef()
        assert obj.create_element("https://example.org/doc.xml", "Doc") is obj
        assert b"RepositoryItemRef" in obj.text
        assert b"xlink:href" in obj.text

    def test_query_response_create_and_serialize(self):
        obj = QueryResponse()
        assert obj.create_element(
            "urn:oasis:names:tc:ebxml-regrep:ResponseStatusType:Success", "req-1"
        ) is obj
        assert b"QueryResponse" in obj.text

    def test_classification_create_and_serialize(self):
        obj = Classification()
        assert obj.create_element("urn:uuid:cls", "urn:scheme", "Annex") is obj
        assert b"Classification" in obj.text



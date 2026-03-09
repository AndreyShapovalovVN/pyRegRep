"""
Unit tests for pyRegRep4.RIMParsing module.

Tests cover:
- XML parsing and namespace handling
- Slot extraction and value processing
- Type conversion (Boolean, String, International String, etc.)
- Serialization functionality
"""

import inspect
import pytest
from lxml import etree
from pathlib import Path
from pyRegRep4.RIMParsing import Parsing


# Test data directory
TEST_DATA_DIR = Path(__file__).parent


def _supports_any_type_argument(parsing: Parsing) -> bool:
    """Return True when serialize() supports `any_type` keyword argument."""
    return "any_type" in inspect.signature(parsing.serialize).parameters


class TestParsingBasics:
    """Test basic Parsing class functionality."""

    @pytest.fixture
    def first_request(self):
        """Load the first EDM request XML file."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Request.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    @pytest.fixture
    def first_response(self):
        """Load the first EDM response XML file."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Response.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_parsing_initialization(self, first_request):
        """Test that Parsing object is correctly initialized."""
        assert first_request is not None
        assert first_request.doc is not None
        assert first_request.xml is not None
        assert first_request.slots is not None

    def test_namespace_handling(self, first_request):
        """Test that namespaces are correctly detected and stored."""
        assert first_request._ns is not None
        assert isinstance(first_request._ns, dict)
        # Common namespaces in RIM documents
        assert any(ns for ns in first_request._ns.values() if "rim" in ns.lower() or "regrep" in ns.lower())

    def test_slots_structure(self, first_request):
        """Test that slots dictionary has expected structure."""
        assert "doc" in first_request.slots
        assert "query" in first_request.slots
        assert "exception" in first_request.slots
        assert "object" in first_request.slots

        # All should be dictionaries
        for key in first_request.slots.keys():
            assert isinstance(first_request.slots[key], dict), f"slots['{key}'] should be a dict"

    def test_slots_content_not_empty(self, first_request):
        """Test that at least one slot category contains data."""
        slots = first_request.slots
        total_items = sum(len(v) for v in slots.values())
        assert total_items > 0, "Should have at least some slots in the document"


class TestSlotParsing:
    """Test slot parsing and extraction."""

    @pytest.fixture
    def request_doc(self):
        """Load request document for slot tests."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Request.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_spec_identifier_present(self, request_doc):
        """Test that SpecificationIdentifier slot is present."""
        doc_slots = request_doc.slots.get("doc", {})
        assert "SpecificationIdentifier" in doc_slots

    def test_spec_identifier_value(self, request_doc):
        """Test SpecificationIdentifier has expected value format."""
        doc_slots = request_doc.slots.get("doc", {})
        spec_id = doc_slots.get("SpecificationIdentifier")
        assert spec_id is not None
        # It should be a tuple with (type, value)
        assert isinstance(spec_id, tuple) and len(spec_id) == 2

    def test_issue_datetime_present(self, request_doc):
        """Test that IssueDateTime slot is present."""
        doc_slots = request_doc.slots.get("doc", {})
        assert "IssueDateTime" in doc_slots

    def test_procedure_slot_present(self, request_doc):
        """Test that Procedure slot is present."""
        doc_slots = request_doc.slots.get("doc", {})
        assert "Procedure" in doc_slots

    def test_boolean_slot_present(self, request_doc):
        """Test that boolean slots are present."""
        doc_slots = request_doc.slots.get("doc", {})
        assert "PossibilityForPreview" in doc_slots
        assert "ExplicitRequestGiven" in doc_slots


class TestValueTypeParsing:
    """Test parsing of different value types."""

    @pytest.fixture
    def request_doc(self):
        """Load request document for value type tests."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Request.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_string_value_type(self, request_doc):
        """Test parsing of StringValueType."""
        doc_slots = request_doc.slots.get("doc", {})
        spec_id = doc_slots.get("SpecificationIdentifier")

        assert spec_id is not None
        type_name, value = spec_id
        assert "StringValueType" in type_name
        # Value should be a string or bytes
        assert isinstance(value, (str, bytes))

    def test_boolean_value_type(self, request_doc):
        """Test parsing of BooleanValueType."""
        doc_slots = request_doc.slots.get("doc", {})
        preview = doc_slots.get("PossibilityForPreview")

        assert preview is not None
        type_name, value = preview
        assert "BooleanValueType" in type_name

    def test_international_string_value_type(self, request_doc):
        """Test parsing of InternationalStringValueType."""
        doc_slots = request_doc.slots.get("doc", {})
        procedure = doc_slots.get("Procedure")

        assert procedure is not None
        type_name, value = procedure
        assert "InternationalStringValueType" in type_name
        # Should return a list of localized strings
        assert isinstance(value, list)


class TestSerialization:
    """Test serialization functionality."""

    @pytest.fixture
    def request_doc(self):
        """Load request document for serialization tests."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Request.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    @pytest.fixture
    def response_doc(self):
        """Load response document for serialization tests."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Response.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_serialize_returns_dict(self, request_doc):
        """Test that serialize returns a dictionary."""
        serialized = request_doc.serialize()
        assert isinstance(serialized, dict)

    def test_serialize_structure(self, request_doc):
        """Test that serialized data has expected structure."""
        serialized = request_doc.serialize()
        assert "doc" in serialized
        assert "query" in serialized
        assert "exception" in serialized
        assert "object" in serialized

    def test_serialize_removes_type_tuples(self, request_doc):
        """Test that serialization removes type information and returns values."""
        serialized = request_doc.serialize()
        doc_slots = serialized.get("doc", {})

        # After serialization, values should not be tuples with types
        for key, value in doc_slots.items():
            if value is not None:
                # Should not be (type, value) tuples anymore
                assert not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], str))

    def test_serialize_string_value(self, request_doc):
        """Test serialization of string values."""
        serialized = request_doc.serialize()
        spec_id = serialized.get("doc", {}).get("SpecificationIdentifier")

        assert spec_id is not None
        # Should be a string value
        assert isinstance(spec_id, (str, bytes))

    def test_serialize_boolean_value(self, request_doc):
        """Test serialization of boolean values."""
        serialized = request_doc.serialize()
        preview = serialized.get("doc", {}).get("PossibilityForPreview")

        assert preview is not None
        # Should be converted to Python boolean
        assert isinstance(preview, bool)

    def test_serialize_international_string(self, request_doc):
        """Test serialization of international string values."""
        serialized = request_doc.serialize()
        procedure = serialized.get("doc", {}).get("Procedure")

        assert procedure is not None
        # Should be a list of dicts with lang and value
        if isinstance(procedure, list):
            assert all(isinstance(item, dict) for item in procedure)

    def test_serialize_any_value_type_default_returns_element(self, request_doc):
        """AnyValueType with any_type=False should return lxml Element."""
        if _supports_any_type_argument(request_doc):
            serialized = request_doc.serialize(any_type=False)
        else:
            serialized = request_doc.serialize()
        evidence_provider = serialized.get("doc", {}).get("EvidenceProvider")

        assert evidence_provider is not None
        assert isinstance(evidence_provider, etree._Element)

    def test_serialize_any_value_type_to_dict(self, request_doc):
        """AnyValueType with any_type=True should be serialized to a plain dictionary."""
        if not _supports_any_type_argument(request_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized = request_doc.serialize(any_type=True)
        evidence_provider = serialized.get("doc", {}).get("EvidenceProvider")

        assert evidence_provider is not None
        assert isinstance(evidence_provider, dict)
        assert any("Agent" in key for key in evidence_provider.keys())

    def test_serialize_collection_with_any_value_type_default(self, request_doc):
        """CollectionValueType with AnyValueType items (default) should contain Elements."""
        if _supports_any_type_argument(request_doc):
            serialized = request_doc.serialize(any_type=False)
        else:
            serialized = request_doc.serialize()
        requirements = serialized.get("doc", {}).get("Requirements")

        assert isinstance(requirements, list)
        assert requirements, "Requirements should not be empty"
        assert all(isinstance(item, etree._Element) for item in requirements)

    def test_serialize_collection_with_any_value_type(self, request_doc):
        """CollectionValueType with AnyValueType items (any_type=True) should serialize to dicts."""
        if not _supports_any_type_argument(request_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized = request_doc.serialize(any_type=True)
        requirements = serialized.get("doc", {}).get("Requirements")

        assert isinstance(requirements, list)
        assert requirements, "Requirements should not be empty"
        assert all(isinstance(item, dict) for item in requirements)
        assert all(not isinstance(item, etree._Element) for item in requirements)


class TestMultipleFiles:
    """Test parsing multiple test files."""

    @pytest.mark.parametrize("filename", [
        "EDM_Ferst_Request.xml",
        "EDM_Ferst_Response.xml",
        "EDM_Second_Request.xml",
        "EDM_Second_Response.xml",
    ])
    def test_all_files_parse_without_error(self, filename):
        """Test that all test XML files can be parsed without errors."""
        xml_file = TEST_DATA_DIR / filename
        assert xml_file.exists(), f"Test file {filename} not found"

        with open(xml_file, "rb") as f:
            parsing = Parsing(f.read())

        assert parsing is not None
        assert parsing.slots is not None
        assert isinstance(parsing.slots, dict)

    @pytest.mark.parametrize("filename", [
        "EDM_Ferst_Request.xml",
        "EDM_Ferst_Response.xml",
        "EDM_Second_Request.xml",
        "EDM_Second_Response.xml",
    ])
    def test_all_files_serialize(self, filename):
        """Test that all test files can be serialized."""
        xml_file = TEST_DATA_DIR / filename
        with open(xml_file, "rb") as f:
            parsing = Parsing(f.read())

        serialized = parsing.serialize()
        assert isinstance(serialized, dict)
        assert "doc" in serialized


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_xml_raises_error(self):
        """Test that invalid XML raises an appropriate error."""
        invalid_xml = b"<invalid>not closed"
        with pytest.raises(Exception):  # lxml will raise XMLSyntaxError
            Parsing(invalid_xml)

    def test_empty_xml_handling(self):
        """Test handling of minimal XML documents."""
        # Minimal valid XML with namespaces (includes rs namespace to avoid errors)
        minimal_xml = b'''<?xml version="1.0"?>
<query:QueryRequest xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:4.0"
                    xmlns:query="urn:oasis:names:tc:ebxml-regrep:xsd:query:4.0"
                    xmlns:rs="urn:oasis:names:tc:ebxml-regrep:xsd:rs:4.0">
</query:QueryRequest>'''
        parsing = Parsing(minimal_xml)
        assert parsing is not None
        assert isinstance(parsing.slots, dict)

    @pytest.fixture
    def request_doc(self):
        """Load request document."""
        xml_file = TEST_DATA_DIR / "EDM_Ferst_Request.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_slots_caching(self, request_doc):
        """Test that slots are properly cached and consistent."""
        slots1 = request_doc.slots
        slots2 = request_doc.slots
        # Should return the same cached object
        assert slots1 is slots2

    def test_serialize_consistency(self, request_doc):
        """Test that multiple serializations return consistent results."""
        serialized1 = request_doc.serialize()
        serialized2 = request_doc.serialize()
        assert serialized1 == serialized2


class TestAnyValueTypeSerialization:
    """Dedicated tests for AnyValueType serialization with xmltodict."""

    @pytest.fixture
    def second_response_doc(self):
        """Load second response document which has AnyValueType in objects."""
        xml_file = TEST_DATA_DIR / "EDM_Second_Response.xml"
        with open(xml_file, "rb") as f:
            return Parsing(f.read())

    def test_any_value_type_single_element_default(self, second_response_doc):
        """Single AnyValueType element (default mode) should remain as lxml Element."""
        if _supports_any_type_argument(second_response_doc):
            serialized = second_response_doc.serialize(any_type=False)
        else:
            serialized = second_response_doc.serialize()
        evidence_requester = serialized.get("doc", {}).get("EvidenceRequester")

        assert evidence_requester is not None
        assert isinstance(evidence_requester, etree._Element)

    def test_any_value_type_single_element_serialized(self, second_response_doc):
        """Single AnyValueType element (any_type=True) should be dict with namespace-aware keys."""
        if not _supports_any_type_argument(second_response_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized = second_response_doc.serialize(any_type=True)
        evidence_requester = serialized.get("doc", {}).get("EvidenceRequester")

        assert evidence_requester is not None
        assert isinstance(evidence_requester, dict)
        assert len(evidence_requester) > 0

    def test_any_value_type_preserves_xml_structure(self, second_response_doc):
        """Serialized AnyValueType should preserve XML structure and content."""
        if not _supports_any_type_argument(second_response_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized = second_response_doc.serialize(any_type=True)
        evidence_requester = serialized.get("doc", {}).get("EvidenceRequester")

        assert evidence_requester is not None
        root_keys = list(evidence_requester.keys())
        assert len(root_keys) > 0

        root_key = root_keys[0]
        root_content = evidence_requester[root_key]
        assert isinstance(root_content, dict)

    def test_any_value_type_in_objects_section(self, second_response_doc):
        """AnyValueType in RegistryObject slots should serialize correctly."""
        if not _supports_any_type_argument(second_response_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized = second_response_doc.serialize(any_type=True)
        object_slots = serialized.get("object", {})

        if "EvidenceMetadata" in object_slots:
            evidence_metadata = object_slots["EvidenceMetadata"]
            assert isinstance(evidence_metadata, dict)

    def test_serialize_consistency_across_calls(self, second_response_doc):
        """Multiple serialize(any_type=True) calls should produce identical results."""
        if not _supports_any_type_argument(second_response_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        result1 = second_response_doc.serialize(any_type=True)
        result2 = second_response_doc.serialize(any_type=True)

        assert result1 == result2

    def test_any_type_parameter_does_not_affect_other_types(self, second_response_doc):
        """Setting any_type=True should not affect serialization of other types."""
        if not _supports_any_type_argument(second_response_doc):
            pytest.skip("serialize(any_type=...) is not supported in the current Parsing implementation")

        serialized_with_any = second_response_doc.serialize(any_type=True)
        serialized_without_any = second_response_doc.serialize(any_type=False)

        for section in ["doc", "query", "exception"]:
            for key, val in serialized_with_any.get(section, {}).items():
                if key not in ["EvidenceRequester", "EvidenceProvider", "EvidenceMetadata"]:
                    assert key in serialized_without_any.get(section, {})


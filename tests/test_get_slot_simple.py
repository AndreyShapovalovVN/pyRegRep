#!/usr/bin/env python3
"""
Simple test script to verify get_slot() functionality.
"""

import datetime
import sys

import pytest
from lxml import etree

from pyRegRep4.RIMElement import _AnyValueType, _StringValueType, get_slot


def test_basic_functionality():
    """Test basic get_slot() functionality."""
    print("Testing get_slot() function...")
    print("-" * 60)

    # Test 1: StringValueType
    print("\n1. Testing StringValueType...")
    string_slot = get_slot("TestString", "StringValueType", "hello world")
    assert string_slot.name == "TestString"
    assert string_slot.value == "hello world"
    assert isinstance(string_slot, _StringValueType)
    print("   ✓ StringValueType works correctly")

    # Test 2: BooleanValueType
    print("2. Testing BooleanValueType...")
    bool_slot = get_slot("TestBool", "BooleanValueType", True)
    assert bool_slot.name == "TestBool"
    assert bool_slot.value is True
    print("   ✓ BooleanValueType works correctly")

    # Test 3: DateTimeValueType
    print("3. Testing DateTimeValueType...")
    now = datetime.datetime(2024, 3, 15, 10, 30, 45)
    datetime_slot = get_slot("TestTime", "DateTimeValueType", now)
    assert datetime_slot.name == "TestTime"
    assert datetime_slot.value == now
    print("   ✓ DateTimeValueType works correctly")

    # Test 4: AnyValueType
    print("4. Testing AnyValueType...")
    elem = etree.Element("CustomData")
    elem.text = "custom content"
    any_slot = get_slot("TestAny", "AnyValueType", elem)
    assert any_slot.name == "TestAny"
    assert isinstance(any_slot, _AnyValueType)
    print("   ✓ AnyValueType works correctly")

    # Test 5: Invalid type handling
    print("5. Testing error handling...")
    with pytest.raises(ValueError, match="Невідомий тип слота"):
        get_slot("Invalid", "InvalidType", "value")
    print("   ✓ Error handling works correctly")

    # Test 6: XML generation
    print("6. Testing XML generation...")
    slot = get_slot("XMLTest", "StringValueType", "test")
    xml_bytes = slot.text
    assert isinstance(xml_bytes, bytes)
    assert b"XMLTest" in xml_bytes
    assert b"StringValueType" in xml_bytes
    print("   ✓ XML generation works correctly")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

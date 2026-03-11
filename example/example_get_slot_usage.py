"""
Example demonstrating usage of get_slot() function for creating RIM slot elements.

The get_slot() function is a factory function that creates appropriate slot objects
based on the slot type. It supports the following RIM slot value types:
- StringValueType: For text values
- BooleanValueType: For boolean values
- DateTimeValueType: For datetime values
- CollectionValueType: For collections of elements
- AnyValueType: For arbitrary XML elements
- InternationalStringValueType: For multilingual text
"""

import datetime
from lxml import etree
from pyRegRep4.RIMElement import get_slot

# Example 1: Create a StringValueType slot
print("=" * 80)
print("Example 1: StringValueType")
print("=" * 80)

string_slot = get_slot("SpecificationIdentifier", "StringValueType", "oots-edm:v1.2")
print(f"Slot name: {string_slot.name}")
print(f"Slot value: {string_slot.value}")
print(f"Slot XML:\n{string_slot.text.decode()}\n")


# Example 2: Create a BooleanValueType slot
print("=" * 80)
print("Example 2: BooleanValueType")
print("=" * 80)

bool_slot = get_slot("PossibilityForPreview", "BooleanValueType", True)
print(f"Slot name: {bool_slot.name}")
print(f"Slot value: {bool_slot.value}")
print(f"Slot XML:\n{bool_slot.text.decode()}\n")


# Example 3: Create a DateTimeValueType slot
print("=" * 80)
print("Example 3: DateTimeValueType")
print("=" * 80)

now = datetime.datetime(2024, 3, 15, 10, 30, 45)
datetime_slot = get_slot("IssueDateTime", "DateTimeValueType", now)
print(f"Slot name: {datetime_slot.name}")
print(f"Slot value: {datetime_slot.value}")
print(f"Slot XML:\n{datetime_slot.text.decode()}\n")


# Example 4: Create an AnyValueType slot
print("=" * 80)
print("Example 4: AnyValueType")
print("=" * 80)

# Create a custom XML element
custom_elem = etree.Element("CustomData")
custom_elem.text = "Custom payload"
custom_elem.attrib["id"] = "unique-123"

any_slot = get_slot("CustomPayload", "AnyValueType", custom_elem)
print(f"Slot name: {any_slot.name}")
print(f"Slot contains XML element: {any_slot.value.tag}")
print(f"Slot XML:\n{any_slot.text.decode()}\n")


# Example 5: Create an InternationalStringValueType slot
print("=" * 80)
print("Example 5: InternationalStringValueType")
print("=" * 80)

# Create multilingual strings
local_strings = []

en_string = etree.Element("LocalString")
en_string.text = "English description"
en_string.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
local_strings.append(en_string)

uk_string = etree.Element("LocalString")
uk_string.text = "Український опис"
uk_string.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "uk"
local_strings.append(uk_string)

intl_slot = get_slot("Description", "InternationalStringValueType", local_strings)
print(f"Slot name: {intl_slot.name}")
print(f"Number of language variants: {len(intl_slot.value)}")
print(f"Slot XML:\n{intl_slot.text.decode()}\n")


# Example 6: Create a CollectionValueType slot
print("=" * 80)
print("Example 6: CollectionValueType")
print("=" * 80)

# Create a collection item
collection_item = etree.Element("Item")
child = etree.SubElement(collection_item, "Data")
child.text = "Collection data"

coll_slot = get_slot("Items", "CollectionValueType", collection_item)
print(f"Slot name: {coll_slot.name}")
print(f"Slot XML:\n{coll_slot.text.decode()}\n")


# Example 7: Error handling - invalid slot type
print("=" * 80)
print("Example 7: Error handling")
print("=" * 80)

try:
    invalid_slot = get_slot("InvalidSlot", "InvalidType", "value")
except ValueError as e:
    print(f"Error caught: {e}\n")


print("=" * 80)
print("All examples completed successfully!")
print("=" * 80)


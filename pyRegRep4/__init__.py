"""
pyRegRep4 - Python Registry Repository for RIM/ebXML documents.

This module provides tools for parsing, creating, and manipulating
RIM (Registry Information Model) and ebXML documents.

Main Components:
- RIMElement: Classes for creating RIM slot elements
- RIMParsing: Parser for reading and extracting data from RIM documents
"""

from pyRegRep4.RIMElement import (
    get_slot,
    Xml,
    _StringValueType,
    _BooleanValueType,
    _TimeStamp,
    _CollectionValueType,
    _AnyValueType,
    _InternationalStringValueType,
)

__all__ = [
    "get_slot",
    "Xml",
    "_StringValueType",
    "_BooleanValueType",
    "_TimeStamp",
    "_CollectionValueType",
    "_AnyValueType",
    "_InternationalStringValueType",
]

__version__ = "7.1.0"
__author__ = "Andrey Shapovalov"


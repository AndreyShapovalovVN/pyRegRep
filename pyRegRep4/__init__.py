"""
pyRegRep4 - Python Registry Repository for RIM/ebXML documents.

This module provides tools for parsing, creating, and manipulating
RIM (Registry Information Model) and ebXML documents.

Main Components:
- RIMElement: Classes for creating RIM slot elements
- RIMParsing: Parser for reading and extracting data from RIM documents
"""

from pyRegRep4.RIMElement import get_slot
from pyRegRep4.utils import deep_get
from pyRegRep4.RIMParsing import Parsing, serialize_any_value_type

__all__ = [
    "get_slot",
    "deep_get",
    "Parsing",
    "serialize_any_value_type",
]

__version__ = "12"
__author__ = "Andrey Shapovalov"


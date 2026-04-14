"""Namespace management for RIM/ebXML documents."""

from typing import Dict


class NS:
    """Base class for handling XML namespaces."""

    # Default namespaces for RIM/ebXML documents
    DEFAULT_NAMESPACES = {
        "rim": "urn:oasis:names:tc:ebxml-regrep:xsd:rim:4.0",
        "query": "urn:oasis:names:tc:ebxml-regrep:xsd:query:4.0",
        "rs": "urn:oasis:names:tc:ebxml-regrep:xsd:rs:4.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsd": "http://www.w3.org/2001/XMLSchema",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
    }

    def __init__(self):
        """Initialize namespace handling."""
        self._ns: Dict[str, str] = self.DEFAULT_NAMESPACES.copy()  # type: ignore

    def _tname(self, prefix: str, localname: str) -> str:
        """
        Create a qualified tag name with namespace.

        Args:
            prefix: Namespace prefix (e.g., 'rim', 'xsi')
            localname: Local element name

        Returns:
            Qualified tag name in Clark notation
        """
        if prefix not in self._ns:
            raise ValueError(f"Unknown namespace prefix: {prefix}")

        return f"{{{self._ns[prefix]}}}{localname}"

    def _extract_namespaces(self) -> Dict[str, str]:
        """
        Extract namespaces from the document.
        Override this method in subclasses if needed.

        Returns:
            Dictionary of namespace mappings
        """
        return self._ns.copy()

    @property
    def ns(self) -> Dict[str, str]:
        """Get the namespace mappings."""
        return self._ns.copy()



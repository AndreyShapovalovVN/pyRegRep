import datetime
import uuid

from pyRegRep4.NS import NS
from lxml import etree


#         Initializes the GetEvidance instance.


class _xml(NS):
    def __init__(self, value):
        self._element: etree._Element
        self.name: str
        self.value = value
        self._create_element()

    def _create_element(self): ...

    @property
    def element(self) -> etree._Element:
        """
        Returns the XML element representing the possibility for preview.
        :return: The XML element.
        """
        return self._element

    @property
    def text(self) -> bytes:
        return etree.tostring(self._element)


class _StringValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:StringValueType"},
        )
        if isinstance(self.value, str):
            value = self.value
        else:
            raise ValueError("Value must be a string.")
        etree.SubElement(sv, self._tname("rim", "Value")).text = value


class _BooleanValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:BooleanValueType"},
        )
        if isinstance(self.value, bool):
            value = str(self.value).lower()
        else:
            raise ValueError("Value must be a boolean")
        etree.SubElement(sv, self._tname("rim", "Value")).text = value


class _IntegerValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:IntegerValueType"},
        )
        if isinstance(self.value, int):
            value = str(self.value)
        else:
            raise ValueError(" Value must be an integer.")
        etree.SubElement(sv, self._tname("rim", "Value")).text = value


class _TimeStamp(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:DateTimeValueType"},
        )
        etree.SubElement(sv, self._tname("rim", "Value")).text = self.value.isoformat()


class _CollectionValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={
                self._tname("xsi", "type"): "rim:CollectionValueType",
                "collectionType": "urn:oasis:names:tc:ebxml-regrep:CollectionType:Set",
            },
        )
        sv.append(self.value)


class _AnyValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:AnyValueType"},
        )
        sv.append(self.value)


class _InternationalStringValueType(_xml):
    def _create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns, attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:InternationalStringValueType"},
        )
        v = etree.SubElement(sv, self._tname("rim", "Value"))
        if isinstance(self.value, list):
            for item in self.value:
                v.append(item)
        else:
            v.append(self.value)


class PossibilityForPreview(_BooleanValueType):
    def __init__(self, value: bool):
        self.name = "PossibilityForPreview"
        super().__init__(value)


class SpecificationIdentifier(_StringValueType):
    def __init__(self, value: str = "oots-edm:v1.2"):
        self.name = "SpecificationIdentifier"
        super().__init__(value)


class EvidenceResponseIdentifier(_StringValueType):
    def __init__(self, value: str = f"{uuid.uuid4()}"):
        self.name = "EvidenceResponseIdentifier"
        super().__init__(value)


class IssueDateTime(_TimeStamp):
    def __init__(self, value: datetime.datetime = datetime.datetime.now()):
        self.name = "IssueDateTime"
        super().__init__(value)


class TimeStamp(_TimeStamp):
    def __init__(self, value: datetime.datetime = datetime.datetime.now()):
        self.name = "Timestamp"
        super().__init__(value)


class EvidenceProvider(_CollectionValueType):
    def __init__(self, value: etree._Element):
        self.name = "EvidenceProvider"
        super().__init__(value)


class ErrorProvider(_AnyValueType):
    def __init__(self, value: etree._Element):
        self.name = "ErrorProvider"
        super().__init__(value)


class EvidenceRequester(_AnyValueType):
    def __init__(self, value: etree._Element):
        self.name = "EvidenceRequester"
        super().__init__(value)


class PreviewLocation(_StringValueType):
    def __init__(self, value: str):
        self.name = "PreviewLocation"
        super().__init__(value)


class PreviewDescription(_InternationalStringValueType):
    def __init__(self, value: list[etree._Element]):
        self.name = "PreviewDescription"
        super().__init__(value)


class PreviewMethod(_StringValueType):
    def __init__(self, value: str):
        self.name = "PreviewMethod"
        super().__init__(value)


class EvidenceMetadata(_AnyValueType):
    def __init__(self, value: etree._Element):
        self.name = "EvidenceMetadata"
        super().__init__(value)


__all__ = [
    'EvidenceRequester',
    'EvidenceResponseIdentifier',
    'SpecificationIdentifier',
    'IssueDateTime',
    'EvidenceProvider',
]

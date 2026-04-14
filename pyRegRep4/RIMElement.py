import datetime
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable

from lxml import etree

from pyRegRep4.NS import NS

_logger = logging.getLogger(__name__)

__all__ = [
    "get_slot",
    "RegistryObject",
    "RepositoryItemRef",
    "QueryResponse",
    "Classification"
]


class _ElementContainer(NS):
    """Internal base for simple classes that wrap a single XML element."""

    def __init__(self) -> None:
        super().__init__()
        self._element: etree._Element | None = None

    @property
    def element(self) -> etree._Element:
        if self._element is None:
            raise ValueError("XML element is not initialized")
        return self._element

    @property
    def text(self) -> bytes:
        return etree.tostring(self.element)


class Xml(ABC, _ElementContainer):
    """Base class for slot-like XML objects that carry value and name."""

    def __init__(self, value: Any):
        super().__init__()
        self._name: str = ""
        self.value: Any = value
        self.create_element()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        if self._element is not None:
            self.create_element()

    @abstractmethod
    def create_element(self):
        ...


class _BooleanValueType(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:BooleanValueType"},
        )
        etree.SubElement(sv, self._tname("rim", "Value")).text = str(self.value).lower()


class _StringValueType(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:StringValueType"},
        )
        etree.SubElement(sv, self._tname("rim", "Value")).text = self.value


class _TimeStamp(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:DateTimeValueType"},
        )
        if isinstance(self.value, datetime.datetime):
            etree.SubElement(sv, self._tname("rim", "Value")).text = self.value.isoformat()
        else:
            etree.SubElement(sv, self._tname("rim", "Value")).text = self.value


class _CollectionValueType(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={
                self._tname("xsi", "type"): "rim:CollectionValueType",
                "collectionType": "urn:oasis:names:tc:ebxml-regrep:CollectionType:Set",
            },
        )
        if isinstance(self.value, etree._Element):
            e = etree.SubElement(sv, self._tname("rim", "Element"),
                                 attrib={self._tname("xsi", "type"): 'rim:AnyValueType'})
        else:
            e = etree.SubElement(sv, self._tname("rim", "Element"),
                                 attrib={self._tname("xsi", "type"): 'rim:StringValueType'})
        e.append(self.value)


class _AnyValueType(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:AnyValueType"},
        )
        sv.append(self.value)


class _InternationalStringValueType(Xml):
    def create_element(self):
        self._element = etree.Element(
            self._tname("rim", "Slot"), nsmap=self._ns,
            attrib={"name": self.name}
        )
        sv = etree.SubElement(
            self._element,
            self._tname("rim", "SlotValue"),
            attrib={self._tname("xsi", "type"): "rim:InternationalStringValueType"},
        )
        v = etree.SubElement(sv, self._tname("rim", "Value"))
        if isinstance(self.value, list):
            for item in self.value:
                if isinstance(item, etree._Element):
                    v.append(item)
                elif isinstance(item, dict):
                    element = self._intenation_element(item)
                    if element is not None:
                        v.append(element)
                else:
                    _logger.warning(f"Unsupported item type in InternationalStringValueType: {type(item)}")
        else:
            if isinstance(self.value, etree._Element):
                v.append(self.value)

    def _intenation_element(self, item: dict) -> etree._Element | None:
        if "lang" in item and "text" in item:
            element = etree.Element(
                self._tname("rim", "LocalizedString"),
                attrib={
                    self._tname("xml", "lang"): item["lang"],
                    "value": item["text"]
                }
            )
            return element
        else:
            _logger.warning(f"Invalid item format for InternationalStringValueType: {item}")
            return None


def get_slot(name: str, slot_type: str, value: Any) -> Xml:
    """
    Фабрична функція для створення RIM слотів на базі типу.

    Ця функція спрощує створення об'єктів слотів різних типів, автоматично
    вибираючи правильний клас на основі переданого типу слота.

    Args:
        name (str): Ім'я слота (буде встановлено в атрибут "name" XML елемента)
        slot_type (str): Тип слота. Підтримувані значення:
            - "StringValueType": Для текстових значень
            - "BooleanValueType": Для логічних значень (True/False)
            - "DateTimeValueType": Для дати/часу (datetime.datetime або ISO string)
            - "CollectionValueType": Для колекцій XML елементів
            - "AnyValueType": Для довільних XML елементів
            - "InternationalStringValueType": Для багатомовного тексту
        value (Any): Значення слота. Тип залежить від slot_type:
            - StringValueType: str
            - BooleanValueType: bool
            - DateTimeValueType: datetime.datetime або str (ISO format)
            - CollectionValueType: etree._Element
            - AnyValueType: etree._Element
            - InternationalStringValueType: etree._Element або list[etree._Element]

    Returns:
        Xml: Об'єкт слота (підклас Xml), який представляє RIM слот з даним типом.
             Об'єкт має властивості:
             - name: Ім'я слота
             - value: Значення слота
             - element: XML елемент слота (etree._Element)
             - text: Серіалізований XML як bytes

    Raises:
        ValueError: Якщо переданий slot_type не підтримується. Помилка містить
                   список всіх підтримуваних типів.

    Приклади:
        >>> # Створення StringValueType слота
        >>> slot = get_slot("SpecId", "StringValueType", "oots-edm:v1.2")
        >>> print(slot.name)  # 'SpecId'
        >>> print(slot.value)  # 'oots-edm:v1.2'

        >>> # Створення BooleanValueType слота
        >>> slot = get_slot("Preview", "BooleanValueType", True)
        >>> print(slot.element.tag)  # '{...}Slot'

        >>> # Створення DateTimeValueType слота
        >>> from datetime import datetime
        >>> now = datetime.now()
        >>> slot = get_slot("IssueTime", "DateTimeValueType", now)

        >>> # Створення AnyValueType слота з XML елементом
        >>> from lxml import etree
        >>> elem = etree.Element("CustomData")
        >>> slot = get_slot("Custom", "AnyValueType", elem)

        >>> # Обробка помилки при невідомому типі
        >>> try:
        ...     slot = get_slot("Bad", "UnknownType", "value")
        ... except ValueError as e:
        ...     print(f"Error: {e}")
    """
    slot_type_map: dict[str, Callable[[Any], Xml]] = {
        "StringValueType": _StringValueType,
        "BooleanValueType": _BooleanValueType,
        "DateTimeValueType": _TimeStamp,
        "CollectionValueType": _CollectionValueType,
        "AnyValueType": _AnyValueType,
        "InternationalStringValueType": _InternationalStringValueType,
    }

    slot_class = slot_type_map.get(slot_type)
    if slot_class is None:
        raise ValueError(f"Невідомий тип слота: {slot_type}. Підтримувані типи: {list(slot_type_map.keys())}")

    slot = slot_class(value)
    slot.name = name
    return slot


class RegistryObject(_ElementContainer):
    """Builder for rim:RegistryObject elements."""

    def create_element(self, type: str, id: str):
        self._element = etree.Element(
            self._tname("rim", "RegistryObject"),
            nsmap=self._ns,
            attrib={
                self._tname("xsi", "type"): type,
                "id": id
            }
        )
        return self


class RepositoryItemRef(_ElementContainer):
    """Builder for rim:RepositoryItemRef elements."""

    def create_element(self, href: str, title: str | None = None):
        attr = {self._tname("xlink", "href"): href}
        if title is not None:
            attr["title"] = title

        self._element = etree.Element(
            self._tname("rim", "RepositoryItemRef"),
            nsmap=self._ns,
            attrib=attr
        )
        return self


class QueryResponse(_ElementContainer):
    """Builder for query:QueryResponse elements."""

    def create_element(self, status: str, request_id: str):
        self._element = etree.Element(
            self._tname("query", "QueryResponse"), nsmap=self._ns,
            attrib={
                'status': status,
                'requestId': request_id,
            }
        )
        return self


class Classification(_ElementContainer):
    """Builder for rim:Classification elements."""

    def create_element(self, id: str, classification_scheme: str, classification_node: str):
        self._element = etree.Element(
            self._tname("rim", "Classification"),
            nsmap=self._ns,
            attrib={
                "id": id,
                "classificationScheme": classification_scheme,
                "classificationNode": classification_node
            }
        )
        return self

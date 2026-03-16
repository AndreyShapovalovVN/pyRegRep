import datetime
import logging
from typing import Any

from lxml import etree

from pyRegRep4.NS import NS

_logger = logging.getLogger(__name__)


class Xml(NS):
    def __init__(self, value: Any):
        super().__init__()
        self._name: str = ""
        self.value: Any = value
        self._element: etree._Element | None = None
        self._create_element()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        if self._element is not None:
            self._create_element()

    def _create_element(self):
        ...

    @property
    def element(self) -> etree._Element:
        if self._element is None:
            raise ValueError("XML element is not initialized")
        return self._element

    @property
    def text(self) -> bytes:
        return etree.tostring(self.element)


class _BooleanValueType(Xml):
    def _create_element(self):
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
    def _create_element(self):
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
    def _create_element(self):
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
    def _create_element(self):
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
    def _create_element(self):
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
    def _create_element(self):
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
    slot_type_map = {
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

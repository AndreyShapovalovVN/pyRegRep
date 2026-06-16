import logging
from enum import Enum
from typing import Any

import xmltodict
from lxml import etree

_logger = logging.getLogger(__name__)


def serialize_any_value_type(value: Any) -> Any:
    """Convert XML elements from AnyValueType into plain dictionaries."""
    if isinstance(value, etree._Element):
        try:
            xml_bytes = etree.tostring(value, encoding="utf-8")
            return xmltodict.parse(xml_bytes)
        except Exception as e:
            _logger.warning(f"Не вдалося серіалізувати AnyValueType через xmltodict: {e}")
            return etree.tostring(value, encoding="unicode")
    return value


class ValueTypes(str, Enum):
    """Типи значень у RIM документах."""
    STRING = "StringValueType"
    BOOLEAN = "BooleanValueType"
    INTEGER = "IntegerValueType"
    DATETIME = "DateTimeValueType"
    INTERNATIONAL_STRING = "InternationalStringValueType"
    COLLECTION = "CollectionValueType"
    ANY = "AnyValueType"


class ParsingError(Exception):
    """Базовий клас для помилок парсування."""
    pass


class Parsing:
    """
    Парсер RIM/ebXML документів.

    Автоматично обробляє namespace, витягує запити, винятки та об'єкти реєстру.

    Attributes:
        xml: Декодований XML як рядок
        doc: Распарсений XML документ (etree._Element)
        query: Розташування Query елемента у документі або None
        exception: Розташування Exception елемента у документі або None
        objects: Список RegistryObject елементів
        slots: Кешований словник усіх слотів з документу
    """

    def __init__(self, doc: bytes | str):

        if isinstance(doc, bytes):
            self.xml = doc.decode("utf-8")
        elif isinstance(doc, str):
            self.xml = doc
            doc = doc.encode("utf-8")  # Конвертуємо назад в bytes для lxml
        else:
            raise ParsingError(
                f"Невалідний тип даних для парсування: {type(doc)}. "
                "Очікується bytes або str."
            )

        try:
            parser = etree.XMLParser(remove_comments=True)
            self.doc = etree.fromstring(doc, parser)
        except etree.XMLSyntaxError as e:
            raise ParsingError(f"Помилка парсування XML: {e}") from e

        # Обробка namespace
        self._ns = self._extract_namespaces()

        # Витягування основних елементів
        try:
            self.query = self.doc.find(".//query:Query", namespaces=self._ns)
        except Exception as e:
            _logger.warning(f"Namespace не знайдено: {e}")
            self.query = None

        try:
            self.exception = self.doc.find(".//rs:Exception", namespaces=self._ns)
        except Exception as e:
            _logger.warning(f"Namespace не знайдено: {e}")
            self.exception = None

        try:
            self.objects = self.doc.findall(".//rim:RegistryObject", namespaces=self._ns)
        except Exception as e:
            _logger.warning(f"Namespace не знайдено: {e}")
            self.objects = []

        # Кешований результат
        self._slots_cache: dict[str, Any] | None = None
        self.slots = self.__list_slots()

    def _extract_namespaces(self) -> dict[str, str]:
        """
        Витягти всі namespace з кореневого елемента XML.

        Returns:
            Словник у форматі {префікс: URI}
        """
        ns = {}
        for k, v in self.doc.nsmap.items():
            if k is not None and v is not None:
                ns[k] = v
                _logger.debug(f"Знайдено namespace: {k} -> {v}")
            else:
                _logger.warning(f"Пропущено некоректний namespace: {k} -> {v}")
        return ns

    def __safe_add_slot(
        self,
        target: dict[str, tuple[str, Any]],
        slot: etree._Element,
        context: str,
    ) -> None:
        name = slot.get("name")
        if not name:
            return

        try:
            target[name] = self.__value(slot)
        except ParsingError as e:
            _logger.exception(f"Помилка парсування слота '{context}/{name}': {e}")

    def __tname(self, ns: str, tag: str) -> str:
        """
        Побудувати повне ім'я тега з namespace.

        Args:
            ns: Префікс namespace
            tag: Локальне ім'я тега

        Returns:
            Повне ім'я тега у форматі {namespace_uri}tag
        """
        if not ns or ns not in self._ns:
            _logger.warning(f"Namespace '{ns}' не знайдено, повертаємо просто тег '{tag}'")
            return tag
        return f"{{{self._ns[ns]}}}{tag}"

    def __extract_type(self, type_attr: str) -> str:
        """
        Витягти тип значення з атрибута xsi:type.

        Args:
            type_attr: Атрибут у форматі "префікс:Тип"

        Returns:
            Само значення типу без префіксу

        Raises:
            ParsingError: Якщо формат типу невалідний
        """
        if not type_attr:
            raise ParsingError("Атрибут xsi:type не знайдено")

        if ':' not in type_attr:
            raise ParsingError(f"Невалідний формат типу: {type_attr}. Очікується 'префікс:Тип'")

        type_value = type_attr.split(":")[1].strip()
        if not type_value:
            raise ParsingError(f"Тип значення не можна витягти з: {type_attr}")

        return type_value

    def __get_slot_value(self, slot: etree._Element) -> etree._Element:
        if len(slot) == 0:
            raise ParsingError(f"Слот '{slot.get('name')}' не має дочірніх елементів")

        return slot[0]

    def __get_slot_value_type(self, slot_value: etree._Element) -> str:
        type_attr = slot_value.get(self.__tname("xsi", "type"), "")

        try:
            return self.__extract_type(type_attr)
        except ParsingError as e:
            _logger.exception(f"Помилка витягування типу для слота: {e}")
            raise

    def __parse_slot_value(self, type_: str, slot_value: etree._Element) -> Any:
        if ValueTypes.ANY.value in type_:
            return self.__parse_any_value(slot_value)

        if ValueTypes.INTERNATIONAL_STRING.value in type_:
            return self.__parse_international_string(slot_value)

        if ValueTypes.COLLECTION.value in type_:
            return self.__parse_collection(slot_value)

        return self.__parse_simple_value(slot_value)

    def __parse_any_value(self, slot_value: etree._Element) -> Any:
        return slot_value[0] if len(slot_value) > 0 else None

    def __parse_international_string(self, slot_value: etree._Element) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []

        if len(slot_value) == 0:
            return values

        for item in slot_value[0]:
            values.append(
                {
                    "lang": item.get(self.__tname("xsi", "lang")),
                    "value": item.get("value"),
                }
            )

        return values

    def __parse_collection(self, slot_value: etree._Element) -> list[tuple[str, Any]]:
        values = []

        for item in slot_value:
            wrapper = etree.Element("wrapper")
            wrapper.append(item)
            values.append(self.__value(wrapper))

        return values

    def __parse_simple_value(self, slot_value: etree._Element) -> Any:
        if len(slot_value) > 0 and len(slot_value[0]) > 0:
            return slot_value[0][0].text

        if len(slot_value) > 0:
            return slot_value[0].text

        return None

    def __value(self, slot: etree._Element) -> tuple[str, Any]:
        slot_value = self.__get_slot_value(slot)
        type_ = self.__get_slot_value_type(slot_value)

        try:
            return type_, self.__parse_slot_value(type_, slot_value)
        except (IndexError, AttributeError) as e:
            _logger.exception(f"Помилка обробки значення типу {type_}: {e}")
            raise ParsingError(f"Помилка обробки значення: {e}") from e

    def __process_root_element(
        self,
        element: etree._Element,
        slots: dict[str, dict[str, Any]],
    ) -> None:
        if element.tag == self.__tname("rim", "Slot"):
            self.__safe_add_slot(slots["doc"], element, "doc")
            return

        if element.tag == self.__tname("query", "Query"):
            self.__process_slot_container(element, slots["query"], "query")
            return

        if element.tag == self.__tname("rs", "Exception"):
            self.__process_slot_container(element, slots["exception"], "exception")
            return

        if element.tag == self.__tname("rim", "RegistryObjectList"):
            self.__process_registry_object_list(element, slots["object"])

    def __process_slot_container(
        self,
        container: etree._Element,
        target: dict[str, Any],
        context: str,
    ) -> None:
        for item in container:
            self.__safe_add_slot(target, item, context)

    def __process_registry_object_list(
        self,
        registry_object_list: etree._Element,
        target: dict[str, Any],
    ) -> None:
        for registry_object in registry_object_list:
            obj_data = self.__process_registry_object(registry_object)

            if obj_data:
                target.update(obj_data)

    def __process_registry_object(
        self,
        registry_object: etree._Element,
    ) -> dict[str, Any]:
        obj_data: dict[str, Any] = {}

        for child in registry_object:
            if child.tag == self.__tname("rim", "Slot"):
                self.__safe_add_slot(obj_data, child, "object")

            elif child.tag == self.__tname("rim", "RepositoryItemRef"):
                obj_data["RepositoryItemRef"] = self.__repository_item_ref(child)

        return obj_data

    def __repository_item_ref(self, element: etree._Element) -> dict[str, str | None]:
        return {
            "xlink": element.get(self.__tname("xlink", "href")),
            "title": element.get(self.__tname("xlink", "title")),
        }

    def __list_slots(self) -> dict[str, dict[str, Any]]:
        slots: dict[str, dict[str, Any]] = {
            "doc": {},
            "query": {},
            "exception": {},
            "object": {},
        }

        for element in self.doc:
            try:
                self.__process_root_element(element, slots)
            except Exception as e:
                _logger.exception(f"Неочікувана помилка при обробці елемента: {e}")

        return slots

    def __transform_serialized_value(self, data: Any, any_type: bool) -> Any:
        if isinstance(data, list):
            return [self.__transform_serialized_value(item, any_type) for item in data]

        if isinstance(data, dict):
            return {
                key: self.__transform_serialized_value(value, any_type)
                for key, value in data.items()
            }

        if not isinstance(data, tuple) or len(data) != 2:
            return data

        data_type, value = data
        return self.__transform_value_by_type(data_type, value, any_type)

    def __transform_value_by_type(
        self,
        data_type: str,
        value: Any,
        any_type: bool,
    ) -> Any:
        if data_type == ValueTypes.BOOLEAN.value:
            return value.lower() == "true" if isinstance(value, str) else bool(value)

        if data_type in {
            ValueTypes.STRING.value,
            ValueTypes.DATETIME.value,
        }:
            return value.strip() if isinstance(value, str) else value

        if data_type == ValueTypes.INTEGER.value:
            return int(value) if value else None

        if data_type == ValueTypes.COLLECTION.value:
            return self.__transform_serialized_value(value, any_type)

        if data_type == ValueTypes.ANY.value:
            return serialize_any_value_type(value) if any_type else value

        if data_type == ValueTypes.INTERNATIONAL_STRING.value:
            return self.__transform_serialized_value(value, any_type)

        _logger.warning(f"Невідомий тип значення: {data_type}")
        return (
            self.__transform_serialized_value(value, any_type)
            if isinstance(value, (list, dict))
            else value
        )

    def serialize(self, any_type: bool = False) -> dict[str, Any]:
        serialized = self.__transform_serialized_value(self.slots, any_type)
        if isinstance(serialized, dict):
            return serialized
        raise ParsingError("Очікувався словник після серіалізації слотів")

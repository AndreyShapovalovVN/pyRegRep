import logging
from enum import Enum
from typing import Any, Dict, Optional, Tuple

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
            raise ParsingError(f"Невалідний тип даних для парсування: {type(doc)}. Очікується bytes або str.")

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
        self._slots_cache: Optional[Dict[str, Any]] = None
        self.slots = self.__list_slots()

    def _extract_namespaces(self) -> Dict[str, str]:
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

    def __value(self, slot: etree._Element) -> Tuple[str, Any]:
        """
        Витягти значення зі слота з його типом.

        Args:
            slot: XML елемент слота

        Returns:
            Кортеж (тип_значення, значення)

        Raises:
            ParsingError: Якщо слот має неправильну структуру
        """
        if len(slot) == 0:
            raise ParsingError(f"Слот '{slot.get('name')}' не має дочірніх елементів")

        slot_value = slot[0]  # Отримати SlotValue елемент
        type_attr = slot_value.get(self.__tname("xsi", "type"), '')

        try:
            type_ = self.__extract_type(type_attr)
        except ParsingError as e:
            _logger.error(f"Помилка витягування типу для слота: {e}")
            raise

        # Обробка різних типів значень
        try:
            if ValueTypes.ANY.value in type_:
                return type_, slot_value[0] if len(slot_value) > 0 else None

            elif ValueTypes.INTERNATIONAL_STRING.value in type_:
                values = []
                for item in slot_value[0]:
                    value = {
                        "lang": item.get(self.__tname("xsi", "lang")),
                        "value": item.get("value"),
                    }
                    values.append(value)
                return type_, values

            elif ValueTypes.COLLECTION.value in type_:
                values = []
                for item in slot_value:
                    wrapper = etree.Element("wrapper")
                    wrapper.append(item)
                    values.append(self.__value(wrapper))  # type: ignore
                return type_, values

            else:
                # Прості типи: String, Boolean, DateTime тощо
                if len(slot_value) > 0 and len(slot_value[0]) > 0:
                    return type_, slot_value[0][0].text
                elif len(slot_value) > 0:
                    return type_, slot_value[0].text
                else:
                    return type_, None
        except (IndexError, AttributeError) as e:
            _logger.error(f"Помилка обробки значення типу {type_}: {e}")
            raise ParsingError(f"Помилка обробки значення: {e}") from e

    def __list_slots(self) -> Dict[str, Dict[str, Tuple[str, Any]]]:
        """
        Витягти всі слоти з документу та організувати їх за категоріями.

        Returns:
            Словник структури: {категорія: {ім'я_слота: (тип, значення)}}
        """
        slots: Dict[str, Dict[str, Tuple[str, Any]]] = {
            "doc": {},
            "query": {},
            "exception": {},
            "object": {}
        }

        for element in self.doc:
            try:
                # Слоти на рівні документу
                if element.tag == self.__tname("rim", "Slot"):
                    name = element.get("name")
                    if name:
                        try:
                            slots["doc"][name] = self.__value(element)
                        except ParsingError as e:
                            _logger.error(f"Помилка парсування слота 'doc/{name}': {e}")

                # Query елементи
                elif element.tag == self.__tname("query", "Query"):
                    for query_item in element:
                        name = query_item.get("name")
                        if name:
                            try:
                                slots["query"][name] = self.__value(query_item)
                            except ParsingError as e:
                                _logger.error(f"Помилка парсування слота 'query/{name}': {e}")

                # Exception елементи
                elif element.tag == self.__tname("rs", "Exception"):
                    for exc_item in element:
                        name = exc_item.get("name")
                        if name:
                            try:
                                slots["exception"][name] = self.__value(exc_item)
                            except ParsingError as e:
                                _logger.error(f"Помилка парсування слота 'exception/{name}': {e}")

                # RegistryObject елементи
                elif element.tag == self.__tname("rim", "RegistryObjectList"):
                    for registry_object in element:
                        obj_data: Dict[str, Any] = {}
                        for child_element in registry_object:
                            if child_element.tag == self.__tname("rim", "Slot"):
                                name = child_element.get("name")
                                if name:
                                    try:
                                        obj_data[name] = self.__value(child_element)
                                    except ParsingError as e:
                                        _logger.error(f"Помилка парсування слота 'object/{name}': {e}")

                            elif child_element.tag == self.__tname("rim", "RepositoryItemRef"):
                                obj_data["RepositoryItemRef"] = {
                                    "xlink": child_element.get(self.__tname("xlink", "href")),
                                    "title": child_element.get(self.__tname("xlink", "title")),
                                }

                        if obj_data:
                            slots["object"].update(obj_data)

            except Exception as e:
                _logger.error(f"Неочікувана помилка при обробці елемента: {e}")
                continue

        return slots

    def serialize(self, any_type: bool = False) -> Dict[str, Any]:
        """
        Серіалізувати слоти, перетворюючи типізовані значення на Python об'єкти.

        Перетворює:
        - BooleanValueType -> bool
        - StringValueType -> str
        - DateTimeValueType -> str (ISO format)
        - InternationalStringValueType -> list[dict]
        - CollectionValueType -> list
        - AnyValueType -> Element (default) або dict (якщо any_type=True)

        Args:
            any_type: Якщо True, перетворює AnyValueType елементи в dict через xmltodict.
                     Якщо False (за замовчуванням), повертає lxml Element.

        Returns:
            Серіалізований словник без типової інформації
        """

        def transform_data(data: Any) -> Any:
            """Рекурсивно трансформувати дані, видаляючи тип-інформацію."""
            if isinstance(data, list):
                return [transform_data(item) for item in data]

            elif isinstance(data, dict):
                return {k: transform_data(v) for k, v in data.items()}

            elif isinstance(data, tuple) and len(data) == 2:
                data_type, value = data

                # Перетворення типів значень
                if data_type == ValueTypes.BOOLEAN.value:
                    if isinstance(value, str):
                        return value.lower() == 'true'
                    return bool(value)

                elif data_type == ValueTypes.STRING.value:
                    return value.strip() if isinstance(value, str) else value

                elif data_type == ValueTypes.DATETIME.value:
                    return value.strip() if isinstance(value, str) else value

                elif data_type == ValueTypes.COLLECTION.value:
                    return transform_data(value)

                elif data_type == ValueTypes.ANY.value:
                    if any_type:
                        return serialize_any_value_type(value)
                    return value

                elif data_type == ValueTypes.INTERNATIONAL_STRING.value:
                    return transform_data(value)

                elif data_type == ValueTypes.INTEGER.value:
                    return int(value) if value else None

                # Невідомий тип - повернути значення як є
                else:
                    _logger.warning(f"Невідомий тип значення: {data_type}")
                    return transform_data(value) if isinstance(value, (list, dict)) else value

            return data

        return transform_data(self.slots)

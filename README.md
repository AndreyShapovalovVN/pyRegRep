# pyRegRep

Бібліотека Python для парсування та обробки XML документів у форматі RIM (Registry Information Model) / ebXML.

## Опис

**pyRegRep** — інструмент для роботи з XML документами стандарту Registry Information Model (RIM), що застосовується в системах eGovernment та обміну даними (зокрема, OOTS/EDM). Бібліотека дозволяє легко витягувати, аналізувати та серіалізувати дані з RIM/ebXML документів, а також програмно створювати коректні RIM-слоти різних типів.

## Можливості

- ✅ Парсування RIM/ebXML XML документів (`bytes` або `str`)
- ✅ Автоматична обробка просторів імен (namespaces)
- ✅ Витягування запитів (Query), винятків (Exception) та об'єктів реєстру (RegistryObject)
- ✅ Обробка всіх типів значень: Boolean, String, Integer, DateTime, Collection, InternationalString, AnyValue
- ✅ Серіалізація даних у зручний Python-формат (`dict`)
- ✅ Фабрика слотів `get_slot()` — програмне створення RIM-слотів за типом
- ✅ Серіалізація `AnyValueType` через `xmltodict` (параметр `any_type=True`)
- ✅ Підтримка вкладених колекцій та складних структур
- ✅ Безпечний доступ до вкладених даних через `deep_get()`

## Вимоги

- **Python**: >= 3.10
- **Залежності**:
  - `lxml >= 5.2.1` — робота з XML
  - `xmltodict >= 0.13.0` — серіалізація `AnyValueType`

## Установка

```bash
# З PyPI (якщо опубліковано)
pip install pyRegRep

# З локального джерела (editable)
pip install -e .
```

Під час встановлення через `pip install pyRegRep` або `pip install -e .` runtime-залежності (`lxml`, `xmltodict`) встановлюються автоматично.

## Швидкий старт

### Парсування XML документу

```python
from pyRegRep4.RIMParsing import Parsing

with open("document.xml", "rb") as f:
    parser = Parsing(f.read())

# Усі слоти у вигляді {category: {name: (type, value)}}
print(parser.slots)

# Серіалізовані дані (без типової інформації)
print(parser.serialize())

# Серіалізація з обробкою AnyValueType в dict
print(parser.serialize(any_type=True))

from pyRegRep4 import deep_get

# Безпечний доступ до вкладених ключів
spec_id = deep_get(parser.serialize(), "doc", "SpecificationIdentifier", default="unknown")
print(spec_id)
```

### Програмне створення RIM-слотів

```python
import datetime
from lxml import etree
from pyRegRep4.RIMElement import get_slot

# Текстовий слот
slot = get_slot("SpecificationIdentifier", "StringValueType", "oots-edm:v1.2")
print(slot.name)   # 'SpecificationIdentifier'
print(slot.value)  # 'oots-edm:v1.2'
print(slot.text)   # XML як bytes

# Логічний слот
slot = get_slot("PossibilityForPreview", "BooleanValueType", True)

# Слот дата/час
slot = get_slot("IssueDateTime", "DateTimeValueType", datetime.datetime.now())

# Багатомовний слот через dict-список
slot = get_slot(
    "Title",
    "InternationalStringValueType",
    [
        {"lang": "en", "text": "Birth Certificate"},
        {"lang": "uk", "text": "Свідоцтво про народження"},
    ],
)

# Довільний XML (AnyValueType)
elem = etree.Element("CustomData")
elem.text = "Payload"
slot = get_slot("CustomPayload", "AnyValueType", elem)
```

## API Довідник

### Клас `Parsing` (`pyRegRep4.RIMParsing`)

#### Конструктор

```python
Parsing(doc: bytes | str)
```

| Параметр | Тип | Опис |
|----------|-----|------|
| `doc` | `bytes \| str` | XML документ |

#### Атрибути

| Атрибут | Тип | Опис |
|---------|-----|------|
| `xml` | `str` | XML як рядок |
| `doc` | `etree._Element` | Розібраний XML документ |
| `query` | `etree._Element \| None` | Елемент `Query` (якщо є) |
| `exception` | `etree._Element \| None` | Елемент `Exception` (якщо є) |
| `objects` | `list` | Список `RegistryObject` елементів |
| `slots` | `dict` | Всі слоти у форматі `{category: {name: (type, value)}}` |

Категорії `slots`: `"doc"`, `"query"`, `"exception"`, `"object"`.

#### Метод `serialize(any_type: bool = False) -> dict`

Серіалізує слоти в чистий Python-формат, видаляючи типову інформацію.

| Тип значення | Python-результат |
|---|---|
| `BooleanValueType` | `bool` |
| `StringValueType` | `str` |
| `DateTimeValueType` | `str` (ISO format) |
| `IntegerValueType` | `int` |
| `CollectionValueType` | `list` |
| `InternationalStringValueType` | `list[dict]` з ключами `lang`/`text` |
| `AnyValueType` (за замовчуванням) | `etree._Element` |
| `AnyValueType` (з `any_type=True`) | `dict` (через `xmltodict`) |

---

### Функція `get_slot()` (`pyRegRep4.RIMElement`)

```python
get_slot(name: str, slot_type: str, value: Any) -> Xml
```

Фабрика для програмного створення RIM-слотів.

| Параметр | Тип | Опис |
|----------|-----|------|
| `name` | `str` | Ім'я слота |
| `slot_type` | `str` | Тип слота (див. таблицю нижче) |
| `value` | `Any` | Значення слота |

**Підтримані типи:**

| `slot_type` | Тип `value` | Опис |
|---|---|---|
| `"StringValueType"` | `str` | Текстовий рядок |
| `"BooleanValueType"` | `bool` | Логічне значення |
| `"DateTimeValueType"` | `datetime.datetime` або `str` | Дата/час |
| `"CollectionValueType"` | `etree._Element` | Колекція елементів |
| `"AnyValueType"` | `etree._Element` | Довільний XML елемент |
| `"InternationalStringValueType"` | `etree._Element`, `list[etree._Element]` або `list[dict]` | Багатомовний текст |

**Повертає** об'єкт `Xml` з властивостями:
- `name` — ім'я слота
- `value` — значення
- `element` — XML елемент (`etree._Element`)
- `text` — серіалізований XML (`bytes`)

**Викидає** `ValueError` при невідомому типі слота.

```python
try:
    slot = get_slot("Bad", "UnknownType", "value")
except ValueError as e:
    print(e)  # Невідомий тип слота: UnknownType. Підтримувані типи: [...]
```

---

### Функція `deep_get()` (`pyRegRep4.utils`)

```python
deep_get(data: dict, *keys, default=None)
```

Безпечно дістає значення з вкладеного `dict` за послідовністю ключів.

| Параметр | Тип | Опис |
|----------|-----|------|
| `data` | `dict` | Джерело даних |
| `*keys` | `Any` | Шлях ключів для проходу по вкладеному словнику |
| `default` | `Any` | Значення за замовчуванням, якщо шлях не знайдено |

**Поведінка:**
- якщо на будь-якому кроці значення не є `dict` — повертається `default`
- якщо кінцеве значення `None` — повертається `default`
- якщо `keys` не передані — повертається `data`

```python
from pyRegRep4 import deep_get

data = {
    "doc": {
        "Procedure": [{"lang": "en", "value": "GetBirthCertificate"}]
    }
}

value = deep_get(data, "doc", "Procedure", 0, "value", default="n/a")
print(value)  # n/a (бо deep_get працює тільки з dict-ланцюжком)

procedure = deep_get(data, "doc", "Procedure", default=[])
print(procedure)  # [{"lang": "en", "value": "GetBirthCertificate"}]
```

---

### Клас `NS` (`pyRegRep4.NS`)

Базовий клас для управління RIM namespace. Надає метод `_tname(prefix, localname)` для генерування кваліфікованих імен тегів у нотації Clark.

---

### Виняток `ParsingError` (`pyRegRep4.RIMParsing`)

Базовий клас для помилок парсування. Кидається при некоректному XML або відсутньому namespace.

## Структура проекту

```
pyRegRep/
├── pyRegRep4/
│   ├── __init__.py          # Експорт: get_slot та типи слотів
│   ├── RIMElement.py        # Класи слотів + фабрика get_slot()
│   ├── RIMParsing.py        # Парсер Parsing + serialize()
│   ├── utils.py             # deep_get() для вкладених словників
│   └── NS.py                # Базовий клас для namespace
├── tests/
│   ├── conftest.py          # sys.path для CI
│   ├── test_rim_parsing.py  # Тести парсера
│   ├── test_rim_element.py  # Тести get_slot() та типів слотів
│   ├── test_utils.py        # Тести deep_get()
│   ├── EDM_Ferst_Request.xml
│   ├── EDM_Ferst_Response.xml
│   ├── EDM_Second_Request.xml
│   └── EDM_Second_Response.xml
├── example/
│   ├── Example_1.py
│   ├── example_anyvaluetype_usage.py
│   └── example_get_slot_usage.py
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Запуск тестів

```bash
# Встановлення залежностей
pip install lxml xmltodict pytest

# Усі тести
python -m pytest --disable-warnings -q

# Тільки тести парсера
python -m pytest tests/test_rim_parsing.py -v

# Тільки тести слотів
python -m pytest tests/test_rim_element.py -v
```

## Логування

Бібліотека використовує стандартний `logging`. Для увімкнення:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Технічні деталі

### Обробка просторів імен

Namespace витягуються автоматично з кореневого елемента документа та зберігаються у `parser._ns` у форматі `{prefix: uri}`.

### Формат `slots`

```python
{
    "doc": {
        "SpecificationIdentifier": ("StringValueType", "oots-edm:v1.2"),
        "IssueDateTime": ("DateTimeValueType", "2024-03-15T10:30:00"),
        "PossibilityForPreview": ("BooleanValueType", "false"),
    },
    "query": {},
    "exception": {},
    "object": {}
}
```

## Автор

**Andrey Shapovalov** — mt.andrey@gmail.com

## Ліцензія

MIT License — див. файл [LICENSE](LICENSE)

## Посилання

- [ebXML / Registry Information Model](https://en.wikipedia.org/wiki/ebXML)
- [OOTS EDM Specification](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/OOTS)
- [lxml Documentation](https://lxml.de/)
- [xmltodict](https://github.com/martinblech/xmltodict)

---

**Версія:** 12 · **Оновлено:** 2026-04-12

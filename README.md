# pyRegRep

Бібліотека Python для парсування та обробки XML документів у форматі RIM (Registry Information Model) / ebXML.

## Опис

**pyRegRep** - це інструмент для роботи з XML документами, що відповідають стандарту Registry Information Model (RIM), який часто використовується в системах eGovernment та обміну даними. Бібліотека дозволяє легко витягувати, аналізувати та серіалізувати дані з RIM/ebXML документів.

## Можливості

- ✅ Парсування RIM/ebXML XML документів
- ✅ Автоматична обробка просторів імен (namespaces)
- ✅ Витягування запитів (Query), винятків (Exception) та об'єктів реєстру (RegistryObject)
- ✅ Обробка різних типів значень (Boolean, String, Collection, International String, Any Value)
- ✅ Серіалізація даних у зручний Python формат (dict)
- ✅ Підтримка складних структур даних та вкладених колекцій

## Вимоги

- **Python**: >= 3.10
- **Залежності**: 
  - `lxml >= 5.2.1` - для роботи з XML

## Установка

### З PyPI (якщо опубліковано)

```bash
pip install pyRegRep
```

### З локального источника

```bash
pip install -e .
```

Або через requirements.txt:

```bash
pip install -r requirements.txt
```

## Швидкий старт

### Базовий приклад

```python
from pyRegRep4.RIMParsing import Parsing

# Прочитайте XML файл
with open("document.xml", "rb") as f:
    xml_data = f.read()

# Створіть об'єкт парсера
parser = Parsing(xml_data)

# Отримайте дані
print(parser.slots)  # Словник всіх витягнутих даних
print(parser.serialize())  # Серіалізовані та очищені дані
```

### Робота з запитами та винятками

```python
from pyRegRep4.RIMParsing import Parsing

with open("document.xml", "rb") as f:
    parser = Parsing(f.read())

# Отримайте елементи документа
if parser.query is not None:
    print("Знайдено Query елемент")

if parser.exception is not None:
    print("Знайдено Exception елемент")

# Отримайте об'єкти реєстру
print(f"Всього об'єктів реєстру: {len(parser.objects)}")
```

## API Довідник

### Клас `Parsing`

#### Конструктор

```python
Parsing(doc: bytes)
```

**Параметри:**
- `doc` (bytes): Бінарні дані XML документа

**Атрибути:**
- `xml` (str): XML як рядок
- `doc` (etree._Element): Розібраний XML документ
- `query` (etree._Element | None): Елемент Query з документа (якщо є)
- `exception` (etree._Element | None): Елемент Exception з документа (якщо є)
- `objects` (list): Список всіх RegistryObject елементів
- `slots` (dict): Словник всіх витягнутих Slot елементів з типами

#### Методи

**`serialize() -> dict`**

Серіалізує витягнені дані, перетворюючи типи значень:
- `BooleanValueType` → `bool`
- `StringValueType` → `str`
- `CollectionValueType` → `list`
- `InternationalStringValueType` → `list[dict]`
- `AnyValueType` → `XML Element`

**Повернення:** Словник серіалізованих даних

## Приклад використання

```python
from pyRegRep4.RIMParsing import Parsing

# Завантаження XML
with open("EDM_Response.xml", "rb") as f:
    data = f.read()

# Парсування
parser = Parsing(data)

# Отримання структурованих даних
slots = parser.serialize()

# Ітерація по даних
for key, value in slots.items():
    print(f"{key}: {value}")
```

## Структура проекту

```
pyRegRep/
├── pyRegRep4/
│   ├── __init__.py
│   └── RIMParsing.py       # Основна логіка парсування
├── tests/
│   ├── test_parsing_1.py    # Тести парсування
│   ├── EDM_Ferst_Request.xml
│   ├── EDM_Ferst_Response.xml
│   ├── EDM_Second_Request.xml
│   └── EDM_Second_Response.xml
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Запуск тестів

```bash
cd tests
python Example_1.py
```

## Логування

Бібліотека використовує модуль `logging` Python. Для включення логування:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Технічні деталі

### Обробка просторів імен

Бібліотека автоматично розпізнає та обробляє всі простори імен (namespaces) у XML документі:
- Простір імен за замовчуванням позначається як `"default"`
- Інші простори імен зберігаються під своїми префіксами

### Типи значень RIM

Підтримуються наступні типи значень:
- **BooleanValueType** - логічні значення
- **StringValueType** - текстові значення
- **IntegerValueType** - цілі числа
- **CollectionValueType** - колекції значень
- **InternationalStringValueType** - багатомовні рядки
- **AnyValueType** - будь-які XML елементи

## Автор

- **Andrey Shapovalov** (mt.andrey@gmail.com)

## Ліцензія

MIT License - див. файл [LICENSE](LICENSE)

## Подяки

Проект використовує бібліотеку [lxml](https://lxml.de/) для роботи з XML.

## Посилання

- [Registry Information Model (RIM)](https://en.wikipedia.org/wiki/ebXML)
- [lxml Documentation](https://lxml.de/)

---

**Версія:** 5.0.1  
**Останнє оновлення:** 2026


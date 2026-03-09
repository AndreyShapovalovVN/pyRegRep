#!/usr/bin/env python
"""
Приклад використання AnyValueType серіалізації з параметром any_type.

Демонструє обидва режими: Element (за замовчуванням) та dict (з any_type=True).
"""

from pathlib import Path
from pyRegRep4.RIMParsing import Parsing
from lxml import etree
import json


def example_default_mode():
    """Приклад 1: Режим за замовчуванням (повертає Element)."""
    print("=" * 60)
    print("Приклад 1: Режим за замовчуванням (any_type=False)")
    print("=" * 60)

    xml_file = Path("../tests/EDM_Ferst_Request.xml")
    if not xml_file.exists():
        print(f"Файл {xml_file} не знайдено")
        return

    doc = Parsing(xml_file.read_bytes())

    # За замовчуванням - повертає Element
    serialized = doc.serialize()  # або doc.serialize(any_type=False)

    evidence_provider = serialized["doc"].get("EvidenceProvider")
    print(f"\nТип EvidenceProvider: {type(evidence_provider)}")
    print(f"Це lxml Element?: {isinstance(evidence_provider, etree._Element)}")

    if evidence_provider is not None:
        print(f"Tag: {evidence_provider.tag}")
        print(f"Дочірні елементи: {len(evidence_provider)}")


def example_serialized_mode():
    """Приклад 2: Режим серіалізації (any_type=True, повертає dict)."""
    print("\n" + "=" * 60)
    print("Приклад 2: Режим серіалізації (any_type=True)")
    print("=" * 60)

    xml_file = Path("../tests/EDM_Ferst_Request.xml")
    if not xml_file.exists():
        print(f"Файл {xml_file} не знайдено")
        return

    doc = Parsing(xml_file.read_bytes())

    # З any_type=True - повертає dict
    serialized = doc.serialize(any_type=True)

    evidence_provider = serialized["doc"].get("EvidenceProvider")
    print(f"\nТип EvidenceProvider: {type(evidence_provider)}")
    print(f"Це dict?: {isinstance(evidence_provider, dict)}")

    if evidence_provider is not None:
        print(f"\nКлючі: {list(evidence_provider.keys())}")
        print("\nПримерна структура:")
        print(json.dumps(evidence_provider, indent=2, ensure_ascii=False)[:500] + "...")


def example_collection_mode():
    """Приклад 3: CollectionValueType з AnyValueType в обох режимах."""
    print("\n" + "=" * 60)
    print("Приклад 3: CollectionValueType з AnyValueType")
    print("=" * 60)

    xml_file = Path("../tests/EDM_Ferst_Request.xml")
    if not xml_file.exists():
        print(f"Файл {xml_file} не знайдено")
        return

    doc = Parsing(xml_file.read_bytes())

    print("\n--- Режим за замовчуванням (Element) ---")
    serialized_default = doc.serialize(any_type=False)
    requirements_default = serialized_default["doc"].get("Requirements", [])
    print(f"Кількість вимог: {len(requirements_default)}")
    if requirements_default:
        print(f"Тип першої вимоги: {type(requirements_default[0])}")
        print(f"Це Element?: {isinstance(requirements_default[0], etree._Element)}")

    print("\n--- Режим серіалізації (dict) ---")
    serialized_dict = doc.serialize(any_type=True)
    requirements_dict = serialized_dict["doc"].get("Requirements", [])
    print(f"Кількість вимог: {len(requirements_dict)}")
    if requirements_dict:
        print(f"Тип першої вимоги: {type(requirements_dict[0])}")
        print(f"Це dict?: {isinstance(requirements_dict[0], dict)}")
        if isinstance(requirements_dict[0], dict):
            print(f"Ключі: {list(requirements_dict[0].keys())}")


def example_object_slots():
    """Приклад 4: AnyValueType в RegistryObject слотах."""
    print("\n" + "=" * 60)
    print("Приклад 4: AnyValueType в об'єктах реєстру")
    print("=" * 60)

    xml_file = Path("../tests/EDM_Second_Response.xml")
    if not xml_file.exists():
        print(f"Файл {xml_file} не знайдено")
        return

    doc = Parsing(xml_file.read_bytes())

    # Серіалізація з any_type=True
    serialized = doc.serialize(any_type=True)

    object_slots = serialized.get("object", {})
    print(f"\nСлоти в об'єктах: {list(object_slots.keys())}")

    for slot_name, slot_value in object_slots.items():
        if isinstance(slot_value, dict):
            print(f"\n{slot_name}:")
            print("  Тип: dict")
            print(f"  Ключі: {list(slot_value.keys())[:3]}...")


def example_consistency():
    """Приклад 5: Консистентність викликів."""
    print("\n" + "=" * 60)
    print("Приклад 5: Консистентність викликів serialize()")
    print("=" * 60)

    xml_file = Path("../tests/EDM_Ferst_Request.xml")
    if not xml_file.exists():
        print(f"Файл {xml_file} не знайдено")
        return

    doc = Parsing(xml_file.read_bytes())

    # Кілька викликів з any_type=True
    result1 = doc.serialize(any_type=True)
    result2 = doc.serialize(any_type=True)

    print(f"\nРезультати ідентичні?: {result1 == result2}")
    print(f"Результати - один об'єкт?: {result1 is result2}")

    # Переключення між режимами не впливає на консистентність
    result3 = doc.serialize(any_type=True)

    print(f"Після переключення режимів результати ще ідентичні?: {result2 == result3}")


if __name__ == "__main__":
    try:
        example_default_mode()
        example_serialized_mode()
        example_collection_mode()
        example_object_slots()
        example_consistency()

        print("\n" + "=" * 60)
        print("✅ Усі приклади успішно виконані!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()


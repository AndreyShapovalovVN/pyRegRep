from lxml import etree

NS_MAP = {
    'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:4.0',
    'xsi': 'https://www.w3.org',
    'xlink': 'https://www.w3.org'
}


class RegRepSlot:
    def __init__(self, name, value_type, value):
        self.name = name
        self.value_type = value_type
        self.value = value

    def to_xml(self):
        # Створюємо базовий елемент Slot
        slot = etree.Element(f"{{{NS_MAP['rim']}}}Slot", name=self.name)

        # Створюємо SlotValue з типом
        slot_value = etree.SubElement(slot, f"{{{NS_MAP['rim']}}}SlotValue")
        slot_value.set(f"{{{NS_MAP['xsi']}}}type", f"rim:{self.value_type}")

        self._process_content(slot_value, self.value_type, self.value)
        return slot

    def to_xml_bytes(self):
        return etree.tostring(self.to_xml(), pretty_print=True)

    def _process_content(self, parent_el, v_type, v_data):
        if v_type == 'CollectionValueType' and isinstance(v_data, list):
            for item in v_data:
                # Очікуємо кортеж (тип, значення) для елементів колекції
                sub_type, sub_val = item
                elem = etree.SubElement(parent_el, f"{{{NS_MAP['rim']}}}Element")
                elem.set(f"{{{NS_MAP['xsi']}}}type", f"rim:{sub_type}")
                self._process_content(elem, sub_type, sub_val)

        elif v_type == 'AnyValueType' and isinstance(v_data, etree._Element):
            # Якщо це вже готовий XML-об'єкт (наприклад, Agent)
            parent_el.append(v_data)

        elif v_type == 'InternationalStringValueType' and isinstance(v_data, list):
            for item in v_data:
                if isinstance(item, dict):
                    etree.SubElement(parent_el, f"{{{NS_MAP['rim']}}}LocalizedString",
                                     attrib={
                                         f"{{{NS_MAP['xsi']}}}lang": item.get('lang'),
                                         'value': item.get('sub_value')
                                     })

        else:
            # Для StringValueType, DateTimeValueType тощо
            v_inner = etree.SubElement(parent_el, f"{{{NS_MAP['rim']}}}Value")
            v_inner.text = str(v_data)

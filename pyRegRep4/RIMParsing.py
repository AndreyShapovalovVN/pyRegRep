import logging

from lxml import etree

_logger = logging.getLogger(__name__)


class Parsing:
    def __init__(self, doc: bytes):
        parser = etree.XMLParser(remove_comments=True)
        self.doc = etree.fromstring(doc, parser)
        self._ns = {}
        for perfix, uri in self.doc.nsmap.items():
            if perfix is None:
                perfix = "default"
            self._ns.update({perfix: uri})
        self.query = self.doc.find(".//query:Query", namespaces=self._ns)
        self.exception = self.doc.find(".//rs:Exception", namespaces=self._ns)
        self.objects = self.doc.findall(".//rim:RegistryObject", namespaces=self._ns)
        self.slots = self.__list_slots()

    def __tname(self, ns: str, tag: str) -> str:
        if not ns:
            return tag
        return f"{{{self._ns[ns]}}}{tag}"

    def __slot(self, name: str) -> etree._Element | None:
        slot = self.doc.find(f".//rim:Slot[@name='{name}']", namespaces=self._ns)
        if slot is None:
            return None
        return slot

    def __value(self, slot: etree._Element):
        slot = slot[0]
        type_ = slot.get(self.__tname("xsi", "type"), '').split(":")[1].strip()  #

        if "AnyValueType" in type_:
            return type_, slot[0]

        elif "InternationalStringValueType" in type_:
            values = []
            for i, item in enumerate(list(slot[0])):
                value = {
                    "lang": item.get(self.__tname("xsi", "lang")),
                    "value": item.get("value"),
                }
                values.append(value)
            return type_, values

        elif "CollectionValueType" in type_:
            values = []
            for i, item in enumerate(list(slot)):
                wrapper = etree.Element("wrapper")
                wrapper.append(item)
                values.append(self.__value(wrapper))
            return type_, values
        else:
            return type_, slot[0].text

    def __list_slots(self) -> dict[str, tuple[str, str]]:
        edm: dict = {"doc": {}, "query": {}, "exception": {}, "object": {}}
        for slot in list(self.doc):
            if slot.tag == self.__tname("rim", "Slot"):
                name = slot.get("name")
                edm["doc"].update({name: (self.__value(slot))})
                continue
            elif slot.tag == self.__tname("query", "Query"):
                for query in list(slot):
                    name = query.get("name")
                    edm["query"].update({name: (self.__value(query))})
                continue
            elif slot.tag == self.__tname("rs", "Exception"):
                for exception in list(slot):
                    name = exception.get("name")
                    edm["exception"].update({name: (self.__value(exception))})
                continue
            elif slot.tag == self.__tname("rim", "RegistryObjectList"):
                for registryObject in list(slot):
                    ev = {}
                    for evidense in list(registryObject):
                        if evidense.tag == self.__tname("rim", "Slot"):
                            ev.update({evidense.get("name"): self.__value(evidense)})
                        if evidense.tag == self.__tname("rim", "RepositoryItemRef"):
                            ev.update(
                                {
                                    "RepositoryItemRef": {
                                        "xlink": evidense.get(
                                            self.__tname("xlink", "href")
                                        ),
                                        "title": evidense.get(
                                            self.__tname("xlink", "title")
                                        ),
                                    }
                                }
                            )
                    edm["object"].update(ev)
                continue
            else:
                continue

        return edm

    def serialize(self):
        def transform_data(data):
            if isinstance(data, list):
                return [transform_data(item) for item in data]

            elif isinstance(data, dict):
                return {k: transform_data(v) for k, v in data.items()}

            elif isinstance(data, tuple) and len(data) == 2:
                data_type, value = data

                if data_type == 'BooleanValueType':
                    return value.lower() == 'true'

                elif data_type == 'StringValueType':
                    return value.strip()

                elif data_type == 'CollectionValueType':
                    return transform_data(value)

                elif data_type == 'AnyValueType':
                    return value

                elif data_type == 'InternationalStringValueType':
                    return transform_data(value)

                # Якщо тип не підпав під умови, повертаємо значення як є
                return transform_data(value) if isinstance(value, (list, dict)) else value

            return data

        return transform_data(self.slots)
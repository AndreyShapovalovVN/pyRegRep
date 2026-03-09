from pyRegRep4.RIMParsing import Parsing
import logging

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)


files = [
    "./EDM_Ferst_Request.xml",
    "./EDM_Ferst_Response.xml",
    "./EDM_Second_Request.xml",
    "./EDM_Second_Response.xml",
]

xmls: list[dict[str, bytes]] = []

for file in files:
    with open(file, "rb") as f:
        d = {file[2:]: f.read()}
        xmls.append(d)

for xml in xmls:
    for key, value in xml.items():
        print("")
        print("=" * 100)
        print(key)
        print("-" * 100)
        edm = Parsing(value)
        print(edm.slots)
        print(edm.serialize())
        for k, v in edm.serialize().items():
            print(k, v)

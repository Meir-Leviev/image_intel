from pprint import pprint

from map_view import create_map
from extractor import extract_all , extract_metadata

content = extract_all("/Users/meirleviev/Desktop/PyCharm/image_intel/images/ready")

# html = create_map(content)
# with open("test2.html", "w") as h:
#     h.write(html)
pprint(content)
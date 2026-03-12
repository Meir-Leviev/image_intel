from map_view import create_map
from extractor import extract_all , extract_metadata

print(extract_metadata("/Users/meirleviev/Desktop/PyCharm/image_intel/images/sample_data/20230118_070716.jpg"))
# content = extract_all("/Users/meirleviev/Desktop/PyCharm/image_intel/images/sample_data")

# html = create_map(content)
# with open("test2.html", "w") as h:
#     h.write(html)
# print(content)
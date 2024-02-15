from pathlib import Path

import geopandas
from matplotlib import pyplot
from warg import flatten_mapping

from svaguely import parse_svg

svg_elements, _ = parse_svg(
    Path(__file__).parent.parent / "tests" / "fixtures" / "svaguely.svg"
)

svg_elements = flatten_mapping(svg_elements)

collected = []
texts = []
for element_name, element_shape in svg_elements.items():
    collected.append(element_shape.geometry)
    if "text" in element_shape.extras:
        texts.append(element_shape.extras["text"])
    else:
        texts.append(None)  # element_name)

frame = geopandas.GeoDataFrame({"label": texts, "geometry": collected})

frame["coords"] = frame["geometry"].apply(lambda x: x.representative_point().coords[:])
frame["coords"] = frame["geometry"].apply(lambda x: x.centroid.coords[:])
frame["coords"] = [coords[0] for coords in frame["coords"]]

print(frame)
frame.plot()

for idx, row in frame.iterrows():
    if row["label"]:
        pyplot.annotate(
            text=row["label"], xy=row["coords"], ha="center", va="center", size=20
        )

pyplot.show()

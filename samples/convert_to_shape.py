from warg import flatten_mapping, ensure_existence

from svaguely import parse_svg

exclude_dir = ensure_existence("exclude")
svg_file_name = "mapspeople.svg"

svg_elements, _ = parse_svg(exclude_dir / svg_file_name, output_space=1)

svg_elements = flatten_mapping(svg_elements)

collected = []

for ith, (element_name, element_shape) in enumerate(svg_elements.items()):
    collected.append(element_shape.geometry)

with open((exclude_dir / svg_file_name).with_suffix(".wkt"), "w") as f:
    for element in collected:
        f.write(element.wkt)

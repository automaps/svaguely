from itertools import count
from typing import Mapping

import svgelements


def convert_elements(group: svgelements.Group) -> Mapping:
  return_dict = {}
  name_counter = iter(count())

  for item in group:
    item_type = type(item)
    item_filled = False

    if hasattr(item, "fill"):
      if item.fill.value is not None:
        item_filled = True

    if hasattr(item, "id") and item.id:
      item_name = item.id
    else:
      item_name = f"NoName{next(name_counter)}"

    if isinstance(item, svgelements.Group):
      return_dict[item_name] = convert_elements(item)
      continue

    if hasattr(item, "values") and "class" in item.values.keys():
      item_value_class = item.values["class"]
    else:
      item_value_class = None

    if isinstance(item, svgelements.Rect):
      item_contents = rectangular_function(item)

    elif isinstance(item, svgelements.SimpleLine):
      item_contents = simpleline_function(item)

    elif isinstance(item, svgelements.Polyline):
      item_contents = polyline_function(item)

    elif isinstance(item, svgelements.Polygon):
      item_contents = polygon_function(item)
    elif isinstance(item, svgelements.Point):
      item_contents = point_function(item)
    elif isinstance(item, svgelements.Circle):
      if False:
        e = svgelements.Path(item)
        e = e.reify()
        item_contents = path_function(e)
      else:
        item_contents = circle_function(item)
    elif isinstance(item, svgelements.Ellipse):
      e = svgelements.Path(item)
      e_reified = e.reify()
      item_contents = path_function(e_reified)

    elif isinstance(item, svgelements.Path):
      item_contents = path_function(item)

    elif isinstance(item, svgelements.Text):
      continue
    else:
      print("Not supported class: {}".format(f"{item=} {type(item)}"))
      continue

    return_dict[item_name] = FloorPlanGeometry(
      item_contents, item_value_class, item_type, item_filled
    )

  return return_dict

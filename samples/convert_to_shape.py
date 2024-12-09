import logging
from pathlib import Path

from warg import flatten_mapping

from svaguely import parse_svg

svg_file_name = (
    Path.home() / "Downloads" / "Monticello_Siteplan_Ver_01_TOURGUIDE_202303091.svg"
)

svg_elements, _ = parse_svg(svg_file_name, output_space=1)

svg_elements = flatten_mapping(svg_elements)

logger = logging.getLogger(__name__)

for ith, (element_unique_id, element) in enumerate(svg_elements.items()):
    logger.warning(element_unique_id)
    # logger.warning(element)

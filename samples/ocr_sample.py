from collections import namedtuple
from pathlib import Path
from typing import Mapping

import numpy
import shapely

from samples.recognition import run_ocr_no_cluster
from mi_companion.submodules.svaguely.svaguely.rendering import render_svg

detection = namedtuple("detection", ("text", "left", "bottom", "right", "top", "page"))
detection_shapely = namedtuple("detection_shapely", ("text", "polygon"))


def horizontal_cluster(rendered_image_path: Path, detections: Mapping) -> None:
    import cv2

    clusters = {}

    detection_tuples = [detection(*a) for a in zip(*detections.values())]
    detection_boxes = [
        detection_shapely(
            dt.text,
            shapely.Polygon.from_bounds(dt.left, dt.bottom, dt.right, dt.top),
        )
        for dt in detection_tuples
    ]

    img = cv2.imread(str(rendered_image_path))

    yx_max = numpy.array((img.shape)).round().astype(numpy.int32)[:2]

    for t, p in detection_boxes:
        coords = []
        asad = numpy.array(p.exterior.coords).round().astype(numpy.int32)
        asad[:, 1] = yx_max[1] - asad[:, 1] - 323  # WHAT? constant

        coords.append(asad)

        cv2.polylines(img, coords, isClosed=True, color=(0, 255, 0))

    cv2.imshow("img", img)
    cv2.waitKey(0)


# b = polygon_geom.bounds
# Find the NW corner of bounds (minx, maxy)
# nw_corner = (b[0], b[3])

rendered_img_path = render_svg(
    Path.home() / "Downloads" / "Cross_Creek_Siteplan_TOURGUIDE_230421.svg"
)

print(horizontal_cluster(rendered_img_path, run_ocr_no_cluster(rendered_img_path)))

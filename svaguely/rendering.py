from pathlib import Path

from bs4 import BeautifulSoup

try:
    import Image
except ImportError:
    from PIL import Image

import logging

logger = logging.getLogger(__name__)


def render_svg(svg_path: Path, inclusion_filter=("label", "number", "text")):
    import cairosvg

    filtered_path = svg_path.parent / f"{'_'.join(inclusion_filter)}.svg"

    root = BeautifulSoup(open(svg_path).read(), features="xml")
    svg_group_element = "g"

    new_root = root.find(svg_group_element)
    for item in new_root.find_all(
        svg_group_element,
        # recursive=True
    ):
        if hasattr(item, "attrs") and item.attrs:
            if "id" in item.attrs:
                item_id = item.attrs["id"].strip().lower()

                keep = False
                for inc_test in inclusion_filter:
                    if inc_test in item_id:
                        keep = True

                if not keep:
                    logger.info(f"Decomposing {item_id}")
                    item.decompose()

    with open(filtered_path, "w") as o:
        o.write(root.prettify())

    target_png = filtered_path.with_suffix(".png")

    with open(filtered_path) as svg:
        with open(target_png, "wb") as f:
            cairosvg.svg2png(
                bytestring=svg.read(),
                write_to=f,
                # dpi=1
            )

    logger.info(f"Wrote filtered PNG to {target_png}")

    return target_png


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    render_svg(Path.home() / "Downloads" / "Cross_Creek_Siteplan_TOURGUIDE_230421.svg")

    render_svg(
        Path.home() / "Downloads" / "Cross_Creek_Siteplan_TOURGUIDE_230421.svg",
        inclusion_filter=("furniture",),
    )

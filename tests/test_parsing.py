from pathlib import Path

from svaguely import parse_svg


def test_string_parse():
    from .fixtures import svg_snippets

    print(parse_svg(svg_snippets.svaguely_logo))


def test_file_parse():
    print(parse_svg(Path(__file__).parent / "fixtures" / "svaguely.svg"))


def test_file_parse_use():
    print(parse_svg(Path(__file__).parent / "fixtures" / "svg_logo.svg"))


def test_file_parse_use_2():
    print(parse_svg(Path(__file__).parent / "fixtures" / "test_chair.svg"))


def test_file_parse_single_path():
    print(parse_svg(Path.home() / "Downloads" / "ricoh-logo-2005-neu.svg"))

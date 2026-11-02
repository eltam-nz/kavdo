import pytest


@pytest.mark.parametrize(
    "text",
    ["plain", "two\nlines", "back\\slash", "trailing\\", "\\n literal", "a\\\nb", ""],
)
def test_escape_round_trips(app, text):
    escaped = app.escape(text)
    assert "\n" not in escaped
    assert app.unescape(escaped) == text


def test_clean_joins_lines_and_strips(app):
    assert app.clean("  Site\tvisit\nnotes  ") == "Site visit notes"


def test_clean_task_keeps_inner_line_breaks(app):
    assert app.clean_task("\n\n first\r\nsecond\t \r\n\n") == " first\nsecond"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10,20,300,400", (10, 20, 300, 400)),
        ("300x400+10+20", (10, 20, 300, 400)),
        ("garbage", None),
        ("1,2,3", None),
    ],
)
def test_parse_geometry(app, value, expected):
    assert app.parse_geometry(value) == expected

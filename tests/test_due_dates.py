from datetime import date

import pytest

# A Monday, so weekday maths is easy to read.
MON = date(2026, 3, 2)


@pytest.fixture(autouse=True)
def _frozen(today):
    today(MON)


@pytest.mark.parametrize(
    ("text", "expected_text", "expected_due"),
    [
        ("Call Bob today", "Call Bob", "2026-03-02"),
        ("Call Bob tomorrow", "Call Bob", "2026-03-03"),
        ("Call Bob tmr.", "Call Bob", "2026-03-03"),
        ("Call Bob due fri", "Call Bob", "2026-03-06"),
        ("Call Bob mon", "Call Bob", "2026-03-02"),          # today counts
        ("Call Bob next mon", "Call Bob", "2026-03-09"),
        ("Call Bob eow", "Call Bob", "2026-03-06"),
        ("Call Bob eom", "Call Bob", "2026-03-31"),
        ("Call Bob next week", "Call Bob", "2026-03-09"),
        ("Call Bob in 3 days", "Call Bob", "2026-03-05"),
        ("Call Bob in 2 weeks", "Call Bob", "2026-03-16"),
        ("Call Bob 2026-04-01", "Call Bob", "2026-04-01"),
        ("Call Bob 15 apr", "Call Bob", "2026-04-15"),
        ("Call Bob apr 15th", "Call Bob", "2026-04-15"),
        ("Call Bob 20/3", "Call Bob", "2026-03-20"),         # NZ day/month
        ("Call Bob by 5/4", "Call Bob", "2026-04-05"),
        ("Call Bob 5/4/27", "Call Bob", "2027-04-05"),
    ],
)
def test_due_from_text_recognises(app, text, expected_text, expected_due):
    assert app.due_from_text(text) == (expected_text, expected_due)


@pytest.mark.parametrize(
    "text",
    [
        "tomorrow",               # nothing left once the date is removed
        "Mix ratio 3/4",          # ambiguous d/m without a cue word
        "Check cl 4.2",           # clause numbers are not dates
        "Review NZS 3404",
        "Call Bob 31/2",          # not a real date
        "Tomorrow call Bob",      # only the end of the task is looked at
    ],
)
def test_due_from_text_leaves_alone(app, text):
    assert app.due_from_text(text) == (text, None)


def test_yearless_date_picks_nearest_year(app, today):
    today(date(2026, 12, 20))
    assert app.due_from_text("Pay rent by 3/1")[1] == "2027-01-03"
    today(date(2026, 10, 15))
    assert app.due_from_text("Pay rent by 2/9")[1] == "2026-09-02"  # recent past = overdue


def test_next_monday_on_sunday_skips_tomorrow(app, today):
    today(date(2026, 3, 8))  # Sunday
    assert app.next_monday() == date(2026, 3, 16)


def test_due_text_labels(app):
    assert app.due_text("2026-03-02") == ("Due today", 0)
    assert app.due_text("2026-03-03") == ("Due tomorrow", 1)
    assert app.due_text("2026-03-01") == ("Overdue, yesterday", -1)
    assert app.due_text("not a date") == (None, 0)


def test_parse_task_shortcuts_combines_everything(app):
    groups = ["General", "Tiwai Point"]
    for text in ("RFI #tiwai tmr !!", "RFI #tiwai !! tmr", "RFI @TiwaiPoint urgent tomorrow"):
        assert app.parse_task_shortcuts(text, groups) == ("RFI", "2026-03-03", True, "Tiwai Point")


def test_ambiguous_group_tag_is_left_as_text(app):
    text, _due, _star, group = app.parse_task_shortcuts("Do #T thing", ["Tiwai", "Taupo"])
    assert group is None
    assert text == "Do #T thing"

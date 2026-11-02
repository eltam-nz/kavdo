"""The Home tab: which dated tasks it lists, in what order, and the view itself."""
from datetime import date

import pytest


def _t(text, due=None, star=False, done=False):
    t = {"text": text, "done": done, "group": "General"}
    if due:
        t["due"] = due
    if star:
        t["star"] = True
    return t


# ---------- dated_tasks (pure) ----------

def test_orders_by_due_date_overdue_first(app):
    tabs = [(0, "Work", [("General", [
        _t("later", "2026-03-20"), _t("overdue", "2026-02-01"), _t("soon", "2026-03-03")])])]
    assert [e["text"] for e in app.dated_tasks(tabs)] == ["overdue", "soon", "later"]


def test_same_date_starred_first_then_tab_group_position(app):
    tabs = [
        (5, "Work", [("General", [_t("w-gen-1", "2026-03-03"), _t("w-gen-2", "2026-03-03")]),
                     ("Site", [_t("w-site", "2026-03-03")])]),
        (2, "Home", [("General", [_t("h-starred", "2026-03-03", star=True),
                                  _t("h-plain", "2026-03-03")])]),
    ]
    assert [e["text"] for e in app.dated_tasks(tabs)] == [
        "h-starred", "w-gen-1", "w-gen-2", "w-site", "h-plain"]


def test_skips_undated_done_and_invalid_dates(app):
    tabs = [(0, "Work", [("General", [
        _t("no date"), _t("done", "2026-03-03", done=True), _t("bad", "soon"),
        _t("kept", "2026-03-03")])])]
    assert [e["text"] for e in app.dated_tasks(tabs)] == ["kept"]


def test_entries_say_where_the_task_lives(app):
    tabs = [(7, "Projects", [("General", [_t("x")]), ("Lincoln", [_t("a"), _t("b", "2026-04-01")])])]
    (entry,) = app.dated_tasks(tabs)
    assert entry == {"text": "b", "due": "2026-04-01", "star": False,
                     "tabid": 7, "tab": "Projects", "group": "Lincoln", "index": 1}


def test_no_tabs_no_entries(app):
    assert app.dated_tasks([]) == []


# ---------- the real window, headless ----------

@pytest.fixture
def qapp(app):
    from PySide6.QtWidgets import QApplication
    qa = QApplication.instance() or QApplication([])
    app.set_scale(1.0)
    yield qa
    for w in list(app.WINDOWS):
        w.quitting = True
        w.hide()
        w.deleteLater()
    app.WINDOWS.clear()
    app.DELETED_TABS.clear()
    qa.processEvents()


@pytest.fixture
def two_windows(app, qapp, data_dir, today):
    """Window A: tabs 0 (Work, open) and 1 (Site). Window B: tab 2 (Admin)."""
    today(date(2026, 3, 2))
    tabs = {
        0: app._empty_tab("Work", "#2f6f73"),
        1: app._empty_tab("Site", "#7a4f9a"),
        2: app._empty_tab("Admin", "#9a4f4f"),
    }
    tabs[0]["groups"] = [["General", [_t("undated"), _t("w-later", "2026-03-20")]],
                         ["Lincoln", [_t("w-lincoln", "2026-03-03")]]]
    tabs[0]["folded"] = {"Lincoln"}
    tabs[1]["groups"] = [["General", [_t("s-overdue", "2026-02-27")]]]
    tabs[2]["groups"] = [["General", [_t("a-today", "2026-03-02", star=True)]]]
    app.TAB_ID_COUNTER[0] = 3
    wa = app.Window(win_state={"geometry": None, "zoomed": False, "pinned": False,
                               "tabs": [0, 1], "active": 0}, tabs_state=tabs)
    wb = app.Window(win_state={"geometry": None, "zoomed": False, "pinned": False,
                               "tabs": [2], "active": 2}, tabs_state=tabs)
    for w in (wa, wb):
        w.load_board()
    return wa, wb


def _rows(win):
    from PySide6.QtCore import Qt
    return [win.home.item(i).data(Qt.UserRole)["text"] for i in range(win.home.count())]


def test_home_lists_every_window_most_urgent_first(app, two_windows):
    wa, _wb = two_windows
    wa.show_home()
    assert wa.home_active and wa.home.isVisibleTo(wa) and not wa.scroll.isVisibleTo(wa)
    assert _rows(wa) == ["s-overdue", "a-today", "w-lincoln", "w-later"]
    assert wa.active_tab == 0            # the open tab is untouched underneath


def test_clicking_a_tab_leaves_home(app, two_windows):
    wa, _wb = two_windows
    wa.show_home()
    wa.switch_tab(0)                     # the tab that was open underneath
    assert not wa.home_active and wa.scroll.isVisibleTo(wa)
    wa.show_home()
    wa.switch_tab(1)
    assert not wa.home_active and wa.active_tab == 1


def test_open_task_jumps_to_tab_unfolds_and_selects(app, two_windows):
    wa, _wb = two_windows
    wa.show_home()
    entry = next(e for e in app.dated_tasks(app.all_tabs_in_order())
                 if e["text"] == "w-lincoln")
    app.open_task(entry)
    assert not wa.home_active and wa.active_tab == 0
    lincoln = wa.board.group_named("Lincoln")
    assert not lincoln.folded
    assert [c.task["text"] for c in wa.board.selected_cards()] == ["w-lincoln"]


def test_open_task_in_another_window(app, two_windows):
    wa, wb = two_windows
    wa.show_home()
    entry = next(e for e in app.dated_tasks(app.all_tabs_in_order()) if e["text"] == "a-today")
    app.open_task(entry)
    assert [c.task["text"] for c in wb.board.selected_cards()] == ["a-today"]
    assert wa.home_active                # window A stays on Home


def test_home_updates_after_a_change_and_saving_is_unaffected(app, two_windows, data_dir):
    wa, wb = two_windows
    assert app.global_save()
    before = (data_dir / "TodoList.txt").read_text(encoding="utf-8")
    wa.show_home()
    assert app.global_save()
    assert (data_dir / "TodoList.txt").read_text(encoding="utf-8") == before
    card = wb.board.open_cards()[0]
    wb.board.set_due([card], "2026-02-01")
    app.global_save()
    assert _rows(wa)[0] == "a-today"     # now the most overdue


def test_undo_does_nothing_on_home(app, two_windows):
    wa, _wb = two_windows
    wa.board.set_due([wa.board.open_cards()[0]], "2026-03-05")
    depth = len(wa.history)
    wa.show_home()
    wa.undo()
    assert len(wa.history) == depth

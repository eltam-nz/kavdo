"""TodoList.txt is the user's only copy of their tasks - guard its format."""


def _sample_state(app):
    tab = {
        "name": "Work",
        "colour": "#2f6f73",
        "collapsed": False,
        "folded": {"Later"},
        "colours": {"Later": "#ff8800"},
        "groups": [
            ["General", [
                {"text": "Plain task", "done": False, "group": "General"},
                {"text": "Two\nlines \\ slash", "done": False, "group": "General",
                 "star": True, "due": "2026-03-05", "files": ["a.msg", "b.pdf"]},
            ]],
            ["Later", [{"text": "Someday", "done": False, "group": "Later"}]],
        ],
        "done": [{"text": "Finished", "done": True, "group": "Later",
                  "doneat": "2026-03-01"}],
    }
    windows = [{"geometry": (10, 20, 400, 560), "zoomed": False, "pinned": True,
                "tabs": [0], "active": 0}]
    return windows, {0: tab}


def _save(app, windows, tabs):
    return app.save_app_state(windows, tabs, scale=1.25, autoarchive=14, tint=0.5,
                              next_tab_id=1, topbar_colour="#202225")


def test_missing_file_gives_default_state(app, data_dir):
    state = app.load_app_state()
    assert len(state["windows"]) == 1
    assert state["tabs"][0]["name"] == "Work"


def test_save_then_load_round_trips(app, data_dir):
    windows, tabs = _sample_state(app)
    assert _save(app, windows, tabs) is True

    state = app.load_app_state()
    assert state["ok"] and not state["partial"]
    assert state["scale"] == 1.25
    assert state["autoarchive"] == 14
    assert state["windows"][0]["geometry"] == (10, 20, 400, 560)
    assert state["windows"][0]["pinned"] is True

    tab = state["tabs"][0]
    assert tab["folded"] == {"Later"}
    assert tab["colours"] == {"Later": "#ff8800"}
    groups = dict((name, tasks) for name, tasks in tab["groups"])
    assert [t["text"] for t in groups["General"]] == ["Plain task", "Two\nlines \\ slash"]
    rich = groups["General"][1]
    assert rich["star"] is True
    assert rich["due"] == "2026-03-05"
    assert rich["files"] == ["a.msg", "b.pdf"]
    assert [(t["text"], t["group"], t["doneat"]) for t in tab["done"]] == [
        ("Finished", "Later", "2026-03-01")]


def test_saving_twice_keeps_a_backup(app, data_dir):
    windows, tabs = _sample_state(app)
    _save(app, windows, tabs)
    tabs[0]["groups"][0][1].append({"text": "New", "done": False, "group": "General"})
    _save(app, windows, tabs)
    assert (data_dir / "TodoList.txt.bak").exists()
    assert "New" not in (data_dir / "TodoList.txt.bak").read_text(encoding="utf-8")
    assert not list(data_dir.glob("*.tmp"))


def test_legacy_v2_file_is_upgraded_into_one_tab(app, data_dir):
    (data_dir / "TodoList.txt").write_text(
        "#format=2\n#window=10,20,300,400\n[General]\n0\tOld task\n[Site]\n1\tDone one\n",
        encoding="utf-8")
    state = app.load_app_state()
    tab = state["tabs"][0]
    assert tab["name"] == "Work"
    assert [t["text"] for t in tab["groups"][0][1]] == ["Old task"]
    assert [t["text"] for t in tab["done"]] == ["Done one"]
    assert state["windows"][0]["geometry"] == (10, 20, 300, 400)


def test_malformed_lines_are_skipped_not_fatal(app, data_dir):
    (data_dir / "TodoList.txt").write_text(
        "#format=3\n#scale=oops\n#tab=0,Work\n[0/General]\n0\tKept\n", encoding="utf-8")
    state = app.load_app_state()
    assert state["partial"] is True
    assert [t["text"] for t in state["tabs"][0]["groups"][0][1]] == ["Kept"]
    assert (data_dir / "TodoError.log").exists()

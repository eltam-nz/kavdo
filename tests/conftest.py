"""Shared test setup.

The app is a single ``TodoList.pyw`` script (not an importable package), so
it is loaded here by path. Importing it does not start the GUI or touch the
single-instance mutex - both only happen under ``if __name__ == "__main__"``.
"""
import importlib.machinery
import importlib.util
import os
import sys
from datetime import date as _real_date
from pathlib import Path

import pytest

# Let Qt load without a display (CI / headless Linux).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "TodoList.pyw"


def _load_app():
    loader = importlib.machinery.SourceFileLoader("todolist", str(APP_FILE))
    spec = importlib.util.spec_from_loader("todolist", loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules["todolist"] = module
    loader.exec_module(module)
    return module


_APP = _load_app()


@pytest.fixture
def app():
    """The TodoList.pyw module."""
    return _APP


@pytest.fixture
def data_dir(app, tmp_path, monkeypatch):
    """Point every data file at a temp folder so tests never touch real tasks."""
    monkeypatch.setattr(app, "DATA_FILE", str(tmp_path / "TodoList.txt"))
    monkeypatch.setattr(app, "ERROR_LOG_FILE", str(tmp_path / "TodoError.log"))
    monkeypatch.setattr(app, "ARCHIVE_FILE", str(tmp_path / "TodoArchive.txt"))
    monkeypatch.setattr(app, "ATTACH_DIR", str(tmp_path / "TodoAttachments"))
    return tmp_path


@pytest.fixture
def today(app, monkeypatch):
    """Freeze date.today() inside the app. Call with a date to set it."""

    def _freeze(fixed):
        class FrozenDate(_real_date):
            @classmethod
            def today(cls):
                return fixed

        monkeypatch.setattr(app, "date", FrozenDate)
        return fixed

    return _freeze

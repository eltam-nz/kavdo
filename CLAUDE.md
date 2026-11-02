# Notes for Claude

- Single-file PySide6 app: `TodoList.pyw` (~7.5k lines). Windows-only at runtime
  (ctypes/user32, AutoHotkey launcher), but imports headless for tests.
- Run `python -m pytest` and `ruff check .` before committing.
- Never commit user data (`TodoList.txt*`, `TodoArchive.txt`, `TodoAttachments/`,
  `TodoError.log`).
- `TodoList.txt` format changes must remain loadable from older files; add a
  test in `tests/test_storage.py` for any format change.
- Keep the existing code style; don't reformat unrelated code.
- `TodoLauncher.ahk` finds the window by the title "My Tasks" and sends custom
  messages 0x8012 (close) - keep these in sync if changed.

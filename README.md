# kavdo – desktop to-do list

A fast, keyboard-friendly to-do list for Windows in the style of Microsoft To Do,
built with PySide6. Press **F2** to open it, **F2** again to save and close.

Features include multiple windows and colour-coded tabs, groups, stars, due dates
typed in plain English (`Call Bob fri`, `RFI by 5/4 !!`), links to files and
folders, Outlook email/attachment drag-and-drop, an archive of completed tasks,
and undo (Ctrl+Z). The docstring at the top of `TodoList.pyw` describes the
behaviour in detail.

## Requirements

- Windows 10/11
- Python 3.12
- [AutoHotkey v2](https://www.autohotkey.com/) (for the F2 hotkey)

## Install

```powershell
py -3.12 -m pip install -r requirements.txt
```

Then run `TodoLauncher.ahk` (put a shortcut to it in `shell:startup` to have F2
available after every login). The launcher expects `TodoList.pyw` in the same
folder and uses `%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe`, falling
back to `pyw.exe`.

You can also start the app directly with `pythonw TodoList.pyw`.

## Where your data lives

Everything is stored as plain text **next to the script**:

| File / folder        | Contents                                  |
|----------------------|-------------------------------------------|
| `TodoList.txt`       | All windows, tabs, groups and tasks       |
| `TodoList.txt.bak`   | Previous save (last-known-good backup)    |
| `TodoArchive.txt`    | Archived completed tasks                  |
| `TodoAttachments/`   | Copied emails and files                   |
| `TodoError.log`      | Errors (a `.pyw` has no console)          |

These are personal data and are excluded by `.gitignore` – never commit them.

## Development

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pre-commit install

python -m pytest     # tests
ruff check .         # lint
```

Tests load `TodoList.pyw` by path and run headless (`QT_QPA_PLATFORM=offscreen`).
They cover the typed due-date/shortcut parsing and the `TodoList.txt` save/load
format, using temporary folders so they never touch real data.

### Workflow

1. Branch from `main` (`feature/<name>`, `fix/<name>`).
2. Make the change, add or update tests, and note it in `CHANGELOG.md`.
3. Open a pull request – CI runs lint and tests on Windows.
4. Merge once CI is green.

Changes to the `TodoList.txt` format must stay backward compatible: the loader
upgrades older files in place, and users' existing task lists must always load.

## Project layout

```
TodoList.pyw        the application (single file)
TodoLauncher.ahk    AutoHotkey v2 F2 launcher/toggle
TodoIcon.ico        window/tray icon
tests/              pytest suite
```

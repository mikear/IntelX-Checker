# AGENTS.md — IntelX Checker

## What this is

Python desktop app (PySide6/Qt GUI + CLI) that queries the Intelligence X API for data leak / OSINT investigations. All source lives in `src/`. The app runs from `src/main.py`.

## Run

```bash
# GUI mode (default)
python src/main.py

# CLI mode
python src/main.py --cli -s "search_term" -e json|csv|html|pdf -o exports/
```

No build step. No compile. Just run.

## Tests

```bash
# From repo root — tests import from src/ directly
cd src && python -m pytest ../tests/
```

Tests use `unittest`. `pytest` discovers them fine. Some tests hit the IntelX API (rate-limited, may fail without key).

## Key architecture

- `src/main.py` — entrypoint. Parses args, launches GUI (`gui.main()`) or CLI.
- `src/gui.py` — `MainWindow(QMainWindow)`. Search runs in a `QThread` via `AnalysisWorker` (QObject + signals).
- `src/api.py` — all IntelX API calls. `check_intelx()` returns `(success, data, search_id)`.
- `src/utils.py` — persistence (`load_history`, `save_history`, `merge_records`) and helpers. History stored in `data/history.json`.
- `src/exports.py` — CSV/JSON/HTML/PDF export functions.
- `src/ui_components.py` — reusable dialogs (`ApiKeyDialog`, `AboutDialog`, `PreviewWindow`).
- `src/i18n.py` — multilanguage support (es/en) via `t(key, lang)`.
- `src/config.py` — `.env` loading and API key re-export from `keyring_storage`.
- `src/keyring_storage.py` — OS keyring get/set for API key.
- `src/interactive_report.py` — interactive HTML report generator with SVG charts.
- `src/svg_charts.py` — pure SVG chart generation (donut, bar, line).
- `data/` — runtime-only, gitignored. Created automatically.

## Important conventions

- **All imports are relative to `src/`.** Never `from src.utils import ...`; just `from utils import ...`.
- **GUI is PySide6 (Qt).** No tkinter, no customtkinter. All UI uses Qt widgets and signals/slots.
- **API base URL:** `free.intelx.io` (hardcoded in `src/api.py`).
- **Deduplication** uses `systemid`/`storageid` fields from the API. Don't use `id` — IntelX records don't have that field.
- **Result accumulation:** `gui.py` merges new results via `merge_records()`. Never reassign `self.current_records = new_data` directly.
- **Thread safety:** GUI updates from background threads use Qt signals (`Signal`). Never touch Qt widgets from a non-main thread.
- **Language:** Comments and UI strings are in Spanish. Keep consistent.
- **Color palette:** Tailwind blue (`#2563EB`), matching IP-Analyzer style. Defined in `gui.py` `COLORS` dict.

## Gotchas

- `.env` is gitignored. API key is stored in system keyring via the `keyring` library.
- `data/` is gitignored — it holds user search history. Never commit it.
- The app logs to `intelx_checker.log` (also gitignored).
- Windows path separators: this project is developed on Windows. Watch out for mixed `/` and `\` in paths.
- `history.json` format: `{"records": [...], "last_updated": "..."}` — not a bare list.
- `qtawesome` provides FontAwesome icons. If not installed, the app works but menus/buttons have no icons.

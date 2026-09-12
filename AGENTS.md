# AGENTS.md — IntelX Checker

## What this is

Python desktop app (customtkinter GUI + CLI) that queries the Intelligence X API for data leak / OSINT investigations. All source lives in `src/`. The app runs from `src/main.py`.

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

Tests use `unittest`. No test runner config exists; `pytest` discovers them fine. Some tests hit the IntelX API (rate-limited, may fail on CI without key).

## Key architecture

- `src/main.py` — entrypoint. Parses args, launches GUI or CLI.
- `src/gui.py` — main `IntelXCheckerApp(ctk.CTk)` class. Search runs in a background thread via `_search_worker`.
- `src/api.py` — all IntelX API calls. `check_intelx()` returns `(success, data, search_id)`.
- `src/utils.py` — persistence (`load_history`, `save_history`, `merge_records`) and helpers. History stored in `data/history.json`.
- `src/exports.py` — CSV/JSON/HTML/PDF export functions.
- `src/ui_components.py` — reusable dialogs and widgets.
- `src/i18n.py` — multilanguage support (es/en).
- `src/config.py` — `.env` loading and API key management via keyring.
- `data/` — runtime-only, gitignored. Created automatically.

## Important conventions

- **All imports are relative to `src/`.** The `src/` directory is the Python path root. Never import as `from src.utils import ...`; just `from utils import ...`.
- **API base URL:** `free.intelx.io` (hardcoded in `src/api.py`).
- **Deduplication** uses `systemid`/`storageid` fields from the API. Don't use `id` — IntelX records don't have that field.
- **Result accumulation:** `gui.py` merges new results into `self.current_records` via `merge_records()`. Never reassign `self.current_records = new_data` directly; always merge.
- **Thread safety:** GUI updates from background threads must use `self.after(0, callback)`. Never touch tkinter widgets from a non-main thread.
- **Language:** Comments and UI strings are in Spanish. Keep consistent.

## Gotchas

- `src/__init__.py` has wildcard imports that break `python -m pytest` from repo root. Always `cd src` before running tests, or run from `src/`.
- `.env` is gitignored. API key is stored in system keyring via the `keyring` library.
- `data/` is gitignored — it holds user search history. Never commit it.
- The app logs to `intelx_checker.log` (also gitignored).
- Windows path separators: this project is developed on Windows. Watch out for mixed `/` and `\` in paths.

"""Small utility helpers used across modules."""
import os
import webbrowser


def sanitize_filename(s: str) -> str:
    if not s:
        return 'search'
    return s.replace('@', '_at_').replace('.', '_dot_').replace(' ', '_')


def open_in_browser(path: str):
    # cross-platform open; on Windows webbrowser.open works fine
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    webbrowser.open(path)

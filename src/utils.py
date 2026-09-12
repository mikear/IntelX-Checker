"""Small utility helpers used across modules."""
import os
import webbrowser


import re

def sanitize_filename(s: str) -> str:
    """Sanitizes a string for use as a valid filename.

    Args:
        s: Input string (e.g. email or domain).

    Returns:
        Sanitized filename string.
    """
    if not s or not isinstance(s, str):
        return 'search'
    s_clean = s.replace('@', '_at_').replace('.', '_dot_').replace(' ', '_')
    s_clean = re.sub(r'[^a-zA-Z0-9_\-]', '', s_clean)
    return s_clean or 'search'


def open_in_browser(path: str) -> None:
    """Opens a file path in the default web browser.

    Args:
        path: File path to open.

    Raises:
        FileNotFoundError: If the specified file path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    webbrowser.open(path)

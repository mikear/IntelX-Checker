"""Small utility helpers used across modules."""
import os
import webbrowser


def sanitize_filename(s: str) -> str:
    """Sanitizes a string for use as a valid filename.

    Args:
        s: Input string (e.g. email or domain).

    Returns:
        Sanitized filename string.
    """
    if not s:
        return 'search'
    return s.replace('@', '_at_').replace('.', '_dot_').replace(' ', '_')


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

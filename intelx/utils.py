"""Small utility helpers used across modules."""
import os
import webbrowser
import re


def sanitize_filename(s: str) -> str:
    if not s:
        return 'search'
    s = s.replace('https://', '').replace('http://', '')
    # Only replace characters that are invalid in filenames, but keep dots for extensions
    invalid_chars = r'[<>:"/\\|?* ]' # Common invalid characters, including space
    s = re.sub(invalid_chars, '_', s) 
    s = s.replace('@', '_at_') # Keep this for email addresses
    return s


def open_in_browser(path: str):
    # cross-platform open; on Windows webbrowser.open works fine
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    webbrowser.open(path)

"""Small utility helpers used across modules."""
import os
import webbrowser
import json
import logging
from datetime import datetime, timezone

import re

logger = logging.getLogger(__name__)

# Ruta del archivo de historial
_HISTORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
_HISTORY_FILE = os.path.join(_HISTORY_DIR, 'history.json')

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


def _get_record_key(record: dict) -> str:
    """Extrae una clave única de un registro para deduplicación.

    Usa 'id' si existe, si no combina 'name' + 'storage'.
    """
    if not isinstance(record, dict):
        return str(record)

    record_id = record.get('id')
    if record_id is not None:
        return f"id:{record_id}"

    name = record.get('name', '')
    storage = record.get('storage', '')
    return f"name:{name}|storage:{storage}"


def merge_records(existing: list, new: list) -> list:
    """Fusiona dos listas de registros eliminando duplicados.

    Preserva el orden: primero los existentes, luego los nuevos.
    """
    seen = set()
    merged = []
    for record in existing + new:
        key = _get_record_key(record)
        if key not in seen:
            seen.add(key)
            merged.append(record)
    return merged


def load_history() -> list:
    """Carga el historial de registros desde el archivo JSON.

    Returns:
        Lista de registros o lista vacía si no existe el archivo o hay error.
    """
    try:
        if not os.path.exists(_HISTORY_FILE):
            return []
        with open(_HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        records = data.get('records', [])
        logger.info(f"Historial cargado: {len(records)} registros")
        return records
    except Exception as e:
        logger.exception("Error cargando historial")
        return []


def save_history(records: list) -> bool:
    """Guarda la lista de registros en el archivo JSON histórico.

    Args:
        records: Lista de registros a persistir.

    Returns:
        True si se guardó correctamente, False si hubo error.
    """
    try:
        os.makedirs(_HISTORY_DIR, exist_ok=True)
        data = {
            'records': records,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        with open(_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Historial guardado: {len(records)} registros")
        return True
    except Exception as e:
        logger.exception("Error guardando historial")
        return False

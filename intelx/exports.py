"""Export helpers: CSV, JSON and simple PDF generation extracted from the legacy GUI.

These functions are UI-agnostic and return the path of the created file. The GUI
can display messages or open the file/folder as needed.
"""
from __future__ import annotations

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def _default_exports_dir(kind: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, 'exports', kind)
    os.makedirs(path, exist_ok=True)
    return path


def _timestamped_name(base_name: str) -> str:
    return f"{base_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}."  # caller appends ext


def export_to_csv(records: List[Dict[str, Any]], filename: Optional[str] = None, exports_dir: Optional[str] = None) -> str:
    """Export records to CSV. Returns the file path.

    If filename is not provided a timestamped name will be generated.
    """
    if exports_dir is None:
        exports_dir = _default_exports_dir('csv')

    if not filename:
        filename = _timestamped_name('intelx_export') + 'csv'
    filepath = os.path.join(exports_dir, filename)

    try:
        # Determine headers as union of all keys in records
        keys = []
        for r in records:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)

        with open(filepath, 'w', encoding='utf-8', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            for r in records:
                # Ensure all values are primitives or strings
                row = {k: ('' if r.get(k) is None else str(r.get(k))) for k in keys}
                writer.writerow(row)

        logger.info('CSV export written: %s', filepath)
        return filepath

    except Exception as e:
        logger.exception('Error writing CSV export')
        raise


def export_to_json(records: List[Dict[str, Any]], filename: Optional[str] = None, exports_dir: Optional[str] = None) -> str:
    """Export records to JSON (pretty printed). Returns the file path."""
    if exports_dir is None:
        exports_dir = _default_exports_dir('json')

    if not filename:
        filename = _timestamped_name('intelx_export') + 'json'
    filepath = os.path.join(exports_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as fh:
            json.dump(records, fh, indent=2, ensure_ascii=False)

        logger.info('JSON export written: %s', filepath)
        return filepath

    except Exception:
        logger.exception('Error writing JSON export')
        raise


def select_records_for_export(records: List[Dict[str, Any]], selected_ids: Optional[List[str]] = None, id_field: str = 'storageid') -> List[Dict[str, Any]]:
    """Return a subset of records filtered by a list of ids (id_field).

    If selected_ids is None or empty the full records list is returned.
    """
    if not selected_ids:
        return records

    id_set = set(str(i) for i in selected_ids)
    filtered = [r for r in records if str(r.get(id_field, '')) in id_set]
    return filtered



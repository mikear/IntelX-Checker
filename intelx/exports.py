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


def generate_pdf_report(records: List[Dict[str, Any]], filepath: Optional[str] = None, title: Optional[str] = None) -> str:
    # Prefer the richer generator implemented in intelx.pdf_report if available
    try:
        from .pdf_report import generate_pdf_report as rich_pdf
    except Exception:
        rich_pdf = None

    if not filepath:
        exports_dir = _default_exports_dir('pdf')
        filename = _timestamped_name('intelx_report') + 'pdf'
        filepath = os.path.join(exports_dir, filename)

    if rich_pdf:
        return rich_pdf(records, filepath, search_term=title)

    # Fallback minimal PDF generator (uses reportlab.canvas)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
    except Exception as e:
        logger.exception('reportlab not available for PDF generation')
        raise

    if title is None:
        title = 'IntelX Report'

    try:
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # Header
        c.setFont('Helvetica-Bold', 14)
        c.drawString(20 * mm, height - 20 * mm, title)
        c.setFont('Helvetica', 9)
        c.drawString(20 * mm, height - 26 * mm, f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}')

        # Summary
        c.setFont('Helvetica-Bold', 11)
        c.drawString(20 * mm, height - 36 * mm, f'Total Records: {len(records)}')

        # Draw a simple table with first N records
        max_rows = 20
        y = height - 46 * mm
        c.setFont('Helvetica', 8)

        if records:
            # Determine columns to show (date, name, bucket, systemid)
            cols = ['date', 'name', 'bucket', 'systemid']
            col_x = [20 * mm, 60 * mm, 140 * mm, 170 * mm]

            # Header row
            for i, col in enumerate(cols):
                c.drawString(col_x[i], y, col.upper())
            y -= 6 * mm

            for row in records[:max_rows]:
                for i, col in enumerate(cols):
                    val = row.get(col, '')
                    text = str(val)[:50]
                    c.drawString(col_x[i], y, text)
                y -= 6 * mm
                if y < 30 * mm:
                    c.showPage()
                    y = height - 20 * mm

        c.showPage()
        c.save()
        logger.info('PDF generated: %s', filepath)
        return filepath

    except Exception:
        logger.exception('Error generating PDF')
        raise

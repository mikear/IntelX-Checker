"""Export helpers for CSV, JSON, PDF and interactive HTML reports.

These functions are UI-agnostic and return the path of the created file. The GUI
can display messages or open the file/folder as needed.
"""
from __future__ import annotations

import os
import json
import csv
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

from interactive_report import generate_interactive_html_report

logger = logging.getLogger(__name__)


def _pdf_text(value: Any) -> str:
    """Return text that ReportLab's built-in fonts can render safely."""
    if value is None:
        return ''
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, default=str)
    # Helvetica uses WinAnsi encoding. Replacing unsupported glyphs is preferable
    # to failing an otherwise valid export because a result contains an emoji.
    return str(value).encode('latin-1', 'replace').decode('latin-1')


def _default_exports_dir(kind: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, 'exports', kind)
    os.makedirs(path, exist_ok=True)
    return path


def _timestamped_name(base_name: str) -> str:
    return f"{base_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}."  # caller appends ext


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


def generate_pdf_report(records: List[Dict[str, Any]], title: str = 'IntelX Export',
                        filename: Optional[str] = None,
                        exports_dir: Optional[str] = None) -> str:
    """Generate a printable PDF report from Intelligence X search results.

    The report keeps the fields shown in the results grid and wraps long values
    so every column remains inside an A4 portrait page.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle)
    except ImportError as exc:
        raise RuntimeError(
            'La exportación a PDF requiere la dependencia "reportlab". '
            'Instale las dependencias de la aplicación y vuelva a intentarlo.'
        ) from exc

    if exports_dir is None:
        exports_dir = _default_exports_dir('pdf')
    else:
        os.makedirs(exports_dir, exist_ok=True)
    if not filename:
        safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        stem = safe_title.replace(' ', '_') or 'IntelX_Export'
        filename = f'{stem}_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.pdf'
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    filepath = os.path.join(exports_dir, filename)

    styles = getSampleStyleSheet()
    heading = ParagraphStyle('PDFHeading', parent=styles['Heading1'], alignment=TA_CENTER,
                             fontName='Helvetica-Bold', fontSize=16, leading=20,
                             textColor=colors.HexColor('#1f4e79'), spaceAfter=4)
    subtitle = ParagraphStyle('PDFSubtitle', parent=styles['Normal'], alignment=TA_CENTER,
                              fontSize=9, leading=12, textColor=colors.HexColor('#555555'))
    cell = ParagraphStyle('PDFCell', parent=styles['Normal'], alignment=TA_LEFT,
                          fontSize=7, leading=9)
    header = ParagraphStyle('PDFHeader', parent=cell, alignment=TA_CENTER,
                            fontName='Helvetica-Bold', textColor=colors.white)

    fields = [
        ('date', 'Fecha', 20 * mm),
        ('name', 'Nombre', 48 * mm),
        ('bucket', 'Fuente', 28 * mm),
        ('type', 'Tipo', 18 * mm),
        ('size', 'Tamaño', 16 * mm),
        ('storageid', 'ID', 48 * mm),
    ]
    data = [[Paragraph(label, header) for _, label, _ in fields]]
    for record in records:
        data.append([
            Paragraph(_pdf_text(record.get(key)), cell)
            for key, _, _ in fields
        ])

    document = SimpleDocTemplate(
        filepath, pagesize=A4, leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=13 * mm, bottomMargin=13 * mm, title=_pdf_text(title),
        author='IntelX Checker',
    )
    table = Table(data, colWidths=[width for _, _, width in fields], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#c8d2dc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f7fa')]),
    ]))
    story = [
        Paragraph(_pdf_text(title), heading),
        Paragraph(f'Resultados exportados: {len(records)} | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', subtitle),
        Spacer(1, 7 * mm), table,
    ]
    try:
        document.build(story)
    except Exception:
        logger.exception('Error writing PDF export')
        raise

    logger.info('PDF export written: %s', filepath)
    return filepath


def select_records_for_export(records: List[Dict[str, Any]], selected_ids: Optional[List[str]] = None, id_field: str = 'storageid') -> List[Dict[str, Any]]:
    """Return a subset of records filtered by a list of ids (id_field).

    If selected_ids is None or empty the full records list is returned.
    """
    if not selected_ids:
        return records

    id_set = set(str(i) for i in selected_ids)
    filtered = [r for r in records if str(r.get(id_field, '')) in id_set]
    return filtered


def export_to_interactive_html(records: List[Dict[str, Any]], 
                              filename: Optional[str] = None, 
                              exports_dir: Optional[str] = None,
                              search_term: str = "",
                              app_version: str = "2.0.0") -> str:
    """Export records to an interactive HTML report. Returns the file path.

    This generates a modern, interactive HTML report with:
    - Interactive table with sorting and filtering
    - Data visualization charts
    - Modern responsive design
    - Standalone HTML file (no external dependencies except CDN for Chart.js)
    
    Args:
        records: List of record dictionaries to export
        filename: Optional filename. If not provided, a timestamped name will be generated
        exports_dir: Optional directory path. Defaults to exports/html/
        search_term: The search term used to generate these results
        app_version: Application version for the footer
        
    Returns:
        The full path to the generated HTML file
    """
    if exports_dir is None:
        exports_dir = _default_exports_dir('html')

    if not filename:
        # Generate filename based on search term and timestamp
        safe_search_term = "".join(c for c in search_term if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if safe_search_term:
            filename = f"IntelX_Report_{safe_search_term.replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"
        else:
            filename = _timestamped_name('IntelX_Report') + 'html'
    
    filepath = os.path.join(exports_dir, filename)

    try:
        # Generate the interactive report
        result_path = generate_interactive_html_report(records, filepath, search_term, app_version)
        logger.info('Interactive HTML report written: %s', result_path)
        return result_path

    except Exception as e:
        logger.exception('Error writing interactive HTML report')
        raise



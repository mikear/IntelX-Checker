"""PDF report generator extracted from legacy GUI._generate_pdf_report.

This module is UI-agnostic: it receives records and a filepath and writes
a multi-page PDF with summary, charts and a table. It depends on reportlab,
matplotlib and pandas. Errors raise exceptions for the caller to handle.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def generate_pdf_report(records: List[Dict[str, Any]], filepath: str, search_term: Optional[str] = None):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pandas as pd
        import tempfile
        import os
    except ImportError as e:
        logger.exception('PDF dependencies missing')
        raise

    # Prepare document
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    story = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18)
    normal = styles['Normal']

    # Title
    title_text = f'IntelX Report - {search_term}' if search_term else 'IntelX Report'
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 12))

    # Summary
    total = len(records)
    story.append(Paragraph(f'Total records: <b>{total}</b>', normal))
    story.append(Spacer(1, 12))

    # Use pandas to build simple aggregates if available
    try:
        df = pd.DataFrame(records)
    except Exception:
        df = None

    tmp_files = []
    try:
        # Sources pie chart
        if df is not None and 'bucket' in df.columns:
            src_counts = df['bucket'].fillna('N/A').value_counts().head(10)
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.pie(src_counts.values, labels=src_counts.index, autopct='%1.1f%%')
            ax.set_title('Top Sources')
            tf = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            fig.savefig(tf.name, bbox_inches='tight')
            plt.close(fig)
            tmp_files.append(tf.name)
            story.append(Image(tf.name, width=450, height=150))
            story.append(Spacer(1, 12))

        # Timeline chart
        if df is not None and 'date' in df.columns:
            try:
                dates = pd.to_datetime(df['date'], errors='coerce').dropna()
                if not dates.empty:
                    series = dates.dt.to_period('M').value_counts().sort_index()
                    fig, ax = plt.subplots(figsize=(6, 2))
                    ax.plot(series.index.astype(str), series.values, marker='o')
                    ax.set_title('Activity by Month')
                    ax.set_xticklabels(series.index.astype(str), rotation=45, fontsize=7)
                    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    fig.savefig(tf.name, bbox_inches='tight')
                    plt.close(fig)
                    tmp_files.append(tf.name)
                    story.append(Image(tf.name, width=450, height=120))
                    story.append(Spacer(1, 12))
            except Exception:
                logger.exception('Error creating timeline chart')

        # Table of first N records
        if records:
            cols = ['date', 'name', 'bucket', 'systemid']
            header = [c.upper() for c in cols]
            table_data = [header]
            for r in records[:30]:
                row = [str(r.get(c, ''))[:80] for c in cols]
                table_data.append(row)

            t = Table(table_data, colWidths=[100, 200, 100, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

        story.append(PageBreak())

        doc.build(story)
        logger.info('PDF generated at %s', filepath)
        return filepath

    finally:
        # Clean up temporary files
        for p in tmp_files:
            try:
                os.unlink(p)
            except Exception:
                pass

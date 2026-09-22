"""Generador PDF profesional (estilo informe pentest/OSINT: OWASP/PTES).

Estructura: portada con control documental, índice automático (TOC),
resumen ejecutivo con gráficos nativos, hallazgos numerados con severidad,
IOCs, metodología, recomendaciones, resultados detallados y glosario.

Solo usa reportlab (sin dependencias nuevas, 100% offline).
"""
from collections import Counter
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, PageBreak, Flowable, NextPageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

import report_narrative as narrative

logger = logging.getLogger(__name__)

PAGE_W, PAGE_H = A4
MARGIN = 15 * mm

NAVY = colors.HexColor("#1B2A4A")
ACCENT = colors.HexColor("#2563EB")
MUTED = colors.HexColor("#64748B")
LIGHT_BG = colors.HexColor("#F4F7FA")
GRID = colors.HexColor("#C8D2DC")

SEV_STYLE = {
    "critical": (colors.HexColor("#FEE2E2"), colors.HexColor("#991B1B"), colors.HexColor("#B91C1C")),
    "high": (colors.HexColor("#FEF3C7"), colors.HexColor("#92400E"), colors.HexColor("#D97706")),
    "medium": (colors.HexColor("#DBEAFE"), colors.HexColor("#1E40AF"), colors.HexColor("#2563EB")),
    "low": (colors.HexColor("#DCFCE7"), colors.HexColor("#166534"), colors.HexColor("#16A34A")),
    "unknown": (colors.HexColor("#E5E7EB"), colors.HexColor("#374151"), colors.HexColor("#6B7280")),
}

LABELS = {
    "es": {
        "classification": "TLP:CLEAR",
        "subtitle": "Informe de Inteligencia · Intelligence X",
        "doc_control": "Control del Documento",
        "version": "Versión", "date": "Fecha (UTC)", "author": "Autor",
        "query": "Consulta", "search_id": "ID de búsqueda", "results": "Resultados",
        "distribution": "Distribución", "toc": "Índice",
        "executive": "1. Resumen Ejecutivo", "kpis": "Cifras clave",
        "total": "Resultados", "sources": "Fuentes únicas", "leaks": "% en filtraciones",
        "critical_high": "Críticos + Altos",
        "sev_chart": "Hallazgos por severidad",
        "src_chart": "Principales fuentes",
        "findings": "2. Hallazgos Clave",
        "no_data": "Sin datos para mostrar.",
        "iocs": "3. Indicadores de Compromiso (IOCs)",
        "capped": "Mostrando {shown} de {total}.",
        "method": "4. Metodología y Alcance",
        "recs": "5. Recomendaciones",
        "details": "6. Resultados Detallados",
        "glossary": "7. Glosario y Advertencias",
        "footer_note": "IntelX Checker V2 · Informe confidencial de uso interno",
        "page": "Página",
        "of": "de",
        "sev_col": "Severidad", "score_col": "Score",
    },
    "en": {
        "classification": "TLP:CLEAR",
        "subtitle": "Intelligence Report · Intelligence X",
        "doc_control": "Document Control",
        "version": "Version", "date": "Date (UTC)", "author": "Author",
        "query": "Query", "search_id": "Search ID", "results": "Results",
        "distribution": "Distribution", "toc": "Contents",
        "executive": "1. Executive Summary", "kpis": "Key figures",
        "total": "Results", "sources": "Unique sources", "leaks": "% in leaks",
        "critical_high": "Critical + High",
        "sev_chart": "Findings by severity",
        "src_chart": "Top sources",
        "findings": "2. Key Findings",
        "no_data": "No data to display.",
        "iocs": "3. Indicators of Compromise (IOCs)",
        "capped": "Showing {shown} of {total}.",
        "method": "4. Methodology & Scope",
        "recs": "5. Recommendations",
        "details": "6. Detailed Results",
        "glossary": "7. Glossary & Caveats",
        "footer_note": "IntelX Checker V2 · Confidential internal-use report",
        "page": "Page",
        "of": "of",
        "sev_col": "Severity", "score_col": "Score",
    },
}


def _pdf_text(value: Any) -> str:
    """Texto seguro para las fuentes integradas de ReportLab (WinAnsi)."""
    if value is None:
        return ""
    return str(value).encode("latin-1", "replace").decode("latin-1")


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"],
                                      fontName="Helvetica-Bold", fontSize=26, leading=30,
                                      textColor=colors.white, alignment=TA_CENTER),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Normal"],
                                    fontName="Helvetica", fontSize=13, leading=17,
                                    textColor=colors.HexColor("#BFDBFE"), alignment=TA_CENTER),
        "cover_term": ParagraphStyle("CoverTerm", parent=base["Normal"],
                                     fontName="Helvetica-Bold", fontSize=16, leading=20,
                                     textColor=colors.white, alignment=TA_CENTER),
        "cover_meta": ParagraphStyle("CoverMeta", parent=base["Normal"],
                                     fontName="Helvetica", fontSize=9, leading=12,
                                     textColor=colors.HexColor("#DBEAFE"), alignment=TA_CENTER),
        "h1": ParagraphStyle("ReportH1", parent=base["Heading1"],
                             fontName="Helvetica-Bold", fontSize=15, leading=19,
                             textColor=NAVY, spaceBefore=14, spaceAfter=8,
                             keepWithNext=True),
        "h2": ParagraphStyle("ReportH2", parent=base["Heading2"],
                             fontName="Helvetica-Bold", fontSize=11, leading=14,
                             textColor=colors.HexColor("#1F4E79"), spaceBefore=10, spaceAfter=5,
                             keepWithNext=True),
        "body": ParagraphStyle("ReportBody", parent=base["Normal"],
                               fontName="Helvetica", fontSize=9.5, leading=14,
                               alignment=TA_JUSTIFY, spaceAfter=5),
        "bullet": ParagraphStyle("ReportBullet", parent=base["Normal"],
                                 fontName="Helvetica", fontSize=9.5, leading=14,
                                 leftIndent=14, bulletIndent=6, spaceAfter=4),
        "cell": ParagraphStyle("ReportCell", parent=base["Normal"],
                               fontName="Helvetica", fontSize=7.5, leading=10),
        "cell_h": ParagraphStyle("ReportCellH", parent=base["Normal"],
                                 fontName="Helvetica-Bold", fontSize=7.5, leading=10,
                                 textColor=colors.white, alignment=TA_CENTER),
        "caption": ParagraphStyle("ReportCaption", parent=base["Normal"],
                                  fontName="Helvetica-Oblique", fontSize=8, leading=11,
                                  textColor=MUTED, alignment=TA_CENTER, spaceAfter=8),
        "toc1": ParagraphStyle("TOC1", parent=base["Normal"],
                               fontName="Helvetica-Bold", fontSize=10, leading=15),
        "toc2": ParagraphStyle("TOC2", parent=base["Normal"],
                               fontName="Helvetica", fontSize=9, leading=13,
                               leftIndent=14),
    }


class NumberedCanvas(pdfcanvas.Canvas):
    """Canvas que numera 'Página X de Y' (requiere dos pasadas, compatible con multiBuild)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            self._draw_page_number(total)
            super().showPage()
        super().save()

    def _draw_page_number(self, total: int):
        if getattr(self, "_skip_number", False):
            return
        labels = getattr(self, "_num_labels", {"page": "Página", "of": "de"})
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - MARGIN, 10 * mm,
                             f"{labels['page']} {self._pageNumber} {labels['of']} {total}")
        self.restoreState()


def _cover_page(canv, doc):
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#EF4444"))
    canv.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawCentredString(PAGE_W / 2, PAGE_H - 8.2 * mm, doc.classification)
    canv.setFillColor(colors.HexColor("#EF4444"))
    canv.rect(0, 0, PAGE_W, 12 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawCentredString(PAGE_W / 2, 4.2 * mm, doc.classification)
    canv._skip_number = True
    canv.restoreState()


def _inner_page(canv, doc):
    canv.saveState()
    canv.setFillColor(colors.HexColor("#EF4444"))
    canv.rect(0, PAGE_H - 9 * mm, PAGE_W, 9 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawCentredString(PAGE_W / 2, PAGE_H - 6.2 * mm, doc.classification)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 8)
    canv.drawString(MARGIN, 10 * mm, doc.footer_note)
    canv._skip_number = False
    canv.restoreState()


class IntelXDocTemplate(BaseDocTemplate):
    """Plantilla con portada + páginas interiores y registro de entradas TOC."""

    def __init__(self, filename, classification: str, footer_note: str, **kwargs):
        super().__init__(filename, pagesize=A4,
                         leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=16 * mm, bottomMargin=16 * mm,
                         showBoundary=0, **kwargs)
        self.classification = classification
        self.footer_note = footer_note
        cover_frame = Frame(self.leftMargin, self.bottomMargin,
                            self.width, self.height, id="cover")
        inner_frame = Frame(self.leftMargin, self.bottomMargin,
                            self.width, self.height, id="inner")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame], onPage=_cover_page),
            PageTemplate(id="inner", frames=[inner_frame], onPage=_inner_page),
        ])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = getattr(flowable.style, "name", "")
            if name in ("ReportH1", "ReportH2"):
                level = 0 if name == "ReportH1" else 1
                text = flowable.getPlainText()
                key = f"h{level}-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (level, text, self.page, key))


def _styled_table(data, col_widths, header_bg=NAVY, font_size=None) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    return table


def _severity_drawing(counts: Dict[str, int], width: int = 380, height: int = 190,
                      lang: str = "es") -> Optional[Drawing]:
    """Tarta de severidad (solo niveles con datos)."""
    items = [(k, counts.get(k, 0)) for k in narrative.SEVERITY_ORDER if counts.get(k, 0) > 0]
    if not items:
        return None
    drawing = Drawing(width, height)
    pie = Pie()
    pie.x, pie.y, pie.width, pie.height = 90, 20, 150, 150
    pie.data = [v for _, v in items]
    pie.labels = [f"{narrative.SEVERITY_ORDER.index(k) + 1}" for k, _ in items]
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white
    for i, (key, _) in enumerate(items):
        pie.slices[i].fillColor = SEV_STYLE[key][2]
    drawing.add(pie)
    # Leyenda manual
    y = height - 30
    for pos, (key, value) in enumerate(items):
        _, _, dot = SEV_STYLE[key]
        drawing.add(Rect(270, y - pos * 22, 12, 12, strokeColor=dot, fillColor=dot))
        drawing.add(String(288, y - pos * 22 + 1,
                           f"{narrative.severity_label(key, lang)}: {value}",
                           fontName="Helvetica", fontSize=9, fillColor=colors.black))
    return drawing


def _sources_drawing(top_sources, width: int = 420, height: int = 200) -> Optional[Drawing]:
    """Barras verticales con las principales fuentes."""
    if not top_sources:
        return None
    labels = [str(name)[:10] for name, _ in top_sources]
    values = [count for _, count in top_sources]
    drawing = Drawing(width, height)
    chart = VerticalBarChart()
    chart.x, chart.y, chart.height, chart.width = 50, 40, 130, width - 90
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.angle = 25
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueStep = max(1, (max(values) // 4) or 1)
    chart.bars[0].fillColor = ACCENT
    chart.bars[0].strokeColor = NAVY
    drawing.add(chart)
    return drawing


def generate_professional_pdf(records: List[Dict[str, Any]],
                              filepath: str,
                              title: str = "IntelX Intelligence Report",
                              search_term: str = "",
                              search_id: Optional[str] = None,
                              lang: str = "es",
                              app_version: str = "2.0.0") -> str:
    """Genera el PDF profesional completo y devuelve su ruta."""
    lang = lang if lang in LABELS else "es"
    labels = LABELS[lang]
    styles = _styles()
    records = records or []
    generated = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    narration = narrative.build_report_narrative(records, search_term, search_id, lang)
    sev_counts = narration["severity_counts"]
    total = len(records)
    sources = sorted({r.get("bucket", "N/A") for r in records if isinstance(r, dict)})
    top_sources = Counter(r.get("bucket", "N/A") for r in records
                          if isinstance(r, dict)).most_common(6)
    leaks = sum(1 for r in records
                if isinstance(r, dict) and ("leak" in str(r.get("bucket", "")).lower()
                                            or "paste" in str(r.get("bucket", "")).lower()))
    leaks_pct = (leaks / total * 100) if total else 0.0
    crit_high = sev_counts.get("critical", 0) + sev_counts.get("high", 0)

    doc = IntelXDocTemplate(filepath, classification=labels["classification"],
                            footer_note=labels["footer_note"],
                            title=_pdf_text(title), author="IntelX Checker")
    story: List[Flowable] = []
    cell, cell_h = styles["cell"], styles["cell_h"]

    # ---------------- Portada ----------------
    story.append(Spacer(1, 42 * mm))
    story.append(Paragraph("🛡 INTELX CHECKER", styles["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(_pdf_text(title), styles["cover_title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(_pdf_text(labels["subtitle"]), styles["cover_sub"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(_pdf_text(f'"{search_term}"' if search_term else "N/A"),
                           styles["cover_term"]))
    story.append(Spacer(1, 10 * mm))

    control = [
        [Paragraph(f"<b>{labels['version']}</b>", cell_h),
         Paragraph(f"<b>{labels['date']}</b>", cell_h),
         Paragraph(f"<b>{labels['author']}</b>", cell_h)],
        [Paragraph(f"1.0 ({app_version})", cell),
         Paragraph(generated, cell),
         Paragraph("IntelX Checker", cell)],
        [Paragraph(f"<b>{labels['query']}</b>", cell_h),
         Paragraph(f"<b>{labels['search_id']}</b>", cell_h),
         Paragraph(f"<b>{labels['results']}</b>", cell_h)],
        [Paragraph(_pdf_text(search_term or "N/A"), cell),
         Paragraph(_pdf_text(search_id or "N/A"), cell),
         Paragraph(str(total), cell)],
        [Paragraph(f"<b>{labels['distribution']}</b>", cell_h),
         Paragraph(f"<b>{labels['classification']}</b>", cell_h),
         Paragraph("", cell_h)],
        [Paragraph("Uso interno", cell) if lang == "es" else Paragraph("Internal use", cell),
         Paragraph(labels["classification"], cell),
         Paragraph("", cell)],
    ]
    story.append(_styled_table(control, [55 * mm, 60 * mm, 55 * mm]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(_pdf_text(labels["footer_note"]), styles["cover_meta"]))
    story.append(NextPageTemplate("inner"))
    story.append(PageBreak())

    # ---------------- Índice ----------------
    story.append(Paragraph(labels["toc"], styles["h1"]))
    toc = TableOfContents()
    toc.levelStyles = [styles["toc1"], styles["toc2"]]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(Spacer(1, 4 * mm))

    # ---------------- 1. Resumen ----------------
    story.append(Paragraph(labels["executive"], styles["h1"]))
    for paragraph in narration["summary"]:
        story.append(Paragraph(_pdf_text(paragraph), styles["body"]))

    story.append(Paragraph(labels["kpis"], styles["h2"]))
    kpi_data = [
        [Paragraph(f"<b>{labels['total']}</b>", cell_h),
         Paragraph(f"<b>{labels['sources']}</b>", cell_h),
         Paragraph(f"<b>{labels['leaks']}</b>", cell_h),
         Paragraph(f"<b>{labels['critical_high']}</b>", cell_h)],
        [Paragraph(str(total), cell), Paragraph(str(len(sources)), cell),
         Paragraph(f"{leaks_pct:.1f}%", cell), Paragraph(str(crit_high), cell)],
    ]
    story.append(_styled_table(kpi_data, [42 * mm, 42 * mm, 42 * mm, 42 * mm]))

    sev_drawing = _severity_drawing(sev_counts, lang=lang)
    if sev_drawing is not None:
        story.append(Spacer(1, 3 * mm))
        story.append(sev_drawing)
        story.append(Paragraph(_pdf_text(labels["sev_chart"]), styles["caption"]))

    src_drawing = _sources_drawing(top_sources)
    if src_drawing is not None:
        story.append(src_drawing)
        story.append(Paragraph(_pdf_text(labels["src_chart"]), styles["caption"]))

    sev_rows = [[Paragraph(f"<b>{labels['sev_col']}</b>", cell_h),
                 Paragraph(f"<b>{labels['score_col']}</b>", cell_h),
                 Paragraph(f"<b>{labels['results']}</b>", cell_h)]]
    sev_ranges = {"critical": "≥ 80", "high": "50–79", "medium": "20–49",
                  "low": "1–19", "unknown": "0"}
    for key in narrative.SEVERITY_ORDER:
        bg, fg, _ = SEV_STYLE[key]
        sev_rows.append([
            Paragraph(f"<font color='{bg.hexval()}'><b>■</b></font> "
                      f"{_pdf_text(narrative.severity_label(key, lang))}", cell),
            Paragraph(sev_ranges[key], cell),
            Paragraph(str(sev_counts.get(key, 0)), cell),
        ])
    story.append(_styled_table(sev_rows, [70 * mm, 50 * mm, 50 * mm]))

    # ---------------- 2. Hallazgos ----------------
    story.append(Paragraph(labels["findings"], styles["h1"]))
    findings = narration.get("findings", [])[:8]
    if not findings:
        story.append(Paragraph(labels["no_data"], styles["body"]))
    for rank, finding in enumerate(findings, start=1):
        sev_key = finding.get("severity", "unknown")
        bg, fg, _ = SEV_STYLE.get(sev_key, SEV_STYLE["unknown"])
        title = (f"IX-{rank:03d} — {finding.get('name', 'N/A')} "
                 f"[{finding.get('severity_label', '')}]")
        story.append(Paragraph(_pdf_text(title), styles["h2"]))
        system_id = finding.get("systemid", "")
        link = (f'<a href="https://intelx.io/?s={_pdf_text(system_id)}" color="#2563EB">'
                f'intelx.io/?s={_pdf_text(system_id)}</a>') if system_id else "N/A"
        detail = [
            [Paragraph(f"<b>{labels['sev_col']}</b>", cell_h),
             Paragraph(f"<b>{labels['score_col']}</b>", cell_h),
             Paragraph("<b>Bucket</b>", cell_h),
             Paragraph("<b>Date</b>" if lang == "en" else "<b>Fecha</b>", cell_h)],
            [Paragraph(f"<font color='{fg.hexval()}'><b>■ "
                      f"{_pdf_text(finding.get('severity_label', ''))}</b></font>", cell),
             Paragraph(str(finding.get("score", 0)), cell),
             Paragraph(_pdf_text(finding.get("bucket", "N/A")), cell),
             Paragraph(_pdf_text(finding.get("date", "N/A") or "N/A"), cell)],
        ]
        story.append(_styled_table(detail, [45 * mm, 30 * mm, 55 * mm, 40 * mm]))
        story.append(Paragraph(_pdf_text(finding.get("reason", "")), styles["body"]))
        story.append(Paragraph(f"Ref: {link}", styles["body"]))

    # ---------------- 3. IOCs ----------------
    story.append(Paragraph(labels["iocs"], styles["h1"]))
    iocs = narration.get("iocs", {})
    for key in ("emails", "ips", "domains", "urls"):
        values = iocs.get(key, [])
        story.append(Paragraph(f"{key.capitalize()} ({len(values)})", styles["h2"]))
        if not values:
            story.append(Paragraph(labels["no_data"], styles["body"]))
            continue
        shown = values[:30]
        rows = [[Paragraph(f"<b>{key.capitalize()}</b>", cell_h)]]
        rows += [[Paragraph(_pdf_text(v), cell)] for v in shown]
        story.append(_styled_table(rows, [170 * mm]))
        if len(values) > 30:
            story.append(Paragraph(
                _pdf_text(labels["capped"].format(shown=30, total=len(values))),
                styles["caption"]))

    # ---------------- 4. Metodología ----------------
    story.append(Paragraph(labels["method"], styles["h1"]))
    method_rows = [[Paragraph(f"<b>{_pdf_text(r.get('item', ''))}</b>", cell),
                    Paragraph(_pdf_text(r.get("value", "")), cell)]
                   for r in narration.get("methodology", [])]
    story.append(_styled_table(method_rows, [45 * mm, 125 * mm], header_bg=NAVY))

    # ---------------- 5. Recomendaciones ----------------
    rec_title = labels["recs"]
    story.append(Paragraph(rec_title, styles["h1"]))
    for idx, rec in enumerate(narration.get("recommendations", []), start=1):
        story.append(Paragraph(_pdf_text(f"{idx}. {rec}"), styles["bullet"],
                               bulletText="•"))

    # ---------------- 6. Detalle ----------------
    story.append(Paragraph(labels["details"], styles["h1"]))
    grid_fields = ["date", "name", "bucket", "sev", "score", "size", "id"]
    grid_labels = {
        "date": "Fecha" if lang == "es" else "Date",
        "name": "Nombre" if lang == "es" else "Name",
        "bucket": "Fuente" if lang == "es" else "Source",
        "sev": labels["sev_col"], "score": labels["score_col"],
        "size": "Tamaño" if lang == "es" else "Size", "id": "ID",
    }
    grid_widths = [18 * mm, 40 * mm, 24 * mm, 16 * mm, 12 * mm, 14 * mm, 42 * mm]
    grid = [[Paragraph(f"<b>{grid_labels[k]}</b>", cell_h) for k in grid_fields]]
    for record in records:
        if not isinstance(record, dict):
            continue
        sev_key = narrative.compute_severity(record)
        _, fg, _ = SEV_STYLE.get(sev_key, SEV_STYLE["unknown"])
        row_id = record.get("systemid", "") or record.get("storageid", "")
        date = str(record.get("date", "") or "")[:19] or "N/A"
        name = str(record.get("name", "N/A") or "N/A")
        name = name[:48] + "…" if len(name) > 48 else name
        grid.append([
            Paragraph(_pdf_text(date), cell),
            Paragraph(_pdf_text(name), cell),
            Paragraph(_pdf_text(record.get("bucket", "N/A")), cell),
            Paragraph(f"<font color='{fg.hexval()}'><b>■</b></font>", cell),
            Paragraph(str(narrative.score_of(record) or "–"), cell),
            Paragraph(_pdf_text(record.get("size", "N/A")), cell),
            Paragraph(_pdf_text(row_id), cell),
        ])
    if len(grid) == 1:
        grid.append([Paragraph(labels["no_data"], cell)] + [Paragraph("", cell)] * 6)
    story.append(_styled_table(grid, grid_widths))

    # ---------------- 7. Glosario ----------------
    story.append(Paragraph(labels["glossary"], styles["h1"]))
    glossary_rows = [[Paragraph(f"<b>{_pdf_text(g.get('term', ''))}</b>", cell),
                      Paragraph(_pdf_text(g.get("definition", "")), cell)]
                     for g in narration.get("glossary", [])]
    story.append(_styled_table(glossary_rows, [40 * mm, 130 * mm], header_bg=NAVY))

    num_labels = {"page": labels["page"], "of": labels["of"]}

    def _maker(*args, **kwargs):
        kwargs["labels"] = num_labels
        return _NumberedWithLabels(*args, **kwargs)

    try:
        doc.multiBuild(story, canvasmaker=_maker)
    except Exception:
        logger.exception("Error writing professional PDF")
        raise
    logger.info("Professional PDF written: %s", filepath)
    return filepath


class _NumberedWithLabels(NumberedCanvas):
    """NumberedCanvas que recibe etiquetas de idioma."""

    def __init__(self, *args, **kwargs):
        self._init_labels = kwargs.pop("labels", {"page": "Página", "of": "de"})
        super().__init__(*args, **kwargs)
        self._num_labels = self._init_labels

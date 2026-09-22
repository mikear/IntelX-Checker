"""Capa narrativa compartida para los reportes HTML y PDF.

Genera contenido interpretativo (no solo números) a partir de los
registros de IntelX: severidad, resumen ejecutivo, hallazgos destacados,
IOCs, metodología, recomendaciones y glosario.

Sin dependencias Qt: es testeable con unittest/pytest puro.
"""
from collections import Counter
from datetime import datetime, timezone
from html import escape as _escape
import logging
from typing import List, Dict, Any, Optional

from analysis import extract_iocs

logger = logging.getLogger(__name__)

# Conjunto de medias descargables (documentos y contenedores).
DOWNLOADABLE_MEDIA = {15, 16, 17, 18, 19, 22, 23, 24, 27, 32}

# Niveles de severidad (claves internas, ordenadas de mayor a menor).
SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_UNKNOWN = "unknown"
SEVERITY_ORDER = [SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW, SEVERITY_UNKNOWN]

STRINGS = {
    "es": {
        "critical": "Crítica",
        "high": "Alta",
        "medium": "Media",
        "low": "Baja",
        "unknown": "Sin datos",
        "severity_title": "Distribución por Severidad",
        "media_title": "Tipos de Medio (Top)",
    },
    "en": {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "unknown": "No data",
        "severity_title": "Severity Distribution",
        "media_title": "Top Media Types",
    },
}


def _lang(lang: str) -> str:
    return lang if lang in STRINGS else "es"


def escape_html(text: Any) -> str:
    """Escapa texto para interpolación segura en HTML."""
    if text is None:
        return ""
    return _escape(str(text), quote=True)


def score_of(record: Dict[str, Any]) -> int:
    """Puntuación de riesgo tolerante a `xscore` o `score`.

    Algunos fixtures y respuestas usan `score`; la API documenta `xscore`.
    """
    if not isinstance(record, dict):
        return 0
    for key in ("xscore", "score"):
        try:
            value = record.get(key)
            if value is not None and float(value) > 0:
                return int(float(value))
        except (TypeError, ValueError):
            continue
    return 0


def compute_severity(record: Dict[str, Any]) -> str:
    """Clasifica un registro en un nivel de severidad.

    Umbrales documentados sobre la puntuación de riesgo:
    >=80 Crítica, >=50 Alta, >=20 Media, >0 Baja, 0 Sin datos.
    """
    score = score_of(record)
    if score >= 80:
        return SEVERITY_CRITICAL
    if score >= 50:
        return SEVERITY_HIGH
    if score >= 20:
        return SEVERITY_MEDIUM
    if score > 0:
        return SEVERITY_LOW
    return SEVERITY_UNKNOWN


def severity_label(key: str, lang: str = "es") -> str:
    """Etiqueta localizada de un nivel de severidad."""
    return STRINGS[_lang(lang)].get(key, key)


def severity_counts(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Cuenta registros por nivel de severidad (todas las claves presentes)."""
    counts = {key: 0 for key in SEVERITY_ORDER}
    for record in records or []:
        counts[compute_severity(record)] += 1
    return counts


def _is_leak_bucket(bucket: str) -> bool:
    bucket = (bucket or "").lower()
    return "leak" in bucket or "paste" in bucket


def _unique_sources(records: List[Dict[str, Any]]) -> List[str]:
    seen = []
    for record in records or []:
        bucket = record.get("bucket", "N/A") if isinstance(record, dict) else "N/A"
        if bucket not in seen:
            seen.append(bucket)
    return seen


def build_executive_summary(records: List[Dict[str, Any]],
                            search_term: str,
                            lang: str = "es") -> List[str]:
    """Genera 3-4 frases de resumen ejecutivo con cifras del análisis."""
    lang = _lang(lang)
    records = records or []
    total = len(records)
    term = (search_term or "N/A").strip() or "N/A"

    if total == 0:
        if lang == "en":
            return [
                f'No results were found for "{term}" in the Intelligence X index.',
                "This does not guarantee the absence of exposure: try alternate "
                "spellings, related domains, or a wider date range before closing the case.",
            ]
        return [
            f'No se encontraron resultados para "{term}" en el índice de Intelligence X.',
            "Esto no garantiza ausencia de exposición: pruebe variantes del término, "
            "dominios relacionados o un rango de fechas más amplio antes de cerrar el caso.",
        ]

    sources = _unique_sources(records)
    leaks = sum(1 for r in records if isinstance(r, dict) and _is_leak_bucket(str(r.get("bucket", ""))))
    leaks_pct = (leaks / total) * 100
    counts = severity_counts(records)
    critical_high = counts[SEVERITY_CRITICAL] + counts[SEVERITY_HIGH]

    top_source = Counter(
        r.get("bucket", "N/A") for r in records if isinstance(r, dict)
    ).most_common(1)
    top_source_name, top_source_n = top_source[0] if top_source else ("N/A", 0)

    months = Counter(
        r.get("date", "")[:7] for r in records
        if isinstance(r, dict) and isinstance(r.get("date"), str) and len(r.get("date", "")) >= 7
    )
    peak = months.most_common(1)[0] if months else None

    if lang == "en":
        paragraphs = [
            f'The search for "{term}" returned {total} result(s) across {len(sources)} '
            f"unique source(s), led by {top_source_name} ({top_source_n}).",
            f"{leaks_pct:.1f}% of the findings sit in leak/paste buckets and "
            f"{critical_high} record(s) are high or critical severity: these deserve "
            "immediate review.",
        ]
        if peak:
            paragraphs.append(
                f"Temporal concentration peaks in {peak[0]} ({peak[1]} record(s)): "
                "correlate that window with known incidents before drawing conclusions."
            )
        paragraphs.append(
            "All figures come from preview metadata (1 line per record on the free tier); "
            "confirm critical findings against the original source before acting."
        )
        return paragraphs

    paragraphs = [
        f'La búsqueda de "{term}" devolvió {total} resultado(s) en {len(sources)} '
        f"fuente(s) única(s), lideradas por {top_source_name} ({top_source_n}).",
        f"El {leaks_pct:.1f}% de los hallazgos está en buckets de filtraciones/pastes y "
        f"{critical_high} registro(s) son de severidad alta o crítica: requieren "
        "revisión inmediata.",
    ]
    if peak:
        paragraphs.append(
            f"La concentración temporal alcanza su pico en {peak[0]} ({peak[1]} registro(s)): "
            "correlacione esa ventana con incidentes conocidos antes de concluir."
        )
    paragraphs.append(
        "Todas las cifras provienen de metadatos de vista previa (1 línea por registro en el "
        "plan gratuito); confirme los hallazgos críticos contra la fuente original antes de actuar."
    )
    return paragraphs


def _finding_reason(record: Dict[str, Any], severity: str, lang: str) -> str:
    """Explica por qué un hallazgo es relevante."""
    bucket = str(record.get("bucket", "N/A"))
    score = score_of(record)
    leak = _is_leak_bucket(bucket)
    if lang == "en":
        base = {
            SEVERITY_CRITICAL: f"Risk score {score}: maximum priority.",
            SEVERITY_HIGH: f"Risk score {score}: likely sensitive exposure.",
            SEVERITY_MEDIUM: f"Risk score {score}: worth reviewing.",
            SEVERITY_LOW: f"Risk score {score}: low signal, keep for context.",
            SEVERITY_UNKNOWN: "No risk score: assess manually.",
        }[severity]
        if leak:
            base += f" Located in leak/paste bucket ({bucket})."
        return base
    base = {
        SEVERITY_CRITICAL: f"Puntuación de riesgo {score}: máxima prioridad.",
        SEVERITY_HIGH: f"Puntuación de riesgo {score}: probable exposición sensible.",
        SEVERITY_MEDIUM: f"Puntuación de riesgo {score}: conviene revisar.",
        SEVERITY_LOW: f"Puntuación de riesgo {score}: señal baja, conservar como contexto.",
        SEVERITY_UNKNOWN: "Sin puntuación de riesgo: evaluar manualmente.",
    }[severity]
    if leak:
        base += f" Ubicado en bucket de filtraciones/pastes ({bucket})."
    return base


def top_findings(records: List[Dict[str, Any]],
                 n: int = 5,
                 lang: str = "es") -> List[Dict[str, Any]]:
    """Devuelve los N hallazgos principales ordenados por puntuación, con explicación."""
    lang = _lang(lang)
    scored = []
    for record in records or []:
        if not isinstance(record, dict):
            continue
        severity = compute_severity(record)
        scored.append((score_of(record), severity, record))
    scored.sort(key=lambda item: (-item[0], str(item[2].get("date", ""))))
    findings = []
    for score, severity, record in scored[:max(0, n)]:
        findings.append({
            "name": record.get("name", "N/A"),
            "bucket": record.get("bucket", "N/A"),
            "date": record.get("date", ""),
            "score": score,
            "severity": severity,
            "severity_label": severity_label(severity, lang),
            "systemid": record.get("systemid", "") or record.get("storageid", ""),
            "reason": _finding_reason(record, severity, lang),
        })
    return findings


def collect_iocs(records: List[Dict[str, Any]],
                 max_items: int = 50) -> Dict[str, List[str]]:
    """Extrae IOCs de forma determinista (listas ordenadas)."""
    try:
        raw = extract_iocs(records or [], max_items=max_items)
    except Exception:
        logger.exception("Error extrayendo IOCs")
        raw = {"domains": [], "ips": [], "emails": [], "urls": []}
    return {key: sorted(set(raw.get(key, [])))[:max_items]
            for key in ("domains", "ips", "emails", "urls")}


def build_recommendations(records: List[Dict[str, Any]],
                          lang: str = "es") -> List[str]:
    """Recomendaciones accionables, con condicionales según los hallazgos."""
    lang = _lang(lang)
    records = records or []
    counts = severity_counts(records)
    critical_high = counts[SEVERITY_CRITICAL] + counts[SEVERITY_HIGH]
    public = sum(1 for r in records
                 if isinstance(r, dict) and "public" in str(r.get("tags", "")).lower())
    downloadable = sum(1 for r in records
                       if isinstance(r, dict) and r.get("media") in DOWNLOADABLE_MEDIA)

    if lang == "en":
        recs = [
            "Continuously monitor the searched term and its variants (alerts on new results).",
            "Enforce multi-factor authentication on every account linked to the exposed identities.",
        ]
        if critical_high:
            recs.insert(0, f"Rotate credentials of the {critical_high} high/critical finding(s) immediately "
                           "and review active sessions.")
        if public:
            recs.append(f"Assess takedown or delisting for the {public} publicly exposed record(s).")
        if downloadable:
            recs.append(f"Download and inspect the {downloadable} downloadable document(s) in a "
                        "sandboxed environment before classifying them.")
        recs.append("Record evidence (IDs, dates, hashes) and escalate to legal/compliance if personal data is involved.")
        return recs

    recs = [
        "Monitoree el término buscado y sus variantes de forma continua (alertas ante nuevos resultados).",
        "Exija autenticación multifactor en todas las cuentas vinculadas a las identidades expuestas.",
    ]
    if critical_high:
        recs.insert(0, f"Rote las credenciales de los {critical_high} hallazgo(s) alto(s)/crítico(s) de inmediato "
                       "y revise sesiones activas.")
    if public:
        recs.append(f"Evalúe la retirada o desindexación de los {public} registro(s) con exposición pública.")
    if downloadable:
        recs.append(f"Descargue e inspeccione los {downloadable} documento(s) descargable(s) en un entorno "
                    "aislado antes de clasificarlos.")
    recs.append("Preserve evidencia (IDs, fechas, hashes) y escale a legal/cumplimiento si hay datos personales.")
    return recs


def build_methodology(search_term: str,
                      search_id: Optional[str] = None,
                      lang: str = "es",
                      generated_utc: Optional[str] = None) -> List[Dict[str, str]]:
    """Filas de metodología y alcance como lista de {item, valor}."""
    lang = _lang(lang)
    if generated_utc is None:
        generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if lang == "en":
        return [
            {"item": "Source", "value": "Intelligence X (free.intelx.io), intelligent/search API"},
            {"item": "Query", "value": search_term or "N/A"},
            {"item": "Search ID", "value": search_id or "N/A"},
            {"item": "Parameters", "value": "lookuplevel 0 (strict) · maxresults 1000 · timeout 25s · sort 2 · media 0 (all)"},
            {"item": "Preview depth", "value": "previewlines=1: content truncated to one line per record"},
            {"item": "Cutoff (UTC)", "value": generated_utc},
            {"item": "Limitations", "value": "Free tier: result caps, no full-text retrieval, preview only. "
                                             "Confirm critical findings at the original source."},
        ]
    return [
        {"item": "Fuente", "value": "Intelligence X (free.intelx.io), API intelligent/search"},
        {"item": "Consulta", "value": search_term or "N/A"},
        {"item": "ID de búsqueda", "value": search_id or "N/A"},
        {"item": "Parámetros", "value": "lookuplevel 0 (estricto) · maxresults 1000 · timeout 25s · sort 2 · media 0 (todos)"},
        {"item": "Profundidad", "value": "previewlines=1: contenido truncado a una línea por registro"},
        {"item": "Corte (UTC)", "value": generated_utc},
        {"item": "Limitaciones", "value": "Plan gratuito: topes de resultados, sin texto completo, solo vista previa. "
                                          "Confirme hallazgos críticos en la fuente original."},
    ]


def get_glossary(lang: str = "es") -> List[Dict[str, str]]:
    """Glosario de términos del informe."""
    if _lang(lang) == "en":
        return [
            {"term": "Bucket", "definition": "IntelX collection a record belongs to (e.g. leaks, pastes). Indicates origin, not content."},
            {"term": "Media (0-32)", "definition": "Format code: 15 PDF, 16 Word, 22 ZIP, 24 text, 27/32 source code, among others."},
            {"term": "xscore", "definition": "IntelX risk score. This report maps >=80 critical, >=50 high, >=20 medium, >0 low."},
            {"term": "systemid / storageid", "definition": "Unique object ID / internal storage ID. systemid links to intelx.io/?s={id}."},
            {"term": "indexed", "definition": "Whether IntelX has the record indexed and searchable."},
            {"term": "TLP", "definition": "Traffic Light Protocol: agree on distribution (RED/AMBER/GREEN/CLEAR) before sharing this report."},
            {"term": "Disclaimer", "definition": "Preview metadata may be partial. Verify critical findings at the original source."},
        ]
    return [
        {"term": "Bucket", "definition": "Colección de IntelX a la que pertenece un registro (p. ej. leaks, pastes). Indica origen, no contenido."},
        {"term": "Media (0-32)", "definition": "Código de formato: 15 PDF, 16 Word, 22 ZIP, 24 texto, 27/32 código fuente, entre otros."},
        {"term": "xscore", "definition": "Puntuación de riesgo de IntelX. Este informe mapea >=80 crítica, >=50 alta, >=20 media, >0 baja."},
        {"term": "systemid / storageid", "definition": "ID único del objeto / ID interno de almacenamiento. systemid enlaza a intelx.io/?s={id}."},
        {"term": "indexed", "definition": "Si IntelX tiene el registro indexado y buscable."},
        {"term": "TLP", "definition": "Traffic Light Protocol: acuerde la distribución (RED/AMBER/GREEN/CLEAR) antes de compartir este informe."},
        {"term": "Disclaimer", "definition": "Los metadatos de vista previa pueden ser parciales. Verifique hallazgos críticos en la fuente original."},
    ]


def build_report_narrative(records: List[Dict[str, Any]],
                           search_term: str,
                           search_id: Optional[str] = None,
                           lang: str = "es",
                           top_n: int = 5) -> Dict[str, Any]:
    """Construye toda la narrativa del informe en un dict serializable."""
    lang = _lang(lang)
    records = records or []
    return {
        "lang": lang,
        "summary": build_executive_summary(records, search_term, lang),
        "severity_counts": severity_counts(records),
        "findings": top_findings(records, n=top_n, lang=lang),
        "iocs": collect_iocs(records),
        "recommendations": build_recommendations(records, lang),
        "methodology": build_methodology(search_term, search_id, lang),
        "glossary": get_glossary(lang),
    }

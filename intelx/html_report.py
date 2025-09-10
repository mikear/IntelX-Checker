"""HTML Report generation utilities."""

import os
from datetime import datetime
import json
import logging
from collections import Counter
from typing import List, Dict, Any

from .api import MEDIA_TYPE_MAP

logger = logging.getLogger(__name__)


def _analyze_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    analysis = {
        "total_results": len(records),
        "source_distribution": Counter(),
        "type_distribution": Counter(),
        "media_distribution": Counter(),
        "exposure_levels": {"public": 0, "indexed": 0, "sensitive": 0},
        "kpis": {
            "leaks_percentage": 0.0,
            "complete_metadata_percentage": 0.0,
            "downloadable_documents_count": 0
        },
        "temporal_data": Counter()
    }

    leaks_count = 0
    complete_metadata_count = 0
    downloadable_count = 0

    for r in records:
        bucket = r.get("bucket", "N/A")
        analysis["source_distribution"][bucket] += 1

        rtype = r.get("type", "N/A")
        analysis["type_distribution"][rtype] += 1

        media = r.get("media", "N/A")
        analysis["media_distribution"][media] += 1

        tags_lower = str(r.get("tags", "")).lower()
        if "public" in tags_lower:
            analysis["exposure_levels"]["public"] += 1
        if r.get("indexed", False):
            analysis["exposure_levels"]["indexed"] += 1
        if "sensitive" in tags_lower or (r.get("xscore", 0) or 0) > 70:
            analysis["exposure_levels"]["sensitive"] += 1

        if "leak" in bucket.lower() or "paste" in bucket.lower():
            leaks_count += 1

        if all(r.get(f) is not None for f in ["date", "name", "size", "type", "media", "bucket", "xscore", "systemid"]):
            complete_metadata_count += 1

        # Downloadable heuristic (documents / source code / containers)
        if isinstance(media, int) and media in {15, 16, 17, 18, 19, 22, 23, 24, 27, 32}:
            downloadable_count += 1

        date_str = r.get("date")
        if date_str and len(date_str) >= 7:
            analysis["temporal_data"][date_str[:7]] += 1

    total = analysis["total_results"] or 1
    if analysis["total_results"]:
        analysis["kpis"]["leaks_percentage"] = (leaks_count / total) * 100
        analysis["kpis"]["complete_metadata_percentage"] = (complete_metadata_count / total) * 100
    analysis["kpis"]["downloadable_documents_count"] = downloadable_count
    analysis["temporal_data"] = dict(sorted(analysis["temporal_data"].items()))
    return analysis


def _media_label(value: Any) -> str:
    if value is None:
        return "(Sin dato)"
    if isinstance(value, int):
        return MEDIA_TYPE_MAP.get(value, "Desconocido")
    if isinstance(value, str):
        try:
            iv = int(value)
            return MEDIA_TYPE_MAP.get(iv, "Desconocido")
        except ValueError:
            return value
    return str(value)


def generate_html_report(records: List[Dict[str, Any]], output_filepath: str, search_term: str, app_version: str = "2.0.0") -> str:
    """Genera un reporte HTML resumido.

    Cambios solicitados:
    - Eliminar gráfico de tipos de contenido.
    - Mostrar gráfico de evolución como barras por año (últimos 5 años, actual incluido).
    - Evitar 'undefined' en leyendas/etiquetas (se asignan labels explícitos).
    - Mantener gráfico de media (Top 5 + Otros) deduplicando etiquetas iguales.
    - Tabla: últimos 100 registros (más recientes primero).
    """
    analysis = _analyze_records(records)

    # Helper para top N + Otros
    def _top_n(counter: Counter, n: int = 5):
        items = counter.most_common()
        if not items:
            return [], []
        top = items[:n]
        rest = items[n:]
        labels = [k for k, _ in top]
        values = [v for _, v in top]
        if rest:
            labels.append("Otros")
            values.append(sum(v for _, v in rest))
        return labels, values

    # (Se elimina uso de tipos para gráficos, pero se mantiene análisis si se quisiera ampliar)
    # Media distribution top N (agrupando etiquetas duplicadas después de mapear)
    media_items = analysis["media_distribution"].items()
    # Mapear y agrupar por etiqueta textual
    grouped: Dict[str, int] = {}
    for raw, count in media_items:
        label = _media_label(raw)
        grouped[label] = grouped.get(label, 0) + count
    # Ordenar por frecuencia
    sorted_media = sorted(grouped.items(), key=lambda x: x[1], reverse=True)
    top = sorted_media[:5]
    rest = sorted_media[5:]
    media_labels = [l for l, _ in top]
    media_values = [v for _, v in top]
    if rest:
        media_labels.append("Otros")
        media_values.append(sum(v for _, v in rest))

    # Evolución temporal: construir serie de los últimos 5 años (60 meses) cronológica (asc)
    from datetime import date
    today = date.today()
    # Obtener primer día del mes actual
    current_month_start = date(today.year, today.month, 1)
    # Generar lista de meses (datetime.date) desde hace 59 meses hasta actual (60 total)
    months = []
    year = current_month_start.year
    month = current_month_start.month
    for _ in range(60):
        months.append(date(year, month, 1))
        # retroceder un mes
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    months.reverse()  # ahora ascendente
    month_labels = [m.strftime('%Y-%m') for m in months]
    month_counts = {lbl: 0 for lbl in month_labels}

    # Parsear fechas de registros y contar
    from datetime import datetime as _dt
    parsed_records = []
    for r in records:
        raw_date = r.get('date')
        parsed = None
        if isinstance(raw_date, str):
            # Intentos comunes
            candidates = [raw_date[:19], raw_date[:10]]  # ISO con tiempo / sólo fecha
            for c in candidates:
                for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                    try:
                        parsed = _dt.strptime(c, fmt)
                        break
                    except ValueError:
                        continue
                if parsed:
                    break
        if parsed:
            key_month = parsed.strftime('%Y-%m')
            if key_month in month_counts:
                month_counts[key_month] += 1
        parsed_records.append((parsed, r))

    temporal_labels = month_labels
    temporal_values = [month_counts[lbl] for lbl in month_labels]

    # Agregación anual (últimos 5 años) para gráfico de evolución
    from collections import OrderedDict
    years_ordered = OrderedDict()
    for lbl, val in zip(temporal_labels, temporal_values):
        yr = lbl.split('-')[0]
        years_ordered[yr] = years_ordered.get(yr, 0) + val
    # Limitar a últimos 5 años (en orden ascendente) y luego usar para gráfico
    all_years_sorted = sorted(years_ordered.keys())
    last5 = all_years_sorted[-5:]
    year_labels = last5
    year_values = [years_ordered[y] for y in year_labels]

    # Registros: últimos 100 (más recientes primero)
    # ordenar por fecha descendente (None al final)
    parsed_records.sort(key=lambda t: t[0] or _dt.min, reverse=True)
    recent_records = [r for _, r in parsed_records[:100]]

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # JSON para JS
    import json as _json
    js_data = {
        "mediaLabels": media_labels,
        "mediaValues": media_values,
        "yearLabels": year_labels,
        "yearValues": year_values,
    }
    js_blob = _json.dumps(js_data)

    html: List[str] = []
    add = html.append
    add("<!DOCTYPE html>")
    add("<html lang='es'>")
    add("<head>")
    add("<meta charset='UTF-8'>")
    add("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
    add(f"<title>Informe IntelX - {search_term}</title>")
    add("<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>")
    add("<style>")
    add("body{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:#f4f6f9;color:#2d3748;line-height:1.4;padding:18px;}")
    add(".wrap{max-width:1150px;margin:0 auto;background:#fff;border-radius:14px;box-shadow:0 6px 18px -6px rgba(0,0,0,.08);overflow:hidden;}")
    add("header{background:linear-gradient(120deg,#4F46E5,#6D28D9);color:#fff;padding:26px 32px;}header h1{margin:0;font-weight:400;font-size:1.9rem;}")
    add("header .meta{margin-top:6px;font-size:.8rem;opacity:.9;}")
    add("section{padding:26px 32px;border-top:1px solid #edf2f7;}section:first-of-type{border-top:none;}")
    add("h2{margin:0 0 18px;font-size:1.25rem;color:#4F46E5;font-weight:600;}")
    add(".grid-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:4px;}")
    add(".card{background:#f8fafc;padding:14px 16px;border-radius:10px;position:relative;overflow:hidden;}")
    add(".card h3{margin:0 0 6px;font-size:.75rem;letter-spacing:.5px;text-transform:uppercase;color:#64748b;font-weight:600;}")
    add(".card .val{font-size:1.4rem;font-weight:600;color:#3b82f6;}")
    add(".charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:26px;margin-top:8px;}")
    add(".chart-box{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;box-shadow:0 3px 6px -4px rgba(0,0,0,.08);}")
    add(".chart-box h3{margin:0 0 10px;font-size:.9rem;font-weight:600;color:#475569;}")
    add("table{width:100%;border-collapse:collapse;margin-top:6px;font-size:.8rem;}")
    add("th,td{padding:6px 8px;border-bottom:1px solid #e2e8f0;text-align:left;}")
    add("th{background:#4F46E5;color:#fff;font-weight:600;font-size:.7rem;letter-spacing:.5px;}")
    add("tbody tr:nth-child(even){background:#f8fafc;}")
    add("tbody tr:hover{background:#eef2ff;}")
    add(".badge{display:inline-block;padding:2px 6px;border-radius:6px;background:#e0e7ff;color:#3730a3;font-size:.65rem;font-weight:600;}")
    add(".note{margin-top:10px;font-size:.65rem;color:#64748b;}")
    add("footer{padding:18px 28px;background:#1e293b;color:#cbd5e1;font-size:.65rem;text-align:center;}")
    add("@media(max-width:760px){header,section{padding:22px 20px;}table{font-size:.72rem;}th{font-size:.63rem;}}");
    add("</style>")
    add("</head>")
    add("<body>")
    add("<div class='wrap'>")
    # Header
    add("<header>")
    add("<h1>Resumen de Búsqueda IntelX</h1>")
    add(f"<div class='meta'>Término: <strong>{search_term or '(vacío)'}</strong> · Resultados: {analysis['total_results']} · Generado: {timestamp}</div>")
    add(f"<div class='meta'>Versión: {app_version}</div>")
    add("</header>")

    # Estadísticas principales
    kpis = analysis['kpis']
    exp = analysis['exposure_levels']
    add("<section>")
    add("<h2>Indicadores Clave</h2>")
    add("<div class='grid-cards'>")
    add(f"<div class='card'><h3>Total</h3><div class='val'>{analysis['total_results']}</div></div>")
    add(f"<div class='card'><h3>Descargables</h3><div class='val'>{kpis['downloadable_documents_count']}</div></div>")
    add(f"<div class='card'><h3>Metadatos Completos</h3><div class='val'>{kpis['complete_metadata_percentage']:.1f}%</div></div>")
    add(f"<div class='card'><h3>Posibles Leaks</h3><div class='val'>{kpis['leaks_percentage']:.1f}%</div></div>")
    add(f"<div class='card'><h3>Exposición Pública</h3><div class='val'>{exp['public']}</div></div>")
    add(f"<div class='card'><h3>Sensible</h3><div class='val'>{exp['sensitive']}</div></div>")
    add("</div>")
    add("<div class='note'>Valores agregados y normalizados. Distribuciones limitadas al Top 5 + Otros.</div>")
    add("</section>")

    # Charts
    add("<section>")
    add("<h2>Visualizaciones</h2>")
    add("<div class='charts'>")
    add("  <div class='chart-box'><h3>Evolución Anual (Últimos 5 Años)</h3><canvas id='chartTemporal' height='180'></canvas></div>")
    add("  <div class='chart-box'><h3>Tipos de Media (Top 5)</h3><canvas id='chartMedia' height='180'></canvas></div>")
    add("</div>")
    add("</section>")

    # Tabla cronológica (limitada)
    add("<section>")
    add("<h2>Registros (Cronológico)</h2>")
    if recent_records:
        add("<table><thead><tr><th>Fecha</th><th>Nombre</th><th>Fuente</th><th>Tipo</th><th>Media</th><th>Punt.</th><th>Acción</th></tr></thead><tbody>")
        for r in recent_records:
            date = r.get('date', 'N/A')
            name_full = r.get('name', 'N/A')
            name = (name_full[:40] + '…') if len(str(name_full)) > 45 else name_full
            bucket = r.get('bucket', 'N/A')
            rtype = r.get('type', 'N/A')
            media_lbl = _media_label(r.get('media'))
            score = r.get('xscore', '–')
            sid = r.get('systemid', '')
            add("<tr>")
            add(f"<td>{date}</td><td>{name}</td><td>{bucket}</td><td>{rtype}</td><td>{media_lbl}</td><td>{score}</td><td><a class='badge' href='https://intelx.io/?s={sid}' target='_blank'>Ver</a></td>")
            add("</tr>")
        add("</tbody></table>")
        if len(records) > 100:
            add(f"<div class='note'>Mostrando últimos 100 de {len(records)} registros totales.</div>")
    else:
        add("<div class='note'>No se encontraron resultados.</div>")
    add("</section>")

    # Footer
    add("<footer>")
    add(f"Reporte HTML · IntelX Checker V2 · Versión {app_version} · Generado {timestamp}. Requiere conexión para cargar librerías externas (Chart.js).")
    add("</footer>")

    # Scripts (Chart.js)
    add("<script>")
    add(f"const DATA = {js_blob};")
    add("function makeChart(id,type,labels,data,extra){const ctx=document.getElementById(id).getContext('2d');return new Chart(ctx,{type:type,data:{labels:labels,datasets:[{label:'Registros',data:data,backgroundColor:['#6366F1','#8B5CF6','#EC4899','#F59E0B','#10B981','#6EE7B7','#F87171'],borderWidth:1,borderColor:'#ffffff40'}]},options:Object.assign({responsive:true,plugins:{legend:{display:true,position:'bottom',labels:{boxWidth:12,font:{size:10}}},tooltip:{callbacks:{label:(c)=>`${c.label}: ${c.formattedValue}`}}},scales:type==='bar'?{y:{beginAtZero:true,ticks:{precision:0,font:{size:10}},grid:{color:'#f1f5f9'}},x:{ticks:{font:{size:10}}}}:{}},extra||{})});}")
    add("document.addEventListener('DOMContentLoaded',()=>{makeChart('chartMedia','doughnut',DATA.mediaLabels,DATA.mediaValues,{cutout:'55%',plugins:{legend:{display:true}}});makeChart('chartTemporal','bar',DATA.yearLabels,DATA.yearValues);});")
    add("</script>")
    add("</div>")  # wrap
    add("</body>")
    add("</html>")

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, 'w', encoding='utf-8') as fh:
        fh.write("\n".join(html))
    logger.info(f"HTML report generated at: {output_filepath}")
    return output_filepath
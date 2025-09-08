"""Export helpers: CSV, JSON and HTML dashboard generation extracted from the legacy GUI.

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


def _clean_description(description: str) -> str:
    """Limpia una descripción removiendo contenido HTML/JavaScript no deseado."""
    if not description:
        return ""
    
    import re
    
    # Si la descripción contiene principalmente código JavaScript, descartarla
    js_indicators = ['function(', 'document.', 'try{', 'catch(', 'script', 'CDATA']
    js_count = sum(1 for indicator in js_indicators if indicator.lower() in description.lower())
    if js_count >= 2 or '/* <![CDATA[' in description:
        return ""  # Descartar descripciones que parecen ser código JavaScript
    
    # Remover código JavaScript de Cloudflare - más agresivo
    description = re.sub(r'/\*.*?\*/', '', description, flags=re.DOTALL)
    description = re.sub(r'<!\[CDATA\[.*?\]\]>', '', description, flags=re.DOTALL)
    description = re.sub(r'!function\(.*?\}\(\);', '', description, flags=re.DOTALL)
    
    # Remover cualquier código JavaScript restante
    description = re.sub(r'function\(.*?\}', '', description, flags=re.DOTALL)
    description = re.sub(r'try\{.*?\}catch\(.*?\)\{.*?\}', '', description, flags=re.DOTALL)
    description = re.sub(r'document\..*?;', '', description, flags=re.DOTALL)
    
    # Remover tags HTML básicos
    description = re.sub(r'<[^>]+>', '', description)
    
    # Remover entidades HTML
    description = description.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    description = description.replace('&#39;', "'").replace('&quot;', '"')
    
    # Remover código JavaScript restante
    description = re.sub(r'<script[^>]*>.*?</script>', '', description, flags=re.DOTALL | re.IGNORECASE)
    description = re.sub(r'javascript:[^\'"\s]*', '', description, flags=re.IGNORECASE)
    
    # Limpiar espacios extra y saltos de línea
    description = ' '.join(description.split())
    
    # Si la descripción queda vacía o es muy corta después de la limpieza, devolver string vacío
    if len(description.strip()) < 10:
        return ""
    
    # Limitar longitud
    return description.strip()[:200] + "..." if len(description.strip()) > 200 else description.strip()


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


def export_dashboard_html(data: dict, filename: Optional[str] = None, exports_dir: Optional[str] = None, search_term: Optional[str] = None, timestamp: Optional[str] = None) -> str:
    """
    Exporta un dashboard HTML con los datos proporcionados y detalles del análisis.
    data: Diccionario con las métricas y listas necesarias para el dashboard.
    """
    import shutil
    import json
    import re
    if exports_dir is None:
        exports_dir = _default_exports_dir('html')
    if not filename:
        filename = _timestamped_name('IntelX_Report_dashboard') + 'html'
    filepath = os.path.join(exports_dir, filename)
    template_path = os.path.join(exports_dir, 'dashboard_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Insertar datos reales en dashboardData
    dashboard_json = json.dumps(data, ensure_ascii=False)
    # Reemplazar el bloque dashboardData completo usando marcadores
    start_marker = '// DASHBOARDDATA_PLACEHOLDER_START'
    end_marker = '// DASHBOARDDATA_PLACEHOLDER_END'
    start_pos = html.find(start_marker)
    if start_pos != -1:
        end_pos = html.find(end_marker, start_pos)
        if end_pos != -1:
            end_pos += len(end_marker)
            # Reemplazar el bloque completo
            old_block = html[start_pos:end_pos]
            new_block = f'{start_marker}\n                    const dashboardData = {dashboard_json};\n                    {end_marker}'
            html = html.replace(old_block, new_block)

    # Agregar variables globales para search_term y timestamp
    if search_term:
        html = html.replace('<script>', f'<script>\n        window.searchTerm = "{search_term}";')
    if timestamp:
        html = html.replace('<script>', f'<script>\n        window.reportTimestamp = "{timestamp}";')
    # Insertar nombre del dominio analizado y fecha
    if search_term:
        html = html.replace('<h1>Dashboard IntelX Checker</h1>', f'<h1>Dashboard IntelX Checker</h1><h2 style="text-align:center;color:#0078d4;">Dominio Analizado: {search_term}</h2>')
    if timestamp:
        html = html.replace('<div class="subtitle">', f'<div class="subtitle">Reporte generado: {timestamp}<br>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.info('Dashboard HTML export written: %s', filepath)
    return filepath


def build_dashboard_data(records, lang='es'):
    """
    Construye el diccionario de métricas para el dashboard a partir de los resultados.
    """
    from collections import Counter, defaultdict
    import datetime
    if not records:
        return {
            'total': 0,
            'unique_domains': 0,
            'unique_buckets': 0,
            'unique_types': 0,
            'first_year': '-',
            'last_year': '-',
            'with_desc': 0,
            'buckets_labels': ["Sin datos" if lang == 'es' else "No data"],
            'buckets_values': [0],
            'tipos_labels': ["Sin datos" if lang == 'es' else "No data"],
            'tipos_values': [0],
            'years_labels': ["Sin datos" if lang == 'es' else "No data"],
            'years_values': [0],
            'ejemplos': [],
            'ejemplos_desc': [],
            'lang': lang
        }
    total = len(records)
    # Dominios únicos
    domains = set()
    for r in records:
        dom = r.get('Dominio', r.get('domain', r.get('Correo', r.get('email', ''))))
        if dom:
            domains.add(dom)
    unique_domains = len(domains)
    # Buckets únicos
    buckets = [r.get('Fuente (Bucket)', r.get('bucket', r.get('media', 'Desconocido'))) for r in records]
    unique_buckets = len(set(buckets))
    top_buckets = Counter(buckets).most_common(5)
    buckets_labels = [x[0] for x in top_buckets]
    buckets_values = [x[1] for x in top_buckets]
    # Tipos únicos
    tipos = [r.get('Tipo de Medio', r.get('type', r.get('media', 'Desconocido'))) for r in records]
    unique_types = len(set(tipos))
    top_tipos = Counter(tipos).most_common(5)
    tipos_labels = [x[0] for x in top_tipos]
    tipos_values = [x[1] for x in top_tipos]
    # Distribución por año (ordenada cronológicamente)
    years = []
    for r in records:
        fecha = r.get('Fecha Aproximada', r.get('date', r.get('added', '')))
        if fecha:
            try:
                year = str(datetime.datetime.fromisoformat(fecha[:10]).year)
            except Exception:
                year = fecha[:4]
            years.append(year)
    years_count = Counter(years)
    # Ordenar años cronológicamente
    sorted_years = sorted(years_count.items(), key=lambda x: x[0])
    years_labels = [x[0] for x in sorted_years]
    years_values = [x[1] for x in sorted_years]
    first_year = min(years) if years else '-'
    last_year = max(years) if years else '-'

    # Datos del último año
    current_year = str(datetime.datetime.now().year)
    last_year_data = years_count.get(current_year, 0)
    last_year_percentage = (last_year_data / total * 100) if total > 0 else 0

    # Métricas adicionales
    records_with_description = len([r for r in records if r.get('description', '').strip()])
    description_percentage = (records_with_description / total * 100) if total > 0 else 0

    # Severidad basada en tipos de datos
    sensitive_types = ['password', 'email', 'credit_card', 'social_security', 'phone']
    sensitive_count = 0
    for r in records:
        content = str(r.get('description', '')).lower()
        if any(sensitive in content for sensitive in sensitive_types):
            sensitive_count += 1
    sensitive_percentage = (sensitive_count / total * 100) if total > 0 else 0

    # Tendencia (comparación con año anterior)
    previous_year = str(int(current_year) - 1)
    previous_year_data = years_count.get(previous_year, 0)
    trend = "↑" if last_year_data > previous_year_data else "↓" if last_year_data < previous_year_data else "→"
    trend_percentage = ((last_year_data - previous_year_data) / previous_year_data * 100) if previous_year_data > 0 else 0

    # Ejemplos de títulos y descripciones (últimos 5)
    all_records = sorted(records, key=lambda x: x.get('Fecha Aproximada', x.get('date', x.get('added', ''))), reverse=True)
    titulos = [r.get('Titulo', r.get('name', '')) for r in all_records if r.get('Titulo', r.get('name', ''))][:5]
    
    # Limpiar descripciones y filtrar las vacías
    descripciones_raw = [r.get('description', '') for r in all_records if r.get('description', '')]
    descripciones_limpias = [_clean_description(desc) for desc in descripciones_raw if _clean_description(desc)]
    descripciones = descripciones_limpias[:5]
    
    ejemplos = titulos
    ejemplos_desc = descripciones
    with_desc = records_with_description
    return {
        'total': total,
        'unique_domains': unique_domains,
        'unique_buckets': unique_buckets,
        'unique_types': unique_types,
        'first_year': first_year,
        'last_year': last_year,
        'with_desc': with_desc,
        'description_percentage': round(description_percentage, 1),
        'sensitive_count': sensitive_count,
        'sensitive_percentage': round(sensitive_percentage, 1),
        'last_year_data': last_year_data,
        'last_year_percentage': round(last_year_percentage, 1),
        'trend': trend,
        'trend_percentage': round(trend_percentage, 1),
        'buckets_labels': buckets_labels,
        'buckets_values': buckets_values,
        'tipos_labels': tipos_labels,
        'tipos_values': tipos_values,
        'years_labels': years_labels,
        'years_values': years_values,
        'ejemplos': ejemplos,
        'ejemplos_desc': ejemplos_desc,
        'lang': lang
    }

#!/usr/bin/env python3
"""
Script para crear una versión offline completa del reporte
descargando Chart.js localmente
"""

import os
import sys
import json
import requests

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import InteractiveReportGenerator


def download_chartjs():
    """Descarga Chart.js para uso offline."""
    try:
        print("📥 Descargando Chart.js desde CDN...")
        url = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        chartjs_content = response.text
        print(f"✅ Chart.js descargado: {len(chartjs_content)} caracteres")
        return chartjs_content
        
    except Exception as e:
        print(f"❌ Error descargando Chart.js: {e}")
        return None


def create_offline_report():
    """Crea un reporte completamente offline."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print("🔍 Creando reporte offline completo...")
    
    # Descargar Chart.js
    chartjs_content = download_chartjs()
    if not chartjs_content:
        print("⚠️ Usando versión con CDN")
        chartjs_include = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>'
    else:
        chartjs_include = f'<script>\n{chartjs_content}\n</script>'
    
    # Crear el generador
    generator = InteractiveReportGenerator()
    
    # Generar componentes
    analysis = generator.data_processor.analyze_records(records)
    chart_data = generator.data_processor.prepare_chart_data(analysis)
    
    # Construir HTML modificado
    timestamp = "2025-09-11 15:30:00 UTC"
    search_term = "@supbienestar.gob.ar"
    
    kpi_cards = generator._build_kpi_cards(analysis)
    charts_html = generator.visualization_generator.generate_charts_html()
    charts_js = generator.visualization_generator.generate_charts_js(chart_data)
    table_html = generator.table_generator.generate_table_html(records)
    table_js = generator.table_generator.generate_table_js(records)
    css = generator.style_generator.generate_css()
    
    # HTML completo con Chart.js embebido
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IntelX Report - {search_term} (Offline)</title>
    {chartjs_include}
    <style>
    {css}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>📊 IntelX Intelligence Report (Offline)</h1>
            <div class="header-meta">
                <strong>Término de búsqueda:</strong> {search_term} • 
                <strong>Resultados:</strong> {analysis['total_results']} • 
                <strong>Generado:</strong> {timestamp} • 
                <strong>Versión:</strong> 2.0.0-offline
            </div>
        </header>

        <!-- KPI Section -->
        <section class="kpi-section">
            <div class="kpi-grid">
                {kpi_cards}
            </div>
        </section>

        <!-- Charts Section -->
        <section class="charts-section">
            <h2 class="section-title">📈 Análisis Visual</h2>
            {charts_html}
        </section>

        <!-- Table Section -->
        <section class="table-section">
            <h2 class="section-title">🔍 Datos Detallados</h2>
            {table_html}
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>
                🛡️ IntelX Checker V2 • Versión 2.0.0-offline • 
                Generado el {timestamp} • 
                Reporte interactivo standalone (100% offline)
            </p>
        </footer>
    </div>

    <script>
    // Verificar que Chart.js se cargó
    if (typeof Chart === 'undefined') {{
        console.error('Chart.js no se cargó correctamente');
        document.querySelector('.charts-section').innerHTML = '<h2>❌ Error: Chart.js no disponible</h2>';
    }} else {{
        console.log('Chart.js cargado correctamente, versión:', Chart.version);
    }}
    
    {charts_js}
    {table_js}
    </script>
</body>
</html>"""
    
    # Guardar archivo offline
    offline_file = "offline_report.html"
    with open(offline_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    file_size = os.path.getsize(offline_file) / 1024
    print(f"✅ Reporte offline creado: {offline_file}")
    print(f"📏 Tamaño: {file_size:.1f} KB")
    
    if chartjs_content:
        print("🌐 Incluye Chart.js embebido (100% offline)")
    else:
        print("🌐 Usa CDN para Chart.js (requiere internet)")
    
    return offline_file


if __name__ == '__main__':
    try:
        offline_file = create_offline_report()
        
        # Abrir en navegador
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath(offline_file)}')
        print(f"🌐 Abriendo {offline_file} en el navegador...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

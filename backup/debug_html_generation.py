#!/usr/bin/env python3
"""
Script para debuggear específicamente la generación completa de HTML
"""

import os
import sys
import json

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import InteractiveReportGenerator


def debug_html_generation():
    """Debug específico para la generación completa de HTML."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print("🔍 Debugging generación completa de HTML...")
    
    # Crear el generador
    generator = InteractiveReportGenerator()
    
    # Ejecutar los pasos uno por uno
    print("1. Analizando datos...")
    analysis = generator.data_processor.analyze_records(records)
    print(f"   ✅ Análisis completado")
    
    print("2. Preparando datos para gráficos...")
    chart_data = generator.data_processor.prepare_chart_data(analysis)
    print(f"   ✅ Datos preparados")
    
    print("3. Generando componentes HTML...")
    
    # KPI cards
    kpi_cards = generator._build_kpi_cards(analysis)
    print(f"   ✅ KPI cards: {len(kpi_cards)} caracteres")
    
    # Charts HTML
    charts_html = generator.visualization_generator.generate_charts_html()
    print(f"   ✅ Charts HTML: {len(charts_html)} caracteres")
    
    # Charts JS
    charts_js = generator.visualization_generator.generate_charts_js(chart_data)
    print(f"   ✅ Charts JS: {len(charts_js)} caracteres")
    
    # Table HTML
    table_html = generator.table_generator.generate_table_html(records)
    print(f"   ✅ Table HTML: {len(table_html)} caracteres")
    
    # Table JS
    table_js = generator.table_generator.generate_table_js(records)
    print(f"   ✅ Table JS: {len(table_js)} caracteres")
    
    # CSS
    css = generator.style_generator.generate_css()
    print(f"   ✅ CSS: {len(css)} caracteres")
    
    print("4. Ensamblando HTML completo...")
    html_content = generator._build_html_document(records, analysis, chart_data, "@supbienestar.gob.ar")
    print(f"   ✅ HTML completo: {len(html_content)} caracteres")
    
    # Verificar que el JavaScript está en el HTML final
    print("\n🔍 Verificando inclusión de JavaScript en HTML:")
    checks = [
        ("Chart.js CDN", "chart.js" in html_content.lower()),
        ("Charts JS incluido", "initializeCharts" in html_content),
        ("Table JS incluido", "initializeTable" in html_content),
        ("Chart data incluido", "chartData" in html_content),
        ("Canvas elements", "canvas id=" in html_content),
        ("Table elements", "table id=" in html_content),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    # Buscar específicamente el script tag
    script_start = html_content.find("<script>")
    script_end = html_content.find("</script>", script_start)
    
    if script_start != -1 and script_end != -1:
        script_content = html_content[script_start:script_end + 9]
        print(f"\n📝 Script tag encontrado:")
        print(f"   Posición: {script_start} - {script_end}")
        print(f"   Tamaño: {len(script_content)} caracteres")
        
        # Mostrar primeras líneas del script
        script_lines = script_content.split('\n')[:15]
        for i, line in enumerate(script_lines, 1):
            print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
    else:
        print("\n❌ No se encontró script tag!")
    
    # Guardar HTML para inspección manual
    debug_html_file = "debug_complete.html"
    with open(debug_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n💾 HTML completo guardado en: {debug_html_file}")
    
    return html_content


if __name__ == '__main__':
    debug_html_generation()

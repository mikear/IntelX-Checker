#!/usr/bin/env python3
"""
Script para debuggear específicamente la generación de JavaScript
"""

import os
import sys
import json

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import DataProcessor, VisualizationGenerator


def debug_javascript_generation():
    """Debug específico para la generación de JavaScript de gráficos."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print("🔍 Debugging generación de JavaScript...")
    
    # Análisis de datos
    print("1. Analizando datos...")
    analysis = DataProcessor.analyze_records(records)
    print(f"   ✅ Análisis completado: {analysis['total_results']} registros")
    
    # Preparación de datos para gráficos
    print("2. Preparando datos para gráficos...")
    chart_data = DataProcessor.prepare_chart_data(analysis)
    print(f"   ✅ Datos preparados: {len(chart_data)} tipos de gráficos")
    
    # Imprimir los datos para verificar que son correctos
    print("\n📊 Datos para gráficos:")
    for key, value in chart_data.items():
        if isinstance(value, dict) and 'labels' in value:
            print(f"   {key}: {len(value['labels'])} elementos")
            print(f"      Labels: {value['labels'][:3]}...")
            print(f"      Values: {value['values'][:3]}...")
        else:
            print(f"   {key}: {value}")
    
    # Generar JavaScript
    print("\n3. Generando JavaScript...")
    viz_gen = VisualizationGenerator()
    charts_js = viz_gen.generate_charts_js(chart_data)
    
    print(f"   ✅ JavaScript generado: {len(charts_js)} caracteres")
    
    # Mostrar parte del JavaScript generado
    print("\n📝 Primeras líneas del JavaScript:")
    lines = charts_js.split('\n')[:20]
    for i, line in enumerate(lines, 1):
        print(f"   {i:2d}: {line}")
    
    if len(lines) >= 20:
        print("   ... (truncado)")
    
    # Verificar que contiene las funciones necesarias
    print("\n🔍 Verificando contenido del JavaScript:")
    checks = [
        ("chartData", "chartData" in charts_js),
        ("createChart", "createChart" in charts_js),
        ("initializeCharts", "initializeCharts" in charts_js),
        ("dataTypesChart", "dataTypesChart" in charts_js),
        ("mediaChart", "mediaChart" in charts_js),
        ("sourcesChart", "sourcesChart" in charts_js),
        ("temporalChart", "temporalChart" in charts_js),
        ("DOMContentLoaded", "DOMContentLoaded" in charts_js),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    # Guardar JavaScript para inspección manual
    js_file = "debug_charts.js"
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(charts_js)
    print(f"\n💾 JavaScript guardado en: {js_file}")
    
    return charts_js


if __name__ == '__main__':
    debug_javascript_generation()

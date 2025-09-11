#!/usr/bin/env python3
"""
Genera reporte mejorado con gráficos SVG ajustados (texto no superpuesto, 5 años evolución)
"""

import os
import sys
import json
import webbrowser

# Agregar el directorio padre al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from intelx.interactive_report import InteractiveReportGenerator

def main():
    print("=== Generador de Reporte SVG Mejorado ===")
    
    # Leer datos reales del archivo JSON existente
    json_file = "reports/json/_at_supbienestar.gob.ar_20250910_213159.json"
    
    if not os.path.exists(json_file):
        print(f"❌ No se encontró el archivo: {json_file}")
        print("   Ejecuta primero una búsqueda en IntelX para generar datos.")
        return
    
    print(f"📂 Cargando datos desde: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # El archivo puede ser una lista directa o un diccionario
        if isinstance(data, list):
            records = data
            search_term = "@supbienestar.gob.ar"  # Usar un término por defecto
        else:
            records = data.get('records', [])
            search_term = data.get('search_term', '@supbienestar.gob.ar')
        
        print(f"📊 Registros cargados: {len(records)}")
        print(f"🔍 Término de búsqueda: {search_term}")
        
        if not records:
            print("❌ No hay registros para procesar")
            return
        
        # Crear generador de reportes
        print("🔧 Inicializando generador de reportes SVG mejorado...")
        generator = InteractiveReportGenerator()
        
        # Generar reporte
        print("🎨 Generando reporte HTML con 3 gráficos principales:")
        print("   • Distribución por Tipo de Dato")
        print("   • Fuentes Principales") 
        print("   • Evolución Temporal (5 años por trimestres)")
        print("   • Texto optimizado sin superposición")
        
        output_file = "exports/html/IntelX_SVG_Report_3_Graficos.html"
        generated_file = generator.generate_report(records, output_file, search_term)
        
        # Verificar que el archivo se generó
        if not os.path.exists(generated_file):
            print(f"❌ Error: No se pudo generar el archivo {generated_file}")
            return
        
        # Leer el contenido generado para verificaciones
        with open(generated_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verificar que el contenido se generó
        if not html_content or len(html_content) < 1000:
            print("❌ Error: Contenido HTML demasiado pequeño o vacío")
            return
        
        print(f"✅ Reporte generado: {len(html_content):,} caracteres")
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(generated_file)
        print(f"💾 Archivo guardado: {generated_file}")
        print(f"📏 Tamaño: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Verificaciones del contenido
        print("\n🔍 Verificaciones del reporte mejorado:")
        
        # 1. Verificar que tiene SVG (ahora solo 3 gráficos)
        svg_count = html_content.count('<svg')
        print(f"   • Gráficos SVG encontrados: {svg_count} (esperados: 3)")
        
        # 2. Verificar que NO tiene Chart.js
        has_chartjs = 'chart.js' in html_content.lower() or 'Chart(' in html_content
        print(f"   • Sin dependencia Chart.js: {'❌ Contiene Chart.js' if has_chartjs else '✅'}")
        
        # 3. Verificar que tiene tabla interactiva
        has_table = '<table' in html_content and 'id="resultsTable"' in html_content
        print(f"   • Tabla interactiva: {'✅' if has_table else '❌'}")
        
        # 4. Verificar que tiene filtros
        has_filters = 'id="typeFilter"' in html_content and 'id="sourceFilter"' in html_content
        print(f"   • Filtros: {'✅' if has_filters else '❌'}")
        
        # 5. Verificar evolución temporal de 5 años
        has_5years = 'Últimos 5 Años' in html_content
        print(f"   • Evolución temporal 5 años: {'✅' if has_5years else '❌'}")
        
        # 6. Verificar datos en gráficos
        path_count = html_content.count('<path')
        rect_count = html_content.count('<rect')
        circle_count = html_content.count('<circle')
        print(f"   • Elementos gráficos SVG: {path_count} paths, {rect_count} rectángulos, {circle_count} círculos")
        
        # 7. Verificar mejoras de texto
        font_size_9 = 'font-size: 9px' in html_content or 'font-size:9px' in html_content
        print(f"   • Texto optimizado (9px): {'✅' if font_size_9 else '❌'}")
        
        if svg_count >= 3 and not has_chartjs and has_table and has_filters and has_5years:
            print("\n✅ ¡Reporte SVG mejorado generado exitosamente!")
            
            # Abrir en navegador
            print("🌐 Abriendo reporte mejorado en navegador...")
            file_url = f"file:///{os.path.abspath(generated_file).replace(os.sep, '/')}"
            webbrowser.open(file_url)
            print(f"   URL: {file_url}")
            
            print("\n🎯 Configuración final:")
            print("   ✅ Solo 3 gráficos principales (sin tipos de media)")
            print("   ✅ Distribución por Tipo de Dato (donut)")
            print("   ✅ Fuentes Principales (barras)")
            print("   ✅ Evolución Temporal - ANCHO COMPLETO (línea)")
            print("   ✅ Layout: 2 gráficos arriba + temporal abajo full-width")
            print("   ✅ Gráfico temporal: 800x350px para mejor legibilidad")
        else:
            print("\n⚠️  Reporte generado con advertencias")
        
        print(f"\n📍 Archivo final: {os.path.abspath(generated_file)}")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

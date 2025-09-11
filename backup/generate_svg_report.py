#!/usr/bin/env python3
"""
Genera reporte interactivo con gráficos SVG puros (sin Chart.js)
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
    print("=== Generador de Reporte SVG Interactivo ===")
    
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
        print("🔧 Inicializando generador de reportes SVG...")
        generator = InteractiveReportGenerator()
        
        # Generar reporte
        print("🎨 Generando reporte HTML con gráficos SVG...")
        output_file = "exports/html/IntelX_SVG_Report.html"
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
        
        # Guardar archivo (ya se genera por el método)
        # output_file ya está definido arriba
        os.makedirs(os.path.dirname(generated_file), exist_ok=True)
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(generated_file)
        print(f"💾 Archivo guardado: {generated_file}")
        print(f"📏 Tamaño: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Verificaciones del contenido
        print("\n🔍 Verificaciones del reporte:")
        
        # 1. Verificar que tiene SVG
        svg_count = html_content.count('<svg')
        print(f"   • Gráficos SVG encontrados: {svg_count}")
        
        # 2. Verificar que NO tiene Chart.js
        has_chartjs = 'chart.js' in html_content.lower() or 'Chart(' in html_content
        print(f"   • Sin dependencia Chart.js: {'❌ Contiene Chart.js' if has_chartjs else '✅'}")
        
        # 3. Verificar que tiene tabla interactiva
        has_table = '<table' in html_content and 'id="resultsTable"' in html_content
        print(f"   • Tabla interactiva: {'✅' if has_table else '❌'}")
        
        # 4. Verificar que tiene filtros
        has_filters = 'id="typeFilter"' in html_content and 'id="sourceFilter"' in html_content
        print(f"   • Filtros: {'✅' if has_filters else '❌'}")
        
        # 5. Verificar que tiene CSS moderno
        has_modern_css = 'border-radius:' in html_content and 'box-shadow:' in html_content
        print(f"   • CSS moderno: {'✅' if has_modern_css else '❌'}")
        
        # 6. Verificar datos en gráficos
        path_count = html_content.count('<path')
        rect_count = html_content.count('<rect')
        circle_count = html_content.count('<circle')
        print(f"   • Elementos gráficos SVG: {path_count} paths, {rect_count} rectángulos, {circle_count} círculos")
        
        if svg_count >= 4 and not has_chartjs and has_table and has_filters:
            print("\n✅ ¡Reporte SVG generado exitosamente!")
            
            # Abrir en navegador
            print("🌐 Abriendo reporte en navegador...")
            file_url = f"file:///{os.path.abspath(generated_file).replace(os.sep, '/')}"
            webbrowser.open(file_url)
            print(f"   URL: {file_url}")
        else:
            print("\n⚠️  Reporte generado con advertencias")
        
        print(f"\n📍 Archivo final: {os.path.abspath(generated_file)}")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

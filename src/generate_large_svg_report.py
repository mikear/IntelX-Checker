// Mover a src/generate_large_svg_report.py
#!/usr/bin/env python3
"""
Genera reporte con gráficos SVG ampliados para mejor visibilidad
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
    print("=== Generador de Reporte SVG AMPLIADO ===")
    
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
        print("🔧 Inicializando generador de reportes SVG AMPLIADO...")
        generator = InteractiveReportGenerator()
        
        # Generar reporte
        print("🎨 Generando reporte HTML con gráficos GRANDES:")
        print("   📏 Gráficos normales: 500x400px (vs 400x300px)")
        print("   📏 Gráfico temporal: 1000x450px (vs 800x350px)")
        print("   📏 Contenedores: 450px altura (vs 350px)")
        print("   📏 Temporal container: 550px altura (vs 450px)")
        print("   🔤 Fuentes más grandes: 11px texto + 16px títulos")
        
        output_file = "exports/html/IntelX_SVG_Report_AMPLIADO.html"
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
        print("\n🔍 Verificaciones del reporte AMPLIADO:")
        
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
        
        # 6. Verificar tamaños ampliados
        has_large_svg = 'width="500"' in html_content and 'width="1000"' in html_content
        print(f"   • Gráficos ampliados (500px/1000px): {'✅' if has_large_svg else '❌'}")
        
        # 7. Verificar fuentes más grandes
        has_large_fonts = 'font-size: 11px' in html_content and 'font-size: 16px' in html_content
        print(f"   • Fuentes más grandes (11px/16px): {'✅' if has_large_fonts else '❌'}")
        
        # 8. Verificar datos en gráficos
        path_count = html_content.count('<path')
        rect_count = html_content.count('<rect')
        circle_count = html_content.count('<circle')
        print(f"   • Elementos gráficos SVG: {path_count} paths, {rect_count} rectángulos, {circle_count} círculos")
        
        if svg_count >= 3 and not has_chartjs and has_table and has_filters and has_5years and has_large_svg:
            print("\n✅ ¡Reporte SVG AMPLIADO generado exitosamente!")
            
            # Abrir en navegador
            print("🌐 Abriendo reporte ampliado en navegador...")
            file_url = f"file:///{os.path.abspath(generated_file).replace(os.sep, '/')}"
            webbrowser.open(file_url)
            print(f"   URL: {file_url}")
            
            print("\n🎯 Mejoras de tamaño implementadas:")
            print("   📈 Gráficos normales: +25% tamaño (500x400px)")
            print("   📈 Gráfico temporal: +25% ancho, +28% alto (1000x450px)")
            print("   📈 Contenedores: +28% altura (450px/550px)")
            print("   📈 Fuentes: +22% texto, +23% títulos (11px/16px)")
            print("   📈 Leyendas: mejor espaciado y más largas")
        else:
            print("\n⚠️  Reporte generado con advertencias")
        
        print(f"\n📍 Archivo final: {os.path.abspath(generated_file)}")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

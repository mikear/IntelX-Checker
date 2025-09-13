// Mover a src/generate_report.py
#!/usr/bin/env python3
"""
Generador de Reportes SVG - IntelX Checker
Genera reportes interactivos HTML con gráficos SVG sin dependencias externas
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
    print("=== IntelX Checker - Generador de Reportes SVG ===")
    
    # Buscar archivos JSON más recientes
    json_files = []
    for root, dirs, files in os.walk("reports"):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print("❌ No se encontraron archivos JSON de reportes.")
        print("   Ejecuta primero una búsqueda en IntelX para generar datos.")
        return
    
    # Usar el archivo más reciente
    json_file = max(json_files, key=os.path.getmtime)
    print(f"📂 Usando archivo más reciente: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # El archivo puede ser una lista directa o un diccionario
        if isinstance(data, list):
            records = data
            search_term = os.path.basename(json_file).replace('.json', '').replace('_', ' ')
        else:
            records = data.get('records', [])
            search_term = data.get('search_term', os.path.basename(json_file).replace('.json', ''))
        
        print(f"📊 Registros cargados: {len(records)}")
        print(f"🔍 Término de búsqueda: {search_term}")
        
        if not records:
            print("❌ No hay registros para procesar")
            return
        
        # Crear generador de reportes
        print("🔧 Generando reporte interactivo con gráficos SVG...")
        generator = InteractiveReportGenerator()
        
        # Generar reporte
        timestamp = json_file.split('_')[-1].replace('.json', '') if '_' in json_file else 'latest'
        output_file = f"exports/html/IntelX_Report_{timestamp}.html"
        generated_file = generator.generate_report(records, output_file, search_term)
        
        # Verificar que el archivo se generó
        if not os.path.exists(generated_file):
            print(f"❌ Error: No se pudo generar el archivo {generated_file}")
            return
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(generated_file)
        print(f"✅ Reporte generado exitosamente!")
        print(f"💾 Archivo: {generated_file}")
        print(f"📏 Tamaño: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Abrir en navegador
        print("🌐 Abriendo reporte en navegador...")
        file_url = f"file:///{os.path.abspath(generated_file).replace(os.sep, '/')}"
        webbrowser.open(file_url)
        
        print("\n🎯 Características del reporte:")
        print("   ✅ 3 gráficos SVG interactivos (sin dependencias externas)")
        print("   ✅ Tabla filtrable con datos detallados")
        print("   ✅ Diseño responsivo y moderno")
        print("   ✅ Funciona completamente offline")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

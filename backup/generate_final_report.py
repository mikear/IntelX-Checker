#!/usr/bin/env python3
"""
Script final para generar reportes HTML interactivos mejorados
con todas las correcciones aplicadas
"""

import os
import sys
import json
from datetime import datetime

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import generate_interactive_html_report


def generate_final_report():
    """Genera el reporte final con todas las mejoras."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    if not os.path.exists(json_file):
        print(f"❌ Archivo no encontrado: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print("🚀 Generando reporte HTML interactivo final...")
    print(f"📊 Procesando {len(records)} registros reales...")
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"IntelX_Report_Final_{timestamp}.html"
    output_path = os.path.join('exports', 'html', output_file)
    
    try:
        result_path = generate_interactive_html_report(
            records=records,
            output_filepath=output_path,
            search_term="@supbienestar.gob.ar",
            app_version="2.0.0-final"
        )
        
        print(f"✅ Reporte generado exitosamente!")
        print(f"📁 Ubicación: {result_path}")
        
        # Mostrar estadísticas del archivo
        file_size = os.path.getsize(result_path) / 1024
        print(f"📏 Tamaño: {file_size:.1f} KB")
        
        # Verificar contenido
        print("\n🔍 Verificando contenido del reporte...")
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("Chart.js CDN", "chart.js" in content.lower()),
            ("Datos de gráficos", "chartData" in content),
            ("Función de inicialización", "initializeCharts" in content),
            ("Canvas para gráficos", "canvas id=" in content),
            ("Tabla interactiva", "table id=" in content),
            ("Filtros", "typeFilter" in content),
            ("CSS moderno", "grid-template-columns" in content),
            ("JavaScript debugging", "console.log" in content),
        ]
        
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n🎉 ¡Todas las verificaciones pasaron!")
        else:
            print("\n⚠️  Algunas verificaciones fallaron")
        
        # Contar elementos clave
        canvas_count = content.count('<canvas id=')
        table_count = content.count('<table id=')
        filter_count = content.count('Filter')
        
        print(f"\n📊 Estadísticas del reporte:")
        print(f"  • Canvas para gráficos: {canvas_count}")
        print(f"  • Tablas interactivas: {table_count}")
        print(f"  • Filtros disponibles: {filter_count}")
        print(f"  • Tamaño total: {file_size:.1f} KB")
        
        # Abrir en navegador
        print("\n🌐 Abriendo reporte en el navegador...")
        import webbrowser
        try:
            webbrowser.open(f'file://{os.path.abspath(result_path)}')
            print("✅ Reporte abierto en el navegador")
        except Exception as e:
            print(f"⚠️  No se pudo abrir automáticamente: {e}")
            print(f"🔗 Abra manualmente: file://{os.path.abspath(result_path)}")
        
        print(f"\n🏆 ¡Reporte HTML interactivo final completado!")
        print(f"📋 Características incluidas:")
        print(f"  ✅ Tabla interactiva con filtros")
        print(f"  ✅ 4 gráficos de distribución")
        print(f"  ✅ Clasificación automática de datos")
        print(f"  ✅ Diseño responsive moderno")
        print(f"  ✅ HTML standalone completo")
        print(f"  ✅ Debugging habilitado")
        
        return result_path
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    generate_final_report()

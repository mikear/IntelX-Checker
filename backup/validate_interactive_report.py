#!/usr/bin/env python3
"""
Script de validación del sistema de reportes HTML interactivos
usando datos reales existentes en el proyecto
"""

import os
import sys
import json
from datetime import datetime

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import generate_interactive_html_report


def load_existing_data():
    """Carga datos existentes de los archivos JSON de exports."""
    
    json_dir = os.path.join(os.path.dirname(__file__), 'reports', 'json')
    
    if not os.path.exists(json_dir):
        print(f"❌ Directorio no encontrado: {json_dir}")
        return None
    
    # Buscar archivos JSON
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ No se encontraron archivos JSON en: {json_dir}")
        return None
    
    # Usar el archivo más reciente
    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(json_dir, f)))
    filepath = os.path.join(json_dir, latest_file)
    
    print(f"📄 Cargando datos desde: {latest_file}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Cargados {len(data)} registros reales")
        return data, latest_file
    
    except Exception as e:
        print(f"❌ Error cargando archivo JSON: {e}")
        return None


def main():
    """Función principal de validación."""
    print("🔍 Validando sistema de reportes HTML con datos reales...")
    
    # Cargar datos existentes
    result = load_existing_data()
    if result is None:
        print("⚠️  No se pudieron cargar datos reales, usando datos mínimos de prueba")
        # Crear datos mínimos para validación
        records = [
            {
                'systemid': 'test_001',
                'name': 'test@example.com',
                'bucket': 'test_source',
                'type': 'email',
                'media': 1,
                'date': '2025-09-11T14:57:00',
                'xscore': 75
            }
        ]
        search_term = "test validation"
    else:
        records, filename = result
        # Extraer término de búsqueda del nombre del archivo
        search_term = filename.replace('_at_', '@').replace('_dot_', '.').split('_')[0]
    
    # Definir ruta de salida
    output_dir = os.path.join(os.path.dirname(__file__), 'exports', 'html')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'Validation_Report_{timestamp}.html')
    
    # Generar reporte
    print("🔨 Generando reporte HTML interactivo con datos reales...")
    try:
        result_path = generate_interactive_html_report(
            records=records,
            output_filepath=output_file,
            search_term=search_term,
            app_version="2.0.0-validation"
        )
        
        print(f"✅ Reporte generado exitosamente!")
        print(f"📁 Ubicación: {result_path}")
        print(f"📏 Tamaño del archivo: {os.path.getsize(result_path) / 1024:.1f} KB")
        print(f"📊 Registros procesados: {len(records)}")
        
        # Mostrar estadísticas básicas
        if len(records) > 0:
            print("\n📋 Estadísticas de los datos:")
            
            # Contar tipos únicos
            types = set(str(r.get('type', 'N/A')) for r in records)
            print(f"  • Tipos únicos: {len(types)} ({', '.join(sorted(types)[:5])}{'...' if len(types) > 5 else ''})")
            
            # Contar fuentes únicas
            sources = set(str(r.get('bucket', 'N/A')) for r in records)
            print(f"  • Fuentes únicas: {len(sources)} ({', '.join(sorted(sources)[:3])}{'...' if len(sources) > 3 else ''})")
            
            # Puntuaciones
            scores = [r.get('xscore', 0) for r in records if r.get('xscore') is not None and str(r.get('xscore')).isdigit()]
            if scores:
                scores = [int(s) if isinstance(s, str) else s for s in scores]
                avg_score = sum(scores) / len(scores)
                print(f"  • Puntuación promedio: {avg_score:.1f}")
                print(f"  • Puntuación máxima: {max(scores)}")
        
        # Intentar abrir en el navegador
        print("\n🌐 Intentando abrir en el navegador...")
        import webbrowser
        try:
            webbrowser.open(f'file://{os.path.abspath(result_path)}')
            print("✅ Reporte abierto en el navegador")
        except Exception as e:
            print(f"⚠️  No se pudo abrir automáticamente: {e}")
            print(f"🔗 Abra manualmente: file://{os.path.abspath(result_path)}")
        
        # Validar integridad del archivo
        print("\n🔍 Validando integridad del archivo...")
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validations = [
            ('Chart.js CDN', 'chart.js' in content.lower()),
            ('Tabla HTML', '<table' in content and '</table>' in content),
            ('JavaScript para filtros', 'applyFilters' in content),
            ('CSS moderno', 'Segoe UI' in content),
            ('Datos JSON', 'const tableData' in content),
            ('Responsive design', '@media' in content)
        ]
        
        all_valid = True
        for check, result in validations:
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
            if not result:
                all_valid = False
        
        if all_valid:
            print("\n🎉 ¡Validación completa exitosa!")
        else:
            print("\n⚠️  Algunas validaciones fallaron")
        
        return 0 if all_valid else 1
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

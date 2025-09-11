#!/usr/bin/env python3
"""
Script de debugging para diagnósticar problemas con datos reales
"""

import os
import sys
import json
from datetime import datetime

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import DataProcessor


def debug_data_processing():
    """Debug del procesamiento de datos."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    if not os.path.exists(json_file):
        print(f"❌ Archivo no encontrado: {json_file}")
        return
    
    print("🔍 Cargando datos reales para debugging...")
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"📊 Total de registros: {len(records)}")
    
    # Analizar el primer registro
    if records:
        print("\n🔍 Analizando primer registro:")
        first_record = records[0]
        for key, value in first_record.items():
            print(f"  {key}: {value} (tipo: {type(value).__name__})")
    
    # Analizar varios registros para ver la variedad
    print(f"\n🔍 Analizando campos clave en primeros 10 registros:")
    
    for i, record in enumerate(records[:10]):
        print(f"\nRegistro {i+1}:")
        print(f"  name: {record.get('name', 'N/A')}")
        print(f"  type: {record.get('type', 'N/A')} (tipo: {type(record.get('type')).__name__})")
        print(f"  media: {record.get('media', 'N/A')} (tipo: {type(record.get('media')).__name__})")
        print(f"  bucket: {record.get('bucket', 'N/A')}")
        print(f"  date: {record.get('date', 'N/A')}")
        print(f"  xscore: {record.get('xscore', 'N/A')}")
        
        # Probar clasificación de datos
        data_type = DataProcessor._classify_data_type(record)
        print(f"  -> Clasificado como: {data_type}")
    
    # Probar análisis completo
    print(f"\n🔨 Probando análisis completo...")
    analysis = None
    try:
        analysis = DataProcessor.analyze_records(records)
        print(f"✅ Análisis completado:")
        print(f"  Total: {analysis['total_results']}")
        print(f"  Tipos únicos: {len(analysis['type_distribution'])}")
        print(f"  Media únicos: {len(analysis['media_distribution'])}")
        print(f"  Fuentes únicas: {analysis['unique_sources']}")
        print(f"  Datos temporales: {len(analysis['temporal_data'])}")
        
        # Mostrar distribuciones
        print(f"\n📊 Distribución de tipos:")
        for tipo, count in analysis['type_distribution'].most_common(5):
            print(f"  {tipo}: {count}")
        
        print(f"\n📊 Distribución de tipos de datos clasificados:")
        for tipo, count in analysis['data_types'].most_common(5):
            print(f"  {tipo}: {count}")
            
        print(f"\n📊 Distribución de media:")
        for media, count in analysis['media_distribution'].most_common(5):
            print(f"  {media}: {count}")
            
        print(f"\n📊 Distribución de fuentes:")
        for fuente, count in analysis['source_distribution'].most_common(5):
            print(f"  {fuente}: {count}")
            
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()
    
    # Probar preparación de datos para gráficos
    print(f"\n🎨 Probando preparación de datos para gráficos...")
    try:
        if analysis is not None:
            chart_data = DataProcessor.prepare_chart_data(analysis)
            print(f"✅ Datos para gráficos preparados:")
            print(f"  Data types labels: {chart_data['dataTypes']['labels']}")
            print(f"  Data types values: {chart_data['dataTypes']['values']}")
            print(f"  Media labels: {chart_data['media']['labels']}")
            print(f"  Media values: {chart_data['media']['values']}")
            print(f"  Temporal labels: {len(chart_data['temporal']['labels'])} meses")
            print(f"  Temporal values: {chart_data['temporal']['values']}")
        else:
            print("⚠️ Análisis no disponible, saltando prueba de gráficos")
        
    except Exception as e:
        print(f"❌ Error en preparación de gráficos: {e}")
        import traceback
        traceback.print_exc()


def debug_table_generation():
    """Debug de la generación de tabla."""
    
    # Cargar datos reales
    json_file = os.path.join(os.path.dirname(__file__), 'reports', 'json', '_at_supbienestar.gob.ar_20250910_213159.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"\n🔍 Probando procesamiento de registros para tabla...")
    
    from intelx.interactive_report import TableGenerator
    
    try:
        # Probar solo con primeros 5 registros
        test_records = records[:5]
        processed = TableGenerator._process_records_for_table(test_records)
        
        print(f"✅ Registros procesados para tabla: {len(processed)}")
        
        for i, record in enumerate(processed):
            print(f"\nRegistro procesado {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"❌ Error procesando registros para tabla: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("🔧 DEBUGGING DEL SISTEMA DE REPORTES")
    print("=" * 50)
    
    debug_data_processing()
    debug_table_generation()
    
    print("\n" + "=" * 50)
    print("🎯 Debug completado")

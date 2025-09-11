#!/usr/bin/env python3
"""
Script de demostración para el nuevo sistema de reportes HTML interactivos
"""

import os
import sys
import json
from datetime import datetime, timedelta
import random

# Añadir el directorio padre al path para importar el módulo intelx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelx.interactive_report import generate_interactive_html_report

def generate_sample_data():
    """Genera datos de muestra para la demostración."""
    
    # Tipos de datos simulados
    data_types = ['email', 'domain', 'ip', 'document', 'database', 'source_code']
    sources = ['pastebin.com', 'github.com', 'telegram', 'leaked_database', 'forum', 'darkweb']
    media_types = [1, 15, 16, 17, 18, 19, 22, 23, 24, 27, 32]
    
    records = []
    
    # Generar 150 registros de muestra
    for i in range(150):
        # Fecha aleatoria en los últimos 18 meses
        days_ago = random.randint(0, 540)
        date = datetime.now() - timedelta(days=days_ago)
        
        # Tipo de dato aleatorio
        data_type = random.choice(data_types)
        
        # Generar nombre basado en el tipo
        if data_type == 'email':
            domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'organization.org']
            name = f"user{i}@{random.choice(domains)}"
        elif data_type == 'domain':
            name = f"subdomain{i}.example-{random.randint(1,100)}.com"
        elif data_type == 'ip':
            name = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        elif data_type == 'document':
            extensions = ['.pdf', '.doc', '.xls', '.ppt', '.txt']
            name = f"document_{i}{random.choice(extensions)}"
        elif data_type == 'database':
            name = f"database_backup_{i}.sql"
        else:
            name = f"source_file_{i}.py"
        
        # Crear registro
        record = {
            'systemid': f"sys_{i:06d}",
            'storageid': f"storage_{i:06d}",
            'name': name,
            'bucket': random.choice(sources),
            'type': data_type,
            'media': random.choice(media_types),
            'date': date.strftime('%Y-%m-%dT%H:%M:%S'),
            'size': random.randint(1024, 10485760),  # 1KB to 10MB
            'xscore': random.randint(0, 100),
            'indexed': random.choice([True, False]),
            'tags': random.choice(['public', 'private', 'sensitive', 'leaked', '']),
            'mimetype': 'application/octet-stream'
        }
        
        records.append(record)
    
    return records

def main():
    """Función principal de demostración."""
    print("🚀 Generando reporte HTML interactivo de demostración...")
    
    # Generar datos de muestra
    print("📊 Generando datos de muestra...")
    sample_records = generate_sample_data()
    print(f"✅ Generados {len(sample_records)} registros de muestra")
    
    # Definir ruta de salida
    output_dir = os.path.join(os.path.dirname(__file__), 'exports', 'html')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'Demo_Report_{timestamp}.html')
    
    # Generar reporte
    print("🔨 Generando reporte HTML interactivo...")
    try:
        result_path = generate_interactive_html_report(
            records=sample_records,
            output_filepath=output_file,
            search_term="demo@company.com",
            app_version="2.0.0-demo"
        )
        
        print(f"✅ Reporte generado exitosamente!")
        print(f"📁 Ubicación: {result_path}")
        print(f"📏 Tamaño del archivo: {os.path.getsize(result_path) / 1024:.1f} KB")
        
        # Intentar abrir en el navegador
        print("\n🌐 Intentando abrir en el navegador...")
        import webbrowser
        try:
            webbrowser.open(f'file://{os.path.abspath(result_path)}')
            print("✅ Reporte abierto en el navegador")
        except Exception as e:
            print(f"⚠️  No se pudo abrir automáticamente: {e}")
            print(f"🔗 Abra manualmente: file://{os.path.abspath(result_path)}")
        
        print("\n📋 Características del reporte:")
        print("  • 📊 Gráficos interactivos (Chart.js)")
        print("  • 🔍 Tabla con filtros y búsqueda")
        print("  • 📱 Diseño responsive")
        print("  • 🎨 Estilo moderno Windows 11/macOS")
        print("  • 📦 Archivo HTML standalone")
        print("  • ⚡ Interactividad completa")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

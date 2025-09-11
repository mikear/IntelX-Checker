# 📊 Sistema de Reportes HTML Interactivos v2.0

> **Nuevo**: Reportes modernos, interactivos y completamente standalone para IntelX Checker

## 🚀 ¿Qué es esto?

El nuevo sistema de reportes HTML transforma completamente la experiencia de visualización de resultados de IntelX. En lugar de reportes estáticos, ahora obtienes una aplicación web interactiva completa en un solo archivo HTML.

## ✨ Características Destacadas

### 🎯 **Interactividad Total**
- **Filtros en tiempo real**: Por tipo, fuente, fecha y búsqueda textual
- **Ordenamiento dinámico**: Haz clic en cualquier columna
- **Gráficos interactivos**: Hover, zoom, y más usando Chart.js
- **Responsive**: Perfecto en móvil, tablet y desktop

### 📊 **Visualizaciones Inteligentes**
- **Distribución de tipos de datos**: Email, IP, dominios, documentos, etc.
- **Análisis temporal**: Evolución de los hallazgos en el tiempo
- **Top fuentes**: De dónde provienen más datos
- **KPIs automáticos**: Métricas clave calculadas automáticamente

### 🎨 **Diseño Moderno**
- **Windows 11/macOS compatible**: Tipografía y colores modernos
- **Minimalista y limpio**: Enfoque en los datos importantes
- **Accesible**: Colores y contrastes optimizados
- **Profesional**: Listo para presentaciones ejecutivas

### 📦 **Standalone y Portable**
- **Un solo archivo**: Todo incluido en un .html
- **Sin instalaciones**: Funciona en cualquier navegador
- **Compartible**: Envía por email o sube a cualquier servidor
- **Offline-friendly**: Una vez cargado, funciona sin internet

## 🚀 Inicio Rápido

### Desde la Interfaz GUI
```
1. Ejecuta una búsqueda en IntelX Checker
2. Ve al menú "Archivo" > "Exportar a HTML..."
3. ¡El reporte interactivo se abre automáticamente!
```

### Programáticamente
```python
from intelx.interactive_report import generate_interactive_html_report

# Genera un reporte completo
file_path = generate_interactive_html_report(
    records=your_search_results,
    output_filepath="mi_reporte.html",
    search_term="example@domain.com"
)
```

### Probando con Datos de Demo
```bash
python demo_interactive_report.py
```

## 📋 Guía de Uso

### 🔍 **Filtros Avanzados**

1. **Por Tipo de Dato**
   - Email, Dominio, IP, Documento, Código, Base de Datos, Otro
   - Clasificación automática basada en contenido

2. **Por Fuente**
   - Dropdown con todas las fuentes encontradas
   - Ej: GitHub, Pastebin, Telegram, etc.

3. **Por Fecha**
   - Selector de rango: "Desde" y "Hasta"
   - Formato: YYYY-MM-DD

4. **Búsqueda Textual**
   - Busca en nombre, tipo, fuente y media
   - Actualización en tiempo real

### 📊 **Interpretando los Gráficos**

#### Distribución por Tipo de Dato
- **Donut Chart**: Muestra qué tipos de datos son más comunes
- **Hover**: Muestra valores exactos
- **Colores únicos**: Cada tipo tiene su color distintivo

#### Evolución Temporal
- **Line Chart**: Tendencia de hallazgos en los últimos 12 meses
- **Picos**: Indican eventos o campañas específicas
- **Tendencias**: Ayuda a identificar patrones temporales

#### Top Fuentes
- **Bar Chart**: Principales fuentes de datos
- **Ordenado**: De mayor a menor cantidad
- **Insights**: Identifica dónde están más expuestos

### 🏷️ **Sistema de Etiquetas**

#### Tipos de Datos
- 🟦 **Email**: Direcciones de correo electrónico
- 🟩 **Dominio**: Nombres de dominio y subdominios
- 🟨 **IP**: Direcciones IP públicas y privadas
- 🟣 **Documento**: PDFs, Office, archivos descargables
- 🟪 **Código**: Scripts, archivos fuente
- 🟥 **Base de Datos**: Dumps, backups SQL
- ⬜ **Otro**: Cualquier otro tipo

#### Puntuación de Riesgo
- 🔴 **Alto (80-100)**: Requiere atención inmediata
- 🟡 **Medio (50-79)**: Monitorear y evaluar
- 🟢 **Bajo (0-49)**: Riesgo mínimo

## 📈 KPIs Incluidos

### 📊 **Métricas Principales**
- **Total de Registros**: Cantidad total encontrada
- **Fuentes Únicas**: Diversidad de fuentes
- **Documentos Descargables**: Archivos disponibles para descarga
- **Metadatos Completos**: Calidad de la información

### ⚠️ **Indicadores de Riesgo**
- **Posibles Leaks**: Porcentaje en fuentes de filtración
- **Exposición Pública**: Registros marcados como públicos
- **Indexados**: Disponibles en motores de búsqueda
- **Sensibles**: Marcados como información sensible

## 🔧 Configuración Avanzada

### Personalización del Output
```python
from intelx.exports import export_to_interactive_html

# Configuración completa
file_path = export_to_interactive_html(
    records=data,
    filename="reporte_personalizado.html",  # Nombre específico
    exports_dir="/mi/directorio/custom",    # Directorio custom
    search_term="mi búsqueda",              # Término de búsqueda
    app_version="2.0.0-custom"              # Versión personalizada
)
```

### Integración en Scripts
```python
import json
from intelx.interactive_report import generate_interactive_html_report

# Cargar datos desde JSON
with open('mis_datos.json', 'r') as f:
    records = json.load(f)

# Generar múltiples reportes
for term in ["email1@domain.com", "email2@domain.com"]:
    filtered_records = [r for r in records if term in r.get('name', '')]
    
    if filtered_records:
        generate_interactive_html_report(
            records=filtered_records,
            output_filepath=f"reporte_{term.replace('@', '_at_')}.html",
            search_term=term
        )
```

## 🛠️ Desarrollo y Extensión

### Arquitectura Modular
```
interactive_report.py
├── DataProcessor          # Análisis y clasificación
├── VisualizationGenerator # Gráficos y charts
├── TableGenerator         # Tablas interactivas
├── StyleGenerator         # CSS moderno
└── InteractiveReportGenerator # Orquestador
```

### Añadir Nuevos Tipos de Datos
```python
# En DataProcessor._classify_data_type()
def _classify_data_type(record):
    name = str(record.get("name", "")).lower()
    
    # Añadir nueva clasificación
    if "cryptocurrency" in name or "bitcoin" in name:
        return "Criptomoneda"
    
    # ... resto de clasificaciones
```

### Personalizar Estilos
```python
# En StyleGenerator.generate_css()
def generate_css(self):
    return """
    /* Tus estilos personalizados */
    :root {
        --primary-color: #your-color;
        --secondary-color: #your-other-color;
    }
    """ + self.default_styles()
```

## 🧪 Testing y Validación

### Scripts de Prueba Incluidos

1. **demo_interactive_report.py**
   - Genera 150 registros de muestra
   - Demuestra todas las características
   - Abre automáticamente en el navegador

2. **validate_interactive_report.py**
   - Usa datos reales del proyecto
   - Valida integridad del HTML generado
   - Verifica todas las funcionalidades

### Ejecutar Pruebas
```bash
# Demo completo
python demo_interactive_report.py

# Validación con datos reales
python validate_interactive_report.py
```

## 🔍 Troubleshooting

### Problemas Comunes

#### El reporte no se abre automáticamente
```python
# Solución: Abrir manualmente
import webbrowser
webbrowser.open(f'file://{absolute_path_to_report}')
```

#### Los gráficos no se muestran
- **Causa**: Sin conexión a internet para Chart.js CDN
- **Solución**: Asegurar conexión al cargar la página inicial

#### Filtros no funcionan
- **Causa**: JavaScript deshabilitado
- **Solución**: Habilitar JavaScript en el navegador

#### Caracteres especiales en nombres de archivo
```python
# Los nombres se sanitizan automáticamente
# ejemplo@domain.com -> ejemplo_at_domain_dot_com.html
```

### Logs y Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Los logs mostrarán el proceso de generación
```

## 📚 Recursos Adicionales

### Documentación Técnica
- `docs/INTERACTIVE_REPORTS.md`: Documentación técnica completa
- `intelx/interactive_report.py`: Código fuente con comentarios

### Ejemplos de Uso
- `demo_interactive_report.py`: Demostración completa
- `validate_interactive_report.py`: Validación con datos reales

### Dependencias
- **Chart.js**: Gráficos interactivos (CDN)
- **Python 3.8+**: Entorno de ejecución
- **Navegador moderno**: Chrome 90+, Firefox 88+, Safari 14+

## 🤝 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear feature branch
3. Implementar mejoras
4. Añadir tests
5. Submit pull request

### Ideas para Mejoras
- 🌙 **Modo oscuro**: Tema dark/light
- 📊 **Más gráficos**: Mapas de calor, Sankey diagrams
- 🔄 **Auto-refresh**: Actualización automática
- 📱 **PWA**: Progressive Web App features
- 🤖 **AI Insights**: Análisis automático con IA

---

## 🎉 ¡Disfruta de tus nuevos reportes interactivos!

El sistema de reportes HTML interactivos transforma datos complejos en insights visuales y accionables. Con filtros avanzados, gráficos modernos y diseño responsive, ahora tienes una herramienta profesional para análisis de intelligence.

**¿Preguntas?** Revisa la documentación técnica o ejecuta los scripts de demo para ver el sistema en acción.

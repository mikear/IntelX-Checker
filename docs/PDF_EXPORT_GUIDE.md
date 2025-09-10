# Guía de Exportación a PDF - IntelX Checker v2.0

## Descripción
La funcionalidad de exportación a PDF permite generar reportes profesionales con análisis estadístico y visualizaciones gráficas de los resultados obtenidos en las búsquedas de Intelligence X.

## Características del Reporte PDF

### 📊 **Contenido del Reporte**
1. **Información General**
   - Fecha y hora del reporte
   - Término de búsqueda utilizado
   - Total de registros encontrados
   - Información de la aplicación

2. **Resumen Estadístico**
   - Tabla con métricas detalladas
   - Distribución por fuentes (buckets)
   - Distribución por tipos de medio
   - Porcentajes de cada categoría

3. **Análisis Gráfico** (cuando hay ≥3 registros)
   - Gráfico circular de distribución por fuentes
   - Gráfico de barras de tipos de medio
   - Colores diferenciados para mejor visualización

4. **Datos Detallados**
   - Tabla estructurada con los primeros 50 registros
   - Columnas: Fecha, Título, Fuente, Tipo de Medio
   - Formato de fecha legible (DD/MM/YYYY)
   - Títulos truncados para mejor presentación

### 🎨 **Diseño Visual**
- **Formato**: A4 con márgenes profesionales
- **Colores**: Esquema azul/rojo para encabezados
- **Tipografía**: Fuentes Helvetica con tamaños variables
- **Tablas**: Bordes y sombreados para mejor legibilidad
- **Gráficos**: Paletas de colores Set3 y Pastel1

### 📁 **Ubicación de Archivos**
- **Directorio**: `exports/pdf/`
- **Nomenclatura**: `Informe_IntelX_{término}_{fecha}_{hora}.pdf`
- **Ejemplo**: `Informe_IntelX_example_at_domain_dot_com_20250907_095108.pdf`

## Cómo Usar la Exportación a PDF

### 1. **Realizar una Búsqueda**
   - Ingresa el término a buscar en el campo correspondiente
   - Ejecuta la búsqueda y espera los resultados
   - Verifica que aparezcan datos en la tabla de resultados

### 2. **Exportar a PDF**
   - Ve al menú **Archivo** → **Exportar a PDF**
   - Selecciona la ubicación y nombre del archivo
   - El sistema generará automáticamente el reporte

### 3. **Verificar el Reporte**
   - Se mostrará un mensaje de confirmación con la ruta del archivo
   - Abre el PDF con tu visor preferido
   - Revisa las estadísticas y gráficos generados

## Dependencias Técnicas

```
reportlab>=4.0.0    # Generación de PDF
matplotlib>=3.7.0   # Creación de gráficos
pandas>=2.0.0       # Análisis de datos
```

## Limitaciones y Consideraciones

### 📋 **Límites de Datos**
- **Tabla detallada**: Máximo 50 registros mostrados
- **Gráficos**: Se generan solo con 3 o más registros
- **Rendimiento**: Optimizado para conjuntos de datos medianos

### 🔧 **Manejo de Errores**
- Validación de datos antes de la exportación
- Mensajes informativos para el usuario
- Limpieza automática de archivos temporales
- Manejo de excepciones en generación de gráficos

### 🌐 **Soporte Multiidioma**
- Interfaz en español e inglés
- Etiquetas de gráficos en idioma de la interfaz
- Formateo de fechas localizado

## Solución de Problemas

### ❌ **Error: "No hay resultados para exportar"**
- **Causa**: No se han realizado búsquedas o no hay datos
- **Solución**: Ejecuta una búsqueda antes de exportar

### ❌ **Error: "Dependencias faltantes para PDF"**
- **Causa**: Librerías PDF no instaladas
- **Solución**: Ejecuta `pip install -r requirements.txt`

### ❌ **Error: "No se pudo generar el PDF"**
- **Causa**: Problemas de permisos o espacio en disco
- **Solución**: Verifica permisos de escritura en el directorio de destino

## Notas de Desarrollo

### 🔄 **Proceso de Generación**
1. Validación de datos de entrada
2. Cálculo de estadísticas con pandas
3. Generación de gráficos con matplotlib
4. Composición del PDF con reportlab
5. Limpieza de archivos temporales

### 🎯 **Optimizaciones Implementadas**
- Truncado inteligente de títulos largos
- Paletas de colores optimizadas
- Gestión eficiente de memoria
- Manejo robusto de excepciones

---

**IntelX Checker v2.0** - Desarrollado con ❤️ para análisis profesional de datos de Intelligence X

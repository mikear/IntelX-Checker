# Manual de Usuario - IntelX Checker

## 1. Introducción

Bienvenido al Manual de Usuario de **IntelX Checker**, una aplicación de escritorio diseñada para facilitar la búsqueda y el análisis de filtraciones de datos a través de la API de Intelligence X. Con esta herramienta, puedes verificar rápidamente si un correo electrónico o un dominio ha sido expuesto en diversas fuentes de inteligencia, como pastes, foros de la darknet, y otras filtraciones públicas y privadas.

## 2. Instalación

Para instalar y ejecutar IntelX Checker, sigue las instrucciones detalladas en el archivo `README.md` ubicado en la raíz del proyecto. Asegúrate de tener Python y todas las dependencias necesarias instaladas.

## 3. Interfaz de Usuario (GUI)

La interfaz de IntelX Checker está diseñada para ser intuitiva y fácil de usar. A continuación, se describen sus componentes principales:

### 3.1. Sección Superior: Búsqueda y Controles

*   **Campo de Correo o Dominio:** Aquí introduces el término de búsqueda (un correo electrónico, un dominio, etc.).
*   **Botón "Buscar":** Inicia la búsqueda en Intelligence X con el término y las fuentes seleccionadas.
*   **Botón "Cancelar":** Detiene cualquier búsqueda en curso.

### 3.2. Sección Central: Estado y Resultados

*   **Barra de Estado:** Muestra mensajes informativos sobre el estado actual de la aplicación (ej. "Buscando...", "¡Éxito!", "Error:").
*   **Barra de Progreso:** Indica el progreso de la búsqueda.
*   **Campo "Filtrar resultados...":** Te permite filtrar los resultados mostrados en la tabla en tiempo real, buscando coincidencias en el título de los registros.
*   **Créditos:** Muestra tus créditos restantes en la API de Intelligence X.
*   **Tabla de Resultados:** Aquí se muestran los registros encontrados por la búsqueda, organizados en columnas. Puedes ordenar los resultados haciendo clic en el encabezado de cada columna.

### 3.3. Pie de Página

Contiene información sobre la versión de la aplicación, el desarrollador y la fuente de los resultados (Intelligence X), con enlaces útiles.

## 4. Menú Principal

La barra de menú superior ofrece acceso a diversas funciones:

### 4.1. Menú "Archivo"

*   **Exportar a CSV...:** Exporta los resultados de la búsqueda a un archivo CSV. Si hay filas seleccionadas en la tabla, te preguntará si deseas exportar solo la selección o todos los resultados. Al finalizar, te dará la opción de abrir la carpeta donde se guardó el archivo.
*   **Exportar a JSON...:** Exporta los resultados de la búsqueda a un archivo JSON. Funciona de manera similar a la exportación a CSV, incluyendo la opción de exportar solo la selección y abrir la carpeta.
*   **Salir:** Cierra la aplicación.

### 4.2. Menú "Configuración"

*   **Gestionar Clave API...:** Abre un diálogo donde puedes introducir, actualizar o eliminar tu clave de API de Intelligence X. Es fundamental para poder realizar búsquedas.
*   **Fuentes de Búsqueda (Buckets)...:** Abre un diálogo donde puedes seleccionar las fuentes (buckets) específicas en las que deseas que se realice la búsqueda. Consulta el `GLOSARIO.md` para una explicación detallada de cada fuente.

### 4.3. Menú "Ayuda"

*   **Refrescar Créditos:** Consulta y actualiza la información de tus créditos restantes en la API de Intelligence X.
*   **Obtener Clave API de IntelX:** Abre tu navegador web en la página donde puedes obtener una clave de API de Intelligence X.
*   **Visitar Intelligence X:** Abre el sitio web principal de Intelligence X en tu navegador.
*   **Acerca de...:** Muestra información sobre la aplicación y el desarrollador.

## 5. Cómo Realizar una Búsqueda

1.  **Asegúrate de tener una Clave API configurada.** Si no la tienes, ve a `Configuración` > `Gestionar Clave API...` e introdúcela.
2.  **Introduce tu término de búsqueda** en el campo "Correo o Dominio:". Puede ser un correo electrónico (ej. `ejemplo@dominio.com`) o un dominio (ej. `dominio.com`).
3.  **(Opcional) Selecciona las fuentes de búsqueda.** Si no deseas buscar en todas las fuentes por defecto, ve a `Configuración` > `Fuentes de Búsqueda (Buckets)...` y selecciona las que te interesen.
4.  **Haz clic en el botón "Buscar".** La aplicación iniciará la consulta y mostrará el progreso.
5.  **Analiza los resultados.** Una vez finalizada la búsqueda, los registros aparecerán en la tabla. Si no se encuentran resultados, la tabla estará vacía.

## 6. Filtrado y Ordenación de Resultados

*   **Filtrar:** Utiliza el campo "Filtrar resultados..." para buscar texto específico dentro de los títulos de los registros mostrados en la tabla. El filtrado se realiza en tiempo real a medida que escribes.
*   **Ordenar:** Haz clic en el encabezado de cualquier columna de la tabla para ordenar los resultados por esa columna (ascendente o descendente).

## 7. Exportación de Resultados

Para guardar los resultados de tu búsqueda:

1.  Ve al menú `Archivo`.
2.  Selecciona `Exportar a CSV...` o `Exportar a JSON...`.
3.  Si tienes filas seleccionadas en la tabla, la aplicación te preguntará si deseas exportar solo la selección o todos los resultados. Elige la opción deseada.
4.  Se abrirá un diálogo para que elijas la ubicación y el nombre del archivo.
5.  Una vez exportado, aparecerá un mensaje de confirmación con un botón "Abrir Carpeta" para acceder directamente al archivo guardado.

## 8. Gestión de Clave API

Tu clave de API es esencial para que la aplicación funcione. Para gestionarla:

1.  Ve a `Configuración` > `Gestionar Clave API...`.
2.  Introduce tu clave en el campo. Si lo dejas vacío y guardas, la clave se eliminará.
3.  Haz clic en "Guardar" para aplicar los cambios.

## 9. Solución de Problemas Comunes

*   **"Falta Clave API"**: Asegúrate de haber introducido tu clave de API en `Configuración` > `Gestionar Clave API...`.
*   **"Sin Selección" (al buscar)**: Debes seleccionar al menos una fuente de búsqueda en `Configuración` > `Fuentes de Búsqueda (Buckets)...`.
*   **Menos resultados de los esperados**: Como se explica en el `GLOSARIO.md`, la base de datos de Intelligence X es dinámica. La cantidad de resultados puede variar con el tiempo.
*   **"Desconocido" en Tipo de Medio**: Este problema ha sido corregido en la versión actual. Asegúrate de tener la última versión de la aplicación.
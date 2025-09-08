# IntelX Checker

![Banner de portada](docs/assets/banner.jpg)

> **IntelX Checker** — Aplicación avanzada para investigar filtraciones de datos y fuentes OSINT. Busca, visualiza y exporta resultados de Intelligence X en una interfaz moderna y profesional.

![Pantalla principal](docs/assets/main.jpg)

IntelX Checker es una aplicación de escritorio para Windows que te permite buscar filtraciones de datos en el motor de búsqueda de Intelligence X. Simplemente introduce un correo electrónico o un dominio para descubrir si ha sido expuesto en pastes, foros de la darknet, filtraciones de datos y más.

---

## ✨ Características

- **Búsqueda Potente:** Realiza búsquedas en la API de Intelligence X por correo electrónico o dominio.
- **Filtro de Fuentes:** Selecciona las fuentes de datos (buckets) específicas en las que deseas buscar.
- **Visualización Clara:** Muestra los resultados en una tabla organizada que puedes ordenar por fecha, nombre, fuente o tipo.
  
  ![Exportación de tabla CSV](docs/assets/csv_table_export.jpg)

- **Exportación a CSV y JSON:** Exporta los resultados de tu búsqueda a archivos CSV o JSON para un análisis posterior.
- **Gestión de API Key:** Guarda tu clave de API de Intelligence X de forma segura.
- **Visualización interna de manual y glosario:** Consulta el manual y glosario en ventanas internas con scroll y formato.
- **Icono en todos los diálogos:** Todos los cuadros de diálogo muestran el icono de la app.
- **Interfaz Moderna:** Una interfaz limpia y fácil de usar con soporte para temas claro y oscuro.

---

## 🚀 Requisitos

- **Python 3.10 o superior**
- Las dependencias de Python listadas en `requirements.txt`:
    - `customtkinter`
    - `tkhtmlview`
    - `markdown2`
    - `Pillow`
    - `requests`
    - `python-dotenv`

---

## ⚙️ Instalación

1. **Clona el repositorio:**
    ```bash
    git clone https://github.com/mikear/pawned.git
    cd pawned
    ```

2. **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Uso

1. **Ejecuta la aplicación:**
    ```bash
    python main.py
    ```
2. **Configura tu API Key:**
    - Ve a `Configuración` > `Gestionar Clave API...`
    - Introduce tu clave de API de Intelligence X. Puedes obtener una en [intelx.io](https://intelx.io/account?tab=developer).
3. **Realiza una búsqueda:**
    - Introduce el correo o dominio en el campo de búsqueda.
    - Haz clic en `Buscar`.
    - Los resultados aparecerán en la tabla.
4. **Exporta resultados:**
    - Usa el menú `Archivo` para exportar a CSV o JSON.
5. **Consulta el manual y glosario:**
    - Accede desde el menú `Ayuda` y visualízalos en ventanas internas con scroll.

---

## 📁 Estructura de carpetas
- `intelx/` : Lógica de API y GUI
- `docs/` : Manual, glosario, icono
- `exports/csv` : Resultados exportados
- `requirements.txt` : Dependencias
- `docs/assets/` : Prints de pantalla y recursos gráficos

---

## 👤 Créditos
Desarrollado por Diego A. Rábalo

---
Para soporte o sugerencias, abre un issue en GitHub.

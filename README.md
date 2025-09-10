<<<<<<< HEAD
# IntelX Checker V2 🕵️‍♂️

![Banner de portada](docs/assets/banner.jpg)

Aplicación avanzada para investigar filtraciones de datos y fuentes OSINT. Busca, visualiza y exporta resultados de Intelligence X en una interfaz moderna y profesional.
=======
# IntelX Checker V2 🕵️‍♂️

![Banner de portada](docs/assets/banner.jpg)

> **IntelX Checker** — Aplicación avanzada para investigar filtraciones de datos y fuentes OSINT. Busca, visualiza y exporta resultados de Intelligence X en una interfaz moderna y profesional.

## Apoya el Proyecto
Esta herramienta es un proyecto de código abierto. Si te resulta útil, considera apoyar su desarrollo con una donación.

[![Donar con PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate/?hosted_button_id=6W8LAAFX9BN6E)

## Tabla de Contenidos
- [Características Destacadas](#características-destacadas)
- [Ideal para](#ideal-para)
- [Screenshots](#screenshots)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Licencia](#licencia)
- [Créditos](#créditos)
- [Contacto y Soporte](#contacto-y-soporte)
- [Palabras Clave (SEO)](#palabras-clave-seo)

## Características Destacadas
- 🔍 **Búsqueda Potente:** Realiza búsquedas en la API de Intelligence X por correo electrónico o dominio.
- 🎯 **Filtro de Fuentes:** Selecciona las fuentes de datos (buckets) específicas en las que deseas buscar.
- 📊 **Visualización Clara:** Muestra los resultados en una tabla organizada que puedes ordenar por fecha, nombre, fuente o tipo.
- 💾 **Exportación Versátil:** Exporta los resultados de tu búsqueda a archivos CSV o JSON para un análisis posterior.
- 🔑 **Gestión Segura de API Key:** Guarda tu clave de API de Intelligence X de forma segura.
- 📚 **Documentación Integrada:** Visualización interna de manual y glosario para consulta rápida.
- ✨ **Interfaz Moderna:** Una interfaz limpia y fácil de usar con soporte para temas claro y oscuro.
- 🖼️ **Iconografía Consistente:** Todos los cuadros de diálogo muestran el icono de la aplicación.

### 🎯 Ideal para:
-   **Analistas de Seguridad:** Investigar filtraciones de datos y correlacionar información de OSINT.
-   **Investigadores Forenses:** Extraer y analizar datos de fuentes públicas y privadas.
-   **Profesionales de Ciberseguridad:** Monitorear la exposición de credenciales y dominios.

## Screenshots

**Pantalla Principal**
![Pantalla principal](docs/assets/main.jpg)

**Exportación de Tabla CSV**
![Exportación de tabla CSV](docs/assets/csv_table_export.jpg)

## 🚀 Requisitos

- **Python 3.10 o superior**
- Las dependencias de Python listadas en `requirements.txt`:
    - `customtkinter`
    - `tkhtmlview`
    - `markdown2`
    - `Pillow`
    - `requests`
    - `python-dotenv`

## ⚙️ Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/mikear/IntelX-Checker.git
    cd IntelX-Checker
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuración
Para funcionar, la aplicación necesita tu clave de API de Intelligence X.

1.  **Obtén tu clave:**
    -   **Intelligence X:** Consigue tu clave en [intelx.io](https://intelx.io/account?tab=developer).

2.  **Configura la clave:**
    -   **Método GUI (Recomendado):**
        -   Inicia la aplicación gráfica.
        -   Ve al menú `Configuración` > `Gestionar Clave API...`
        -   Pega tu clave en el campo correspondiente y guarda. Se creará un archivo `.env` automáticamente.
    -   **Método Manual:**
        -   Crea un archivo llamado `.env` en la raíz del proyecto.
        -   Añade la siguiente línea, reemplazando `TU_CLAVE_AQUI` con tu clave real:
          ```
          INTELX_API_KEY=TU_CLAVE_AQUI
          ```

## ▶️ Uso

1. **Ejecuta la aplicación:**
    ```bash
    python main.py
    ```
2. **Configura tu API Key:**
    - Ve a `Configuración` > `Gestionar Clave API...`
    - Introduce tu clave de API de Intelligence X.
3. **Realiza una búsqueda:**
    - Introduce el correo o dominio en el campo de búsqueda.
    - Haz clic en `Buscar`.
    - Los resultados aparecerán en la tabla.
4. **Exporta resultados:**
    - Usa el menú `Archivo` para exportar a CSV o JSON.
5. **Consulta el manual y glosario:**
    - Accede desde el menú `Ayuda` y visualízalos en ventanas internas con scroll.

## 📁 Estructura de Carpetas
- `intelx/` : Lógica de API y GUI
- `docs/` : Manual, glosario, icono
- `exports/csv` : Resultados exportados
- `requirements.txt` : Dependencias
- `docs/assets/` : Prints de pantalla y recursos gráficos

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 💖 Créditos
Desarrollado por Diego A. Rábalo.
Este proyecto utiliza las siguientes librerías de código abierto:
- **customtkinter:** Para la interfaz gráfica de usuario.
- **tkhtmlview:** Para la visualización de HTML.
- **markdown2:** Para la conversión de Markdown a HTML.
- **Pillow:** Para el procesamiento de imágenes.
- **requests:** Para realizar peticiones HTTP.
- **python-dotenv:** Para la gestión de variables de entorno y claves API.

## 📞 Contacto y Soporte
- 📧 **Correo Electrónico:** [diego_rabalo@hotmail.com](mailto:diego_rabalo@hotmail.com)
- 🔗 **LinkedIn:** [Diego A. Rábalo](https://www.linkedin.com/in/rabalo)

## 🔑 Palabras Clave (SEO)
IntelX Checker, Intelligence X, OSINT, Filtraciones de Datos, Ciberseguridad, Python, GUI, Windows, Análisis de Datos, Exportación CSV, Exportación JSON.
>>>>>>> f1f8b60835c758c195a3913af82733959da3a02f

## Apoya el Proyecto
Esta herramienta es un proyecto de código abierto. Si te resulta útil, considera apoyar su desarrollo con una donación.

<<<<<<< HEAD
[Donar con PayPal](https://www.paypal.com/donate/?hosted_button_id=6W8LAAFX9BN6E)

## Tabla de Contenidos
- [Características Destacadas](#características-destacadas)
- [Ideal para](#🎯-ideal-para)
- [Screenshots](#screenshots)
- [Requisitos](#🚀-requisitos)
- [Instalación](#️-instalación)
- [Configuración](#configuración)
- [Uso](#️-uso)
- [Estructura de Carpetas](#📁-estructura-de-carpetas)
- [Licencia](#📄-licencia)
- [Créditos](#💖-créditos)
- [Contacto y Soporte](#📞-contacto-y-soporte)
- [Palabras Clave (SEO)](#🔑-palabras-clave-seo)

## Características Destacadas
- 🔍 Búsqueda potente en la API de Intelligence X por correo electrónico o dominio.
- 🎯 Filtro de fuentes: selecciona los buckets específicos donde buscar.
- 📊 Visualización clara: resultados en tabla ordenable por fecha, nombre, fuente o tipo.
- 💾 Exportación versátil: exporta resultados a CSV, JSON y HTML (con resumen, evolución anual y distribución de medios).
- 🔑 Gestión segura de API Key: guarda tu clave de API de forma segura.
- 📚 Documentación integrada: manual y glosario accesibles desde la app.
- ✨ Interfaz moderna: temas claro/oscuro, icono integrado y soporte PyInstaller.
- ⚡ Actualización automática de créditos y carga incremental de resultados para evitar bloqueos.

### 🎯 Ideal para:
- Analistas de Seguridad: investigar filtraciones y correlacionar OSINT.
- Investigadores Forenses: extraer y analizar datos públicos y privados.
- Profesionales de Ciberseguridad: monitorear exposición de credenciales y dominios.

## Screenshots
- [Pantalla principal](docs/assets/main.jpg)
- [Exportación de tabla CSV](docs/assets/csv_table_export.jpg)
- [Reporte HTML generado](docs/assets/reporte.jpg)

## 🚀 Requisitos
- Python 3.10 o superior
- Dependencias en `requirements.txt`:
  - customtkinter
  - tkhtmlview
  - markdown2
  - Pillow
  - requests
  - python-dotenv

## ⚙️ Instalación
1. Clona el repositorio:
   ```powershell
   git clone https://github.com/tuusuario/IntelX-Checker-V2.git
   cd IntelX-Checker-V2
   ```
2. (Opcional) Crea un entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instala dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y agrega tu clave API:
   ```powershell
   copy .env.example .env
   # Edita .env y coloca tu INTELX_API_KEY
   ```

## Configuración
Para funcionar, la aplicación necesita tu clave de API de Intelligence X.
- Consíguela en [intelx.io](https://intelx.io/account?tab=developer).
- Método GUI (recomendado):
  - Inicia la app
  - Menú `Configuración` > `Gestionar Clave API...`
  - Pega tu clave y guarda
- Método manual:
  - Crea `.env` en la raíz
  - Añade:
    ```
    INTELX_API_KEY=TU_CLAVE_AQUI
    LANGUAGE=es
    ```

## ▶️ Uso
1. Ejecuta la app:
   ```powershell
   python main.py
   ```
2. Configura tu API Key (menú `Configuración`)
3. Realiza búsquedas y exporta resultados
4. Consulta el manual y glosario desde el menú `Ayuda`
=======
[![Donar con PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate/?hosted_button_id=6W8LAAFX9BN6E)

## Tabla de Contenidos
- [Características Destacadas](#características-destacadas)
- [Ideal para](#ideal-para)
- [Screenshots](#screenshots)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Licencia](#licencia)
- [Créditos](#créditos)
- [Contacto y Soporte](#contacto-y-soporte)
- [Palabras Clave (SEO)](#palabras-clave-seo)

## Características Destacadas
- 🔍 **Búsqueda Potente:** Realiza búsquedas en la API de Intelligence X por correo electrónico o dominio.
- 🎯 **Filtro de Fuentes:** Selecciona las fuentes de datos (buckets) específicas en las que deseas buscar.
- 📊 **Visualización Clara:** Muestra los resultados en una tabla organizada que puedes ordenar por fecha, nombre, fuente o tipo.
- 💾 **Exportación Versátil:** Exporta los resultados de tu búsqueda a archivos CSV o JSON para un análisis posterior.
- 🔑 **Gestión Segura de API Key:** Guarda tu clave de API de Intelligence X de forma segura.
- 📚 **Documentación Integrada:** Visualización interna de manual y glosario para consulta rápida.
- ✨ **Interfaz Moderna:** Una interfaz limpia y fácil de usar con soporte para temas claro y oscuro.
- 🖼️ **Iconografía Consistente:** Todos los cuadros de diálogo muestran el icono de la aplicación.

### 🎯 Ideal para:
-   **Analistas de Seguridad:** Investigar filtraciones de datos y correlacionar información de OSINT.
-   **Investigadores Forenses:** Extraer y analizar datos de fuentes públicas y privadas.
-   **Profesionales de Ciberseguridad:** Monitorear la exposición de credenciales y dominios.

## Screenshots

**Pantalla Principal**
![Pantalla principal](docs/assets/main.jpg)

**Exportación de Tabla CSV**
![Exportación de tabla CSV](docs/assets/csv_table_export.jpg)

## 🚀 Requisitos

- **Python 3.10 o superior**
- Las dependencias de Python listadas en `requirements.txt`:
    - `customtkinter`
    - `tkhtmlview`
    - `markdown2`
    - `Pillow`
    - `requests`
    - `python-dotenv`

## ⚙️ Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/mikear/IntelX-Checker.git
    cd IntelX-Checker
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuración
Para funcionar, la aplicación necesita tu clave de API de Intelligence X.

1.  **Obtén tu clave:**
    -   **Intelligence X:** Consigue tu clave en [intelx.io](https://intelx.io/account?tab=developer).

2.  **Configura la clave:**
    -   **Método GUI (Recomendado):**
        -   Inicia la aplicación gráfica.
        -   Ve al menú `Configuración` > `Gestionar Clave API...`
        -   Pega tu clave en el campo correspondiente y guarda. Se creará un archivo `.env` automáticamente.
    -   **Método Manual:**
        -   Crea un archivo llamado `.env` en la raíz del proyecto.
        -   Añade la siguiente línea, reemplazando `TU_CLAVE_AQUI` con tu clave real:
          ```
          INTELX_API_KEY=TU_CLAVE_AQUI
          ```

## ▶️ Uso

1. **Ejecuta la aplicación:**
    ```bash
    python main.py
    ```
2. **Configura tu API Key:**
    - Ve a `Configuración` > `Gestionar Clave API...`
    - Introduce tu clave de API de Intelligence X.
3. **Realiza una búsqueda:**
    - Introduce el correo o dominio en el campo de búsqueda.
    - Haz clic en `Buscar`.
    - Los resultados aparecerán en la tabla.
4. **Exporta resultados:**
    - Usa el menú `Archivo` para exportar a CSV o JSON.
5. **Consulta el manual y glosario:**
    - Accede desde el menú `Ayuda` y visualízalos en ventanas internas con scroll.
>>>>>>> f1f8b60835c758c195a3913af82733959da3a02f

## 📁 Estructura de Carpetas
- `intelx/` : Lógica de API y GUI
- `docs/` : Manual, glosario, icono
- `exports/csv` : Resultados exportados
- `requirements.txt` : Dependencias
<<<<<<< HEAD
- `docs/assets/` : Imágenes y recursos gráficos
=======
- `docs/assets/` : Prints de pantalla y recursos gráficos
>>>>>>> f1f8b60835c758c195a3913af82733959da3a02f

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 💖 Créditos
<<<<<<< HEAD
Desarrollado por Diego A. Rábalo. Este proyecto utiliza las siguientes librerías:
- customtkinter
- tkhtmlview
- markdown2
- Pillow
- requests
- python-dotenv

## 📞 Contacto y Soporte
- 📧 [diego_rabalo@hotmail.com](mailto:diego_rabalo@hotmail.com)
- 🔗 [LinkedIn: Diego A. Rábalo](https://www.linkedin.com/in/rabalo)
=======
Desarrollado por Diego A. Rábalo.
Este proyecto utiliza las siguientes librerías de código abierto:
- **customtkinter:** Para la interfaz gráfica de usuario.
- **tkhtmlview:** Para la visualización de HTML.
- **markdown2:** Para la conversión de Markdown a HTML.
- **Pillow:** Para el procesamiento de imágenes.
- **requests:** Para realizar peticiones HTTP.
- **python-dotenv:** Para la gestión de variables de entorno y claves API.

## 📞 Contacto y Soporte
- 📧 **Correo Electrónico:** [diego_rabalo@hotmail.com](mailto:diego_rabalo@hotmail.com)
- 🔗 **LinkedIn:** [Diego A. Rábalo](https://www.linkedin.com/in/rabalo)
>>>>>>> f1f8b60835c758c195a3913af82733959da3a02f

## 🔑 Palabras Clave (SEO)
IntelX Checker, Intelligence X, OSINT, Filtraciones de Datos, Ciberseguridad, Python, GUI, Windows, Análisis de Datos, Exportación CSV, Exportación JSON.
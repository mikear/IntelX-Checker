# IntelX Checker V2 🕵️‍♂️

![Banner de portada](docs/assets/banner.jpg)

Aplicación avanzada para investigar filtraciones de datos y fuentes OSINT. Busca, visualiza y exporta resultados de Intelligence X en una interfaz moderna y profesional.

## Apoya el Proyecto
Esta herramienta es un proyecto de código abierto. Si te resulta útil, considera apoyar su desarrollo con una donación.

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

## 📁 Estructura de Carpetas
- `intelx/` : Lógica de API y GUI
- `docs/` : Manual, glosario, icono
- `exports/csv` : Resultados exportados
- `requirements.txt` : Dependencias
- `docs/assets/` : Imágenes y recursos gráficos

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 💖 Créditos
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

## 🔑 Palabras Clave (SEO)
IntelX Checker, Intelligence X, OSINT, Filtraciones de Datos, Ciberseguridad, Python, GUI, Windows, Análisis de Datos, Exportación CSV, Exportación JSON.
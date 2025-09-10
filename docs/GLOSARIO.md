# Glosario de Resultados de Búsqueda

Este glosario explica cada uno de los campos que se muestran en la tabla de resultados de búsqueda de la aplicación IntelX Checker. Comprender estos términos te ayudará a interpretar la información obtenida de Intelligence X de manera más efectiva.

---

## Campos de la Tabla de Resultados

### Fecha Aproximada
*   **Descripción:** Indica la fecha aproximada en que el documento o registro fue publicado o indexado por Intelligence X. Es importante tener en cuenta que esta fecha puede no ser la fecha exacta de creación del contenido original, sino la fecha en que fue detectado y añadido a la base de datos de Intelligence X.
*   **Formato:** Generalmente se muestra en un formato de fecha legible (por ejemplo, AAAA-MM-DD).

### Titulo
*   **Descripción:** Es el título o una breve descripción del contenido del registro. Este campo proporciona una idea rápida sobre de qué trata el documento, la filtración, el paste, etc. Puede ser el título original del documento o un título generado por Intelligence X para resumir el contenido.
*   **Ejemplos:** "Lista de correos electrónicos filtrados", "Credenciales de acceso a foro", "Documento de texto de Pastebin".

### Fuente (Bucket)
*   **Descripción:** Se refiere a la categoría o el tipo de repositorio de donde proviene el registro. Intelligence X organiza la información en diferentes "buckets" (cubos) según su origen y naturaleza. Comprender la fuente es crucial para evaluar la relevancia y el contexto de los datos.
*   **Valores Posibles y su Significado:**
    *   **Pastes:** Repositorios de texto pegado, como Pastebin, Pastie, Hastebin y sitios similares. A menudo contienen volcados de código, credenciales, notas o mensajes.
    *   **Leaks (Públicas):** Filtraciones públicas generales de datos. Esto puede incluir bases de datos comprometidas, volcados de información de sitios web o servicios, y otros conjuntos de datos expuestos públicamente.
    *   **Darknet (.onion):** Contenido encontrado en sitios de la darknet accesibles a través de la red Tor, identificados por la extensión `.onion`.
    *   **Darknet (I2P):** Contenido de sitios de la darknet accesibles a través de la red I2P.
    *   **Dumpsters:** Repositorios de datos desechados o expuestos accidentalmente. Esto puede incluir información que se dejó en servidores mal configurados, almacenamiento en la nube sin protección, o datos residuales.
    *   **Whois:** Información de registros de dominios (Whois). Contiene datos sobre la propiedad y el registro de nombres de dominio.
    *   **Usenet:** Contenido de foros y grupos de noticias Usenet. Usenet es un sistema de discusión global que ha existido desde los primeros días de internet.
    *   **Bot Logs:** Registros generados por bots o malware que capturan credenciales, pulsaciones de teclas, o información de sistemas comprometidos. Estos logs suelen ser muy sensibles y contienen datos de acceso.

### System ID
*   **Descripción:** Es un identificador único asignado por Intelligence X a cada registro. Este ID es fundamental para referenciar un elemento específico dentro de la base de datos de Intelligence X. Aunque no es directamente legible o significativo para el usuario final, es utilizado internamente por la aplicación para realizar acciones como solicitar una vista previa del contenido original o para la exportación de datos.
*   **Importancia:** Permite la identificación precisa y la recuperación de datos detallados asociados a un resultado de búsqueda.

### Tipo de Medio
*   **Descripción:** Clasifica el formato o la naturaleza del contenido del registro. Ayuda a entender si el resultado es un documento de texto, una imagen, un archivo comprimido, etc.
*   **Valores Posibles y su Significado:**
    *   **Invalid/Not Set:** El tipo de medio no está definido o es inválido.
    *   **Paste Document:** Un documento de texto plano, típicamente de un servicio de "paste".
    *   **Paste User:** Información relacionada con un usuario de un servicio de "paste".
    *   **Forum:** Contenido general de un foro.
    *   **Forum Board:** Una sección o subforo específico dentro de un foro.
    *   **Forum Thread:** Un hilo de discusión completo en un foro.
    *   **Forum Post:** Un mensaje individual dentro de un hilo de foro.
    *   **Forum User:** Información relacionada con un usuario de un foro.
    *   **Screenshot of a Website:** Una captura de pantalla de una página web.
    *   **HTML copy of a Website:** Una copia del código HTML de una página web.
    *   **Tweet:** Un mensaje de la plataforma Twitter.
    *   **URL (High-Level Item):** Una URL que representa un elemento de alto nivel, como una página principal o un directorio.
    *   **PDF document:** Un documento en formato PDF.
    *   **Word document:** Un documento creado con Microsoft Word o similar.
    *   **Excel document:** Una hoja de cálculo creada con Microsoft Excel o similar.
    *   **Powerpoint document:** Una presentación creada con Microsoft PowerPoint o similar.
    *   **Picture:** Un archivo de imagen (JPEG, PNG, GIF, etc.).
    *   **Audio file:** Un archivo de audio.
    *   **Video file:** Un archivo de video.
    *   **Container file (ZIP, RAR, etc):** Un archivo comprimido o contenedor (por ejemplo, ZIP, RAR, 7z).
    *   **HTML file:** Un archivo HTML.
    *   **Text file:** Un archivo de texto genérico.
    *   **Código Fuente:** Archivos que contienen código fuente de programación.

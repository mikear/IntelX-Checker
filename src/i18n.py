"""Internationalization (i18n) Module
Provides translation dictionaries and a translation helper t(key, lang).
"""

LANGUAGES = {
    "es": {
        "title": "IntelX Checker V2",
        "Correo o Dominio": "Correo o Dominio:",
        "Buscar": "Buscar",
        "Cancelar": "Cancelar",
        "Filtrar resultados": "Filtrar resultados...",
        "Créditos": "Créditos:",
        "Listo": "Listo.",
        "Listo.": "Listo.",
        "Iniciando búsqueda...": "Iniciando búsqueda...",
        "Búsqueda cancelada": "Búsqueda cancelada",
        "Gestionar Clave API...": "Gestionar Clave API...",
        "Configuración": "Configuración",
        "Español": "Español",
        "English": "English",
        "Tema Claro": "Tema Claro",
        "Tema Oscuro": "Tema Oscuro",
        "Ayuda": "Ayuda",
        "Manual de Uso": "Manual de Uso",
        "Glosario OSINT": "Glosario OSINT",
        "Acerca de...": "Acerca de...",
        "Exportar": "Exportar",
        "Exportar CSV": "Exportar CSV",
        "Exportar JSON": "Exportar JSON",
        "Exportar HTML Interactivo": "Exportar HTML Interactivo",
        "Exportar PDF": "Exportar PDF",
        "total_results": "Total de Registros",
        "unique_sources": "Fuentes Únicas",
        "downloadable_docs": "Documentos Descargables",
        "complete_metadata": "Metadatos Completos",
        "possible_leaks": "Posibles Leaks",
        "public_exposure": "Exposición Pública",
        "indexed": "Indexados",
        "sensitive": "Sensibles"
    },
    "en": {
        "title": "IntelX Checker V2",
        "Correo o Dominio": "Email or Domain:",
        "Buscar": "Search",
        "Cancelar": "Cancel",
        "Filtrar resultados": "Filter results...",
        "Créditos": "Credits:",
        "Listo": "Ready.",
        "Listo.": "Ready.",
        "Iniciando búsqueda...": "Starting search...",
        "Búsqueda cancelada": "Search cancelled",
        "Gestionar Clave API...": "Manage API Key...",
        "Configuración": "Settings",
        "Español": "Spanish",
        "English": "English",
        "Tema Claro": "Light Theme",
        "Tema Oscuro": "Dark Theme",
        "Ayuda": "Help",
        "Manual de Uso": "User Manual",
        "Glosario OSINT": "OSINT Glossary",
        "Acerca de...": "About...",
        "Exportar": "Export",
        "Exportar CSV": "Export CSV",
        "Exportar JSON": "Export JSON",
        "Exportar HTML Interactivo": "Export Interactive HTML",
        "Exportar PDF": "Export PDF",
        "total_results": "Total Records",
        "unique_sources": "Unique Sources",
        "downloadable_docs": "Downloadable Documents",
        "complete_metadata": "Complete Metadata",
        "possible_leaks": "Possible Leaks",
        "public_exposure": "Public Exposure",
        "indexed": "Indexed",
        "sensitive": "Sensitive"
    }
}


def t(key: str, lang: str = "es") -> str:
    """Return translation for key and language."""
    lang_dict = LANGUAGES.get(lang, LANGUAGES["es"])
    return lang_dict.get(key, LANGUAGES["es"].get(key, key))

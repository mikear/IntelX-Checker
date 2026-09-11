"""
Módulo: config.py
Configuración de entorno y logging
"""
import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv, find_dotenv, set_key

SERVICE_NAME = "IntelX_Checker"
API_KEY_NAME = "INTELX_API_KEY"

# --- Translations i18n ---
TRANSLATIONS = {
    "es": {
        "title": "IntelX Checker V2",
        "search_label": "Correo o Dominio:",
        "search_btn": "Buscar",
        "cancel_btn": "Cancelar",
        "filter_placeholder": "Filtrar resultados...",
        "credits": "Créditos:",
        "ready": "Listo",
        "export_csv": "Exportar CSV",
        "export_json": "Exportar JSON",
        "export_html": "Exportar HTML Interactivo",
        "export_pdf": "Exportar PDF",
        "report_title": "Reporte de Inteligencia IntelX",
        "search_term": "Término de búsqueda",
        "total_results": "Total de Registros",
        "unique_sources": "Fuentes Únicas",
        "downloadable_docs": "Documentos Descargables",
        "complete_metadata": "Metadatos Completos",
        "possible_leaks": "Posibles Leaks",
        "public_exposure": "Exposición Pública",
        "indexed": "Indexados",
        "sensitive": "Sensibles",
        "visual_analysis": "Análisis Visual",
        "detailed_data": "Datos Detallados"
    },
    "en": {
        "title": "IntelX Checker V2",
        "search_label": "Email or Domain:",
        "search_btn": "Search",
        "cancel_btn": "Cancel",
        "filter_placeholder": "Filter results...",
        "credits": "Credits:",
        "ready": "Ready",
        "export_csv": "Export CSV",
        "export_json": "Export JSON",
        "export_html": "Export Interactive HTML",
        "export_pdf": "Export PDF",
        "report_title": "IntelX Intelligence Report",
        "search_term": "Search term",
        "total_results": "Total Records",
        "unique_sources": "Unique Sources",
        "downloadable_docs": "Downloadable Documents",
        "complete_metadata": "Complete Metadata",
        "possible_leaks": "Possible Leaks",
        "public_exposure": "Public Exposure",
        "indexed": "Indexed",
        "sensitive": "Sensitive",
        "visual_analysis": "Visual Analysis",
        "detailed_data": "Detailed Data"
    }
}


def get_text(key: str, lang: str = "es") -> str:
    """Return localized string for key and language."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    return lang_dict.get(key, TRANSLATIONS["es"].get(key, key))


# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(threadName)-15s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Cargar variables de entorno ---
def load_env():
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
            dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False, usecwd=True)
            logger.info(f"App empaquetada. Buscando .env cerca de {application_path}. Encontrado: {dotenv_path}")
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False)
            logger.info(f"App como script. Buscando .env. Encontrado: {dotenv_path}")
        if dotenv_path:
            load_dotenv(dotenv_path)
            logger.info(f"Archivo .env cargado desde: {dotenv_path}")
        else:
            logger.warning("Archivo .env NO encontrado.")
    except Exception as e:
        logger.exception(f"Error al buscar o cargar el archivo .env: {e}")
        return None
    return True


def get_stored_api_key() -> str:
    """Retrieve API key first from system keyring, then fall back to environment variable or .env."""
    load_env()
    key: Optional[str] = None
    try:
        import keyring
        key = keyring.get_password(SERVICE_NAME, API_KEY_NAME)
        if key:
            logger.info("API Key retrieved from system keyring.")
            return key
    except Exception as e:
        logger.warning(f"Failed to access system keyring: {e}")

    env_key = os.getenv(API_KEY_NAME, "")
    if env_key:
        logger.info("API Key retrieved from environment / .env.")
    return env_key


def save_stored_api_key(api_key: str, dotenv_path: Optional[str] = None) -> bool:
    """Save API key to system keyring if available, and also update .env file as fallback."""
    keyring_saved = False
    try:
        import keyring
        keyring.set_password(SERVICE_NAME, API_KEY_NAME, api_key)
        keyring_saved = True
        logger.info("API Key successfully saved to system keyring.")
    except Exception as e:
        logger.warning(f"Could not save API Key to keyring: {e}")

    try:
        if not dotenv_path:
            dotenv_path = find_dotenv(filename='.env', raise_error_if_not_found=False) or '.env'
        set_key(dotenv_path, API_KEY_NAME, api_key)
        logger.info(f"API Key saved to .env at {dotenv_path}")
        os.environ[API_KEY_NAME] = api_key
        return True
    except Exception as e:
        logger.error(f"Error saving API Key to .env: {e}")
        return keyring_saved

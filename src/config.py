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

from i18n import t as get_text, LANGUAGES as TRANSLATIONS


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


from keyring_storage import get_api_key as get_stored_api_key, set_api_key as save_stored_api_key

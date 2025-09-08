"""
Módulo: api.py
Lógica de conexión y consulta a la API de Intelligence X
"""
import requests
import json
import time
import threading
import logging
from datetime import datetime, timezone, MINYEAR, MAXYEAR
from typing import Optional, Tuple, List, Dict, Any, Union

# --- Constantes API ---
INTELX_API_URL_BASE = "https://free.intelx.io"
INTELX_API_URL_SEARCH = f"{INTELX_API_URL_BASE}/intelligent/search"
INTELX_API_URL_RESULT = f"{INTELX_API_URL_BASE}/intelligent/search/result"
INTELX_API_URL_STATUS = f"{INTELX_API_URL_BASE}/intelligent/search/status"
INTELX_API_URL_TERMINATE = f"{INTELX_API_URL_BASE}/intelligent/search/terminate"
INTELX_API_URL_AUTH_INFO = f"{INTELX_API_URL_BASE}/authenticate/info"
INTELX_API_URL_FILE_PREVIEW = f"{INTELX_API_URL_BASE}/file/preview"

INTELX_RATE_LIMIT_DELAY: float = 1.5 # Segundos
MAX_RESULTS_TO_FETCH: int = 1000
MAX_WAIT_TIME_RESULTS: int = 60 # Segundos
WAIT_INTERVAL_RESULTS: int = 3   # Segundos

# Timeouts (segundos)
REQUEST_TIMEOUT_SEARCH: int = 35
REQUEST_TIMEOUT_RESULTS: int = 30
REQUEST_TIMEOUT_STATUS: int = 10
REQUEST_TIMEOUT_AUTH: int = 15
REQUEST_TIMEOUT_TERMINATE: int = 10
REQUEST_TIMEOUT_PREVIEW: int = 20

# Otros
USER_AGENT: str = "Python-CustomTkinter-IntelX-Checker-App/1.3.2"
DEFAULT_DATE_MIN: datetime = datetime(MINYEAR, 1, 1, tzinfo=timezone.utc)
DEFAULT_DATE_MAX: datetime = datetime(MAXYEAR, 12, 31, tzinfo=timezone.utc)

# --- Mapeo completo de Media Type según documentación oficial de IntelX SDK ---
MEDIA_TYPE_MAP: Dict[int, str] = {
    0: "All/Not Set",
    1: "Paste Document", 
    2: "Paste User",
    3: "Forum",
    4: "Forum Board",
    5: "Forum Thread",
    6: "Forum Post",
    7: "Forum User",
    8: "Screenshot of Website",
    9: "HTML copy of Website",
    10: "Text copy of Website",  # Mencionado en PHP SDK pero marcado como inválido en Python
    11: "Invalid/Do Not Use",
    12: "Invalid/Do Not Use", 
    13: "Tweet",
    14: "URL (High-Level Item)",
    15: "PDF Document",
    16: "Word Document",
    17: "Excel Document", 
    18: "PowerPoint Document",
    19: "Picture",
    20: "Audio File",
    21: "Video File",
    22: "Container File (ZIP/RAR/TAR)",
    23: "HTML File",
    24: "Text File",
    25: "Ebook",  # Encontrado en FILE_VIEW función
    26: "Unknown Media Type",
    27: "Source Code",
    28: "Unknown Media Type",
    29: "Unknown Media Type", 
    30: "Unknown Media Type",
    31: "Unknown Media Type",
    32: "Source Code",  # Encontrado en mapeo actual
}

# --- Funciones de Lógica API ---
def check_intelx(
    search_term: str,
    api_key: str,
    selected_buckets: Optional[List[str]] = None,
    cancel_event: Optional[threading.Event] = None
) -> Tuple[bool, Union[str, Dict[str, Any]], Optional[str]]:
    """
    Inicia una búsqueda en IntelX y recupera los resultados.

    Returns:
        Tuple[bool, Union[str, Dict], Optional[str]]: (success, data_or_error_message, search_id)
    """
    if not search_term:
        return False, "Introduce un término de búsqueda válido.", None
    if not api_key:
        return False, "La clave API de IntelX no ha sido proporcionada.", None

    cancel_event = cancel_event or threading.Event()
    if cancel_event.is_set():
        logging.info("Cancelado antes de enviar la solicitud de búsqueda.")
        return False, "Búsqueda cancelada antes de iniciar.", None

    selected_buckets = selected_buckets if selected_buckets is not None else []
    headers = {'x-key': api_key, 'User-Agent': USER_AGENT}
    post_data = {
        "term": search_term,
        "buckets": selected_buckets,
        "lookuplevel": 0,
        "maxresults": MAX_RESULTS_TO_FETCH,
        "timeout": 25,
        "datefrom": "",
        "dateto": "",
        "sort": 2,
        "media": 0,
        "terminate": [],
    }

    logging.info(f"Iniciando búsqueda IntelX para '{search_term}' en buckets: {selected_buckets or 'Todos'}")
    response: Optional[requests.Response] = None
    search_id: Optional[str] = None

    try:
        response = requests.post(
            INTELX_API_URL_SEARCH,
            headers=headers,
            json=post_data,
            timeout=REQUEST_TIMEOUT_SEARCH
        )
        response.raise_for_status()

        search_result = response.json()
        search_id = search_result.get('id')
        initial_status = search_result.get('status', -1)

        if not search_id:
            logging.error("La API de IntelX no devolvió un ID de búsqueda en la respuesta.")
            return False, "Error: IntelX no devolvió un ID de búsqueda.", None

        logging.info(f"Búsqueda iniciada con éxito. ID: {search_id}, Status Inicial: {initial_status}")

        if cancel_event.is_set():
            logging.info(f"Búsqueda {search_id} cancelada inmediatamente después de iniciar.")
            return False, "Búsqueda cancelada.", search_id

        success_retrieve, data_retrieve = retrieve_intelx_results(
            search_id, initial_status, headers, cancel_event
        )
        return success_retrieve, data_retrieve, search_id

    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        try:
            error_detail = err.response.json().get('error', err.response.text)
        except json.JSONDecodeError:
            error_detail = err.response.text
        logging.error(f"Error HTTP {status_code} al iniciar búsqueda: {error_detail}")
        error_message = f"Error IntelX {status_code}"
        if status_code == 401:
            error_message += ": Clave API inválida o sin permisos."
        elif status_code == 402:
            error_message += ": Créditos insuficientes."
        else:
            error_message += f": {error_detail[:100]}"
        return False, error_message, search_id
    except requests.exceptions.Timeout:
        logging.error(f"Timeout ({REQUEST_TIMEOUT_SEARCH}s) al iniciar la búsqueda.")
        return False, f"Error: Timeout ({REQUEST_TIMEOUT_SEARCH}s) al conectar con IntelX.", None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión/red al iniciar búsqueda: {e}", exc_info=True)
        return False, f"Error de conexión de red: {e}", None
    except json.JSONDecodeError:
        resp_text = response.text if response else "N/A"
        logging.error(f"Error al decodificar JSON de la respuesta inicial. Respuesta: {resp_text[:200]}...")
        return False, "Error al procesar la respuesta inicial de IntelX.", None
    except Exception as e:
        logging.exception(f"Error inesperado al iniciar búsqueda para '{search_term}': {e}")
        return False, f"Error inesperado: {e}", search_id

def retrieve_intelx_results(
    search_id: str,
    initial_status: int,
    headers: Dict[str, str],
    cancel_event: threading.Event
) -> Tuple[bool, Union[str, Dict[str, Any]]]:
    """
    Espera y recupera los resultados de una búsqueda IntelX, manejando estados y cancelación.

    Returns:
        Tuple[bool, Union[str, Dict]]: (success, data_or_error_message)
    """
    results_url = f"{INTELX_API_URL_RESULT}?id={search_id}&limit={MAX_RESULTS_TO_FETCH}&previewlines=1"
    status_url = f"{INTELX_API_URL_STATUS}?id={search_id}"
    start_time = time.time()
    current_status = initial_status

    logging.info(f"Procesando ID: {search_id} (estado inicial: {current_status})")

    while True:
        if cancel_event.is_set():
            logging.info(f"ID {search_id}: Proceso de recuperación cancelado.")
            return False, "Búsqueda cancelada."

        if current_status == 0:
            logging.info(f"ID {search_id}: Estado 0 (Completado). Obteniendo resultados...")
            results_response: Optional[requests.Response] = None
            try:
                if cancel_event.is_set(): continue

                results_response = requests.get(results_url, headers=headers, timeout=REQUEST_TIMEOUT_RESULTS)
                results_response.raise_for_status()
                results_data = results_response.json()
                logging.info(f"ID {search_id}: Resultados obtenidos correctamente ({len(results_data.get('records', []))} registros).")
                return True, results_data

            except requests.exceptions.HTTPError as err:
                status_code = err.response.status_code
                resp_text = err.response.text
                logging.error(f"Error HTTP {status_code} obteniendo resultados para {search_id}: {resp_text}")
                msg = f"Error {status_code} obteniendo resultados"
                if status_code == 404: msg += " (Búsqueda no encontrada o expirada)."
                elif status_code == 401: msg += " (Clave API inválida)."
                elif status_code == 402: msg += " (Créditos insuficientes)."
                else: msg += "."
                return False, msg
            except requests.exceptions.Timeout:
                logging.error(f"Timeout ({REQUEST_TIMEOUT_RESULTS}s) obteniendo resultados para {search_id}.")
                return False, f"Error: Timeout ({REQUEST_TIMEOUT_RESULTS}s) obteniendo resultados."
            except requests.exceptions.RequestException as e:
                logging.error(f"Error de red obteniendo resultados para {search_id}: {e}", exc_info=True)
                return False, f"Error de red obteniendo resultados: {e}"
            except json.JSONDecodeError:
                resp_text = results_response.text if results_response else "N/A"
                logging.error(f"Error decodificando JSON de resultados para {search_id}. Respuesta: {resp_text[:200]}...")
                return False, "Error procesando la respuesta de resultados de IntelX."
            except Exception as e:
                logging.exception(f"Error inesperado obteniendo resultados {search_id}: {e}")
                return False, f"Error inesperado: {e}"

        elif current_status == 1:
            logging.info(f"ID {search_id}: Estado 1 (Completado sin resultados).")
            return True, {"records": []}

        elif current_status in [2, 3]:
            status_desc = "En progreso" if current_status == 2 else "Esperando resultados"
            logging.info(f"ID {search_id}: Estado {current_status} ({status_desc}). Esperando...")

            elapsed_time = time.time() - start_time
            if elapsed_time > MAX_WAIT_TIME_RESULTS:
                logging.warning(f"ID {search_id}: Timeout global ({MAX_WAIT_TIME_RESULTS}s) esperando en estado {current_status}.")
                return False, f"Error: Timeout esperando que la búsqueda finalice (Estado {current_status})."

            logging.debug(f"ID {search_id}: Esperando {WAIT_INTERVAL_RESULTS}s antes de consultar estado...")
            if cancel_event.wait(timeout=WAIT_INTERVAL_RESULTS):
                logging.info(f"ID {search_id}: Cancelado durante la espera.")
                continue

            if cancel_event.is_set(): continue

            logging.debug(f"ID {search_id}: Consultando estado actual en {status_url}")
            status_response: Optional[requests.Response] = None
            try:
                status_response = requests.get(status_url, headers=headers, timeout=REQUEST_TIMEOUT_STATUS)
                status_response.raise_for_status()
                status_data = status_response.json()

                if 'status' not in status_data:
                    logging.error(f"Respuesta de estado para {search_id} inválida (sin clave 'status'): {status_data}")
                    return False, "Error: Respuesta de estado de IntelX inválida."

                new_status = status_data['status']
                if new_status != current_status:
                    logging.info(f"ID {search_id}: Estado actualizado de {current_status} a {new_status}.")
                    current_status = new_status
                else:
                    logging.debug(f"ID {search_id}: Estado sigue siendo {current_status}.")

            except requests.exceptions.HTTPError as err:
                status_code = err.response.status_code
                resp_text = err.response.text
                logging.error(f"Error HTTP {status_code} verificando estado {search_id}: {resp_text}")
                msg = f"Error {status_code} verificando estado"
                if status_code == 404: msg += " (ID de búsqueda no encontrado)."
                elif status_code == 401: msg += " (Clave API inválida)."
                else: msg += "."
                return False, msg
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout ({REQUEST_TIMEOUT_STATUS}s) verificando estado {search_id}. Se continuará esperando...")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Error de red verificando estado {search_id}: {e}. Se continuará esperando...")
            except json.JSONDecodeError:
                resp_text = status_response.text if status_response else "N/A"
                logging.error(f"Error decodificando JSON de estado para {search_id}. Respuesta: {resp_text[:200]}...")
                return False, "Error procesando la respuesta de estado de IntelX."
            except Exception as e:
                logging.exception(f"Error inesperado verificando estado {search_id}: {e}")
                return False, f"Error inesperado: {e}"

        else:
            logging.error(f"ID {search_id}: Estado inesperado o fallido encontrado: {current_status}")
            return False, f"Error: Estado de búsqueda inesperado o fallido ({current_status})."

def get_api_credits(api_key: str) -> Tuple[bool, Union[int, str]]:
    """
    Obtiene los créditos restantes de la API de IntelX usando el endpoint /authenticate/info.
    Basado en el SDK oficial de IntelX que usa GET_CAPABILITIES().
    
    Returns:
        Tuple[bool, Union[int, str]]: (success, credits_or_error_message)
    """
    if not api_key:
        return False, "Clave API no proporcionada"
    
    headers = {'x-key': api_key, 'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(
            INTELX_API_URL_AUTH_INFO,
            headers=headers,
            timeout=REQUEST_TIMEOUT_AUTH
        )
        response.raise_for_status()
        
        auth_info = response.json()
        
        # Extraer créditos del endpoint de búsqueda según la estructura real de la API
        credits = 0
        if 'paths' in auth_info and '/intelligent/search' in auth_info['paths']:
            search_info = auth_info['paths']['/intelligent/search']
            credits = search_info.get('Credit', 0)
            
        # Si no se encuentran créditos en paths, intentar campos directos
        if credits == 0:
            credits = auth_info.get('credits', 0)
            if credits == 0:
                credits = auth_info.get('dailySearchCredits', 0)
            if credits == 0:
                credits = auth_info.get('searchCredits', 0)
        
        logging.info(f"Créditos de búsqueda disponibles: {credits}")
        return True, credits
        
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code
        try:
            error_detail = err.response.json().get('error', err.response.text)
        except json.JSONDecodeError:
            error_detail = err.response.text
        
        logging.error(f"Error HTTP {status_code} obteniendo créditos: {error_detail}")
        
        if status_code == 401:
            return False, "Clave API inválida"
        elif status_code == 402:
            return False, "Sin créditos disponibles"
        else:
            return False, f"Error {status_code}: {error_detail[:100]}"
            
    except requests.exceptions.Timeout:
        logging.error(f"Timeout ({REQUEST_TIMEOUT_AUTH}s) obteniendo créditos.")
        return False, f"Timeout al obtener créditos"
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión obteniendo créditos: {e}")
        return False, f"Error de conexión: {e}"
        
    except json.JSONDecodeError:
        resp_text = response.text if response else "N/A"
        logging.error(f"Error decodificando JSON de créditos. Respuesta: {resp_text[:200]}...")
        return False, "Error procesando respuesta de créditos"
        
    except Exception as e:
        logging.exception(f"Error inesperado obteniendo créditos: {e}")
        return False, f"Error inesperado: {e}"

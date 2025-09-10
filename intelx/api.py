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
USER_AGENT: str = "Python-CustomTkinter-IntelX-Checker-App/2.0.0"
DEFAULT_DATE_MIN: datetime = datetime(MINYEAR, 1, 1, tzinfo=timezone.utc)
DEFAULT_DATE_MAX: datetime = datetime(MAXYEAR, 12, 31, tzinfo=timezone.utc)

# --- Mapeo completo de Media Type según documentación oficial de IntelX SDK ---
MEDIA_TYPE_MAP: Dict[int, str] = {
    0: "All/Not Set", 1: "Paste Document", 2: "Paste User", 3: "Forum",
    4: "Forum Board", 5: "Forum Thread", 6: "Forum Post", 7: "Forum User",
    8: "Screenshot of Website", 9: "HTML copy of Website", 10: "Text copy of Website",
    11: "Invalid/Do Not Use", 12: "Invalid/Do Not Use", 13: "Tweet",
    14: "URL (High-Level Item)", 15: "PDF Document", 16: "Word Document",
    17: "Excel Document", 18: "PowerPoint Document", 19: "Picture",
    20: "Audio File", 21: "Video File", 22: "Container File (ZIP/RAR/TAR)",
    23: "HTML File", 24: "Text File", 25: "Ebook", 26: "Unknown Media Type",
    27: "Source Code", 28: "Unknown Media Type", 29: "Unknown Media Type",
    30: "Unknown Media Type", 31: "Unknown Media Type", 32: "Source Code",
}

class IntelXAPI:
    """
    Wrapper para la API de Intelligence X que maneja la autenticación,
    búsquedas y recuperación de resultados de forma centralizada.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("La clave API de IntelX no puede estar vacía.")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'x-key': self.api_key,
            'User-Agent': USER_AGENT
        })

    def search(
        self,
        search_term: str,
        selected_buckets: Optional[List[str]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Tuple[bool, Union[str, Dict[str, Any]], Optional[str]]:
        """
        Inicia una búsqueda en IntelX y recupera los resultados.
        """
        if not search_term:
            return False, "Introduce un término de búsqueda válido.", None

        cancel_event = cancel_event or threading.Event()
        if cancel_event.is_set():
            logging.info("Cancelado antes de enviar la solicitud de búsqueda.")
            return False, "Búsqueda cancelada antes de iniciar.", None

        post_data = {
            "term": search_term,
            "buckets": selected_buckets or [],
            "lookuplevel": 0, "maxresults": MAX_RESULTS_TO_FETCH, "timeout": 25,
            "datefrom": "", "dateto": "", "sort": 2, "media": 0, "terminate": [],
        }

        logging.info(f"Iniciando búsqueda IntelX para '{search_term}' en buckets: {selected_buckets or 'Todos'}")
        response: Optional[requests.Response] = None
        search_id: Optional[str] = None

        try:
            response = self.session.post(
                INTELX_API_URL_SEARCH,
                json=post_data,
                timeout=REQUEST_TIMEOUT_SEARCH
            )
            response.raise_for_status()
            search_result = response.json()
            search_id = search_result.get('id')
            initial_status = search_result.get('status', -1)

            if not search_id:
                logging.error("La API de IntelX no devolvió un ID de búsqueda.")
                return False, "Error: IntelX no devolvió un ID de búsqueda.", None

            logging.info(f"Búsqueda iniciada con ID: {search_id}, Status Inicial: {initial_status}")

            if cancel_event.is_set():
                logging.info(f"Búsqueda {search_id} cancelada inmediatamente después de iniciar.")
                self.terminate_search(search_id)
                return False, "Búsqueda cancelada.", search_id

            return self._retrieve_results(search_id, initial_status, cancel_event)

        except requests.exceptions.HTTPError as err:
            return self._handle_http_error(err, search_id)
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

    def _retrieve_results(
        self,
        search_id: str,
        initial_status: int,
        cancel_event: threading.Event
    ) -> Tuple[bool, Union[str, Dict[str, Any]], Optional[str]]:
        """
        Espera y recupera los resultados de una búsqueda, manejando estados y cancelación.
        """
        start_time = time.time()
        current_status = initial_status

        logging.info(f"Procesando ID: {search_id} (estado inicial: {current_status})")

        while True:
            if cancel_event.is_set():
                logging.info(f"ID {search_id}: Proceso de recuperación cancelado.")
                self.terminate_search(search_id)
                return False, "Búsqueda cancelada.", search_id

            if current_status == 0: # Completado con resultados
                return self._fetch_final_results(search_id)

            elif current_status == 1: # Completado sin resultados
                logging.info(f"ID {search_id}: Estado 1 (Completado sin resultados).")
                return True, {"records": []}, search_id

            elif current_status in [2, 3]: # En progreso
                if time.time() - start_time > MAX_WAIT_TIME_RESULTS:
                    logging.warning(f"ID {search_id}: Timeout global ({MAX_WAIT_TIME_RESULTS}s) esperando.")
                    self.terminate_search(search_id)
                    return False, "Error: Timeout esperando que la búsqueda finalice.", search_id

                if cancel_event.wait(timeout=WAIT_INTERVAL_RESULTS):
                    continue # Si el evento se activa, el bucle principal lo capturará

                success, new_status = self._check_search_status(search_id)
                if success:
                    if new_status != current_status:
                        logging.info(f"ID {search_id}: Estado actualizado de {current_status} a {new_status}.")
                        current_status = new_status
                else:
                    # Si falla la comprobación de estado, se sigue intentando hasta el timeout
                    logging.warning(f"No se pudo obtener el estado para {search_id}. Reintentando...")

            else: # Estado inesperado o fallido
                logging.error(f"ID {search_id}: Estado inesperado o fallido encontrado: {current_status}")
                return False, f"Error: Estado de búsqueda inesperado o fallido ({current_status}).", search_id

    def _fetch_final_results(self, search_id: str) -> Tuple[bool, Union[str, Dict], Optional[str]]:
        """Obtiene los resultados finales de una búsqueda completada."""
        logging.info(f"ID {search_id}: Estado 0 (Completado). Obteniendo resultados...")
        results_url = f"{INTELX_API_URL_RESULT}?id={search_id}&limit={MAX_RESULTS_TO_FETCH}&previewlines=1"
        try:
            response = self.session.get(results_url, timeout=REQUEST_TIMEOUT_RESULTS)
            response.raise_for_status()
            results_data = response.json()
            logging.info(f"ID {search_id}: Resultados obtenidos ({len(results_data.get('records', []))} registros).")
            return True, results_data, search_id
        except requests.exceptions.HTTPError as err:
            return self._handle_http_error(err, search_id)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.error(f"Error obteniendo resultados para {search_id}: {e}", exc_info=True)
            return False, f"Error al obtener resultados finales: {e}", search_id

    def _check_search_status(self, search_id: str) -> Tuple[bool, int]:
        """Consulta el estado actual de una búsqueda."""
        status_url = f"{INTELX_API_URL_STATUS}?id={search_id}"
        try:
            response = self.session.get(status_url, timeout=REQUEST_TIMEOUT_STATUS)
            response.raise_for_status()
            status_data = response.json()
            if 'status' not in status_data:
                logging.error(f"Respuesta de estado para {search_id} inválida: {status_data}")
                return False, -1
            return True, status_data['status']
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return False, -1

    def get_credits(self) -> Tuple[bool, Union[int, str]]:
        """Obtiene los créditos restantes de la API."""
        try:
            response = self.session.get(INTELX_API_URL_AUTH_INFO, timeout=REQUEST_TIMEOUT_AUTH)
            response.raise_for_status()
            auth_info = response.json()
            
            credits = 0
            if 'paths' in auth_info and '/intelligent/search' in auth_info['paths']:
                credits = auth_info['paths']['/intelligent/search'].get('Credit', 0)
            
            if credits == 0: # Fallback a otros campos
                credits = auth_info.get('credits', auth_info.get('dailySearchCredits', auth_info.get('searchCredits', 0)))

            logging.info(f"Créditos de búsqueda disponibles: {credits}")
            return True, credits
            
        except requests.exceptions.HTTPError as err:
            success, msg, _ = self._handle_http_error(err)
            return success, msg
        except (requests.exceptions.Timeout, requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.error(f"Error obteniendo créditos: {e}", exc_info=True)
            return False, f"Error al obtener créditos: {e}"
        except Exception as e:
            logging.exception(f"Error inesperado obteniendo créditos: {e}")
            return False, f"Error inesperado: {e}"

    def terminate_search(self, search_id: str) -> bool:
        """Termina una búsqueda en curso en IntelX."""
        if not search_id:
            return False
        terminate_url = f"{INTELX_API_URL_TERMINATE}?id={search_id}"
        try:
            response = self.session.get(terminate_url, timeout=REQUEST_TIMEOUT_TERMINATE)
            response.raise_for_status()
            logging.info(f"Solicitud de terminación enviada para la búsqueda {search_id}.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al intentar terminar la búsqueda {search_id}: {e}")
            return False

    def get_file_preview(self, system_id: str, file_type: int = 0, escape: bool = False) -> Tuple[bool, str]:
        """
        Obtiene la vista previa de un fichero.
        """
        params = {
            "sid": system_id,
            "f": file_type,
            "es": 1 if escape else 0,
            "l": 200 # Limitar a 200 líneas por defecto
        }
        try:
            response = self.session.get(INTELX_API_URL_FILE_PREVIEW, params=params, timeout=REQUEST_TIMEOUT_PREVIEW)
            response.raise_for_status()
            return True, response.text
        except requests.exceptions.HTTPError as err:
            success, msg, _ = self._handle_http_error(err)
            return success, msg
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            logging.error(f"Error obteniendo preview para {system_id}: {e}", exc_info=True)
            return False, f"Error de red o timeout: {e}"

    def _handle_http_error(self, err: requests.exceptions.HTTPError, search_id: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Manejador centralizado para errores HTTP."""
        status_code = err.response.status_code
        try:
            error_detail = err.response.json().get('error', err.response.text)
        except json.JSONDecodeError:
            error_detail = err.response.text
        
        logging.error(f"Error HTTP {status_code}: {error_detail} (ID: {search_id or 'N/A'})")
        
        if status_code == 401:
            message = "Clave API inválida o sin permisos."
        elif status_code == 402:
            message = "Créditos insuficientes."
        elif status_code == 404:
            message = "Recurso no encontrado o búsqueda expirada."
        else:
            message = f"Error {status_code}: {error_detail[:100]}"
            
        return False, message, search_id

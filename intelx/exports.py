"""Export helpers: CSV, JSON and simple PDF generation extracted from the legacy GUI.

These functions are UI-agnostic and return the path of the created file. The GUI
can display messages or open the file/folder as needed.
"""
import os
import json
import csv
import threading
import logging
from datetime import datetime
from typing import List, Dict, Any, Callable

from .html_report import generate_html_report
from .utils import sanitize_filename
from . import ui_components # Para los diálogos

logger = logging.getLogger(__name__)

def _get_export_filepath(search_term: str, format_name: str) -> str:
    """Genera una ruta de archivo estandarizada para la exportación."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    # Asegurarse de que el directorio de reportes exista
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    sanitized_term = sanitize_filename(search_term or 'IntelX_Report')
    filename = f"{sanitized_term}_{timestamp}.{format_name.lower()}"
    return os.path.join(reports_dir, filename)

def export_to_csv(records: List[Dict[str, Any]], output_filepath: str, **kwargs):
    """Exporta una lista de diccionarios a un archivo CSV."""
    try:
        if not records:
            return None
        
        # Encabezados dinámicos basados en todas las claves posibles
        headers = sorted(list(set(key for record in records for key in record.keys())))
        
        with open(output_filepath, 'w', encoding='utf-8', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            for record in records:
                # Asegurar que todos los valores sean primitivos
                row = {k: str(v) if v is not None else '' for k, v in record.items()}
                writer.writerow(row)
        logger.info(f"Exportación a CSV completada en: {output_filepath}")
        return output_filepath
    except Exception as e:
        logger.exception(f"Error al exportar a CSV en {output_filepath}")
        raise

def export_to_json(records: List[Dict[str, Any]], output_filepath: str, **kwargs):
    """Exporta una lista de diccionarios a un archivo JSON."""
    try:
        with open(output_filepath, 'w', encoding='utf-8') as fh:
            json.dump(records, fh, indent=2, ensure_ascii=False)
        logger.info(f"Exportación a JSON completada en: {output_filepath}")
        return output_filepath
    except Exception as e:
        logger.exception(f"Error al exportar a JSON en {output_filepath}")
        raise

def export_to_html(records: List[Dict[str, Any]], output_filepath: str, search_term: str = "", app_version: str = "2.0.0", **kwargs):
    """Exporta una lista de diccionarios a un archivo HTML."""
    try:
        return generate_html_report(records, output_filepath, search_term, app_version)
    except Exception as e:
        logger.exception(f"Error al exportar a HTML en {output_filepath}")
        raise

def export_safe(parent_app, export_function: Callable, records: List[Dict], format_name: str, **kwargs):
    """
    Ejecuta una función de exportación en un hilo separado para no bloquear la UI.
    Maneja la actualización de la barra de estado y los diálogos de éxito/error.
    """
    if not records:
        ui_components.show_custom_messagebox(parent_app, "Sin Datos", "No hay resultados para exportar.", "warning")
        return

    search_term = parent_app.term_entry.get().strip()
    
    # Iniciar el worker en un hilo
    thread = threading.Thread(
        target=_export_worker,
        args=(parent_app, export_function, records, format_name, search_term),
        kwargs=kwargs
    )
    thread.daemon = True
    thread.start()

def _export_worker(parent_app, export_function: Callable, records: List[Dict], format_name: str, search_term: str, **kwargs):
    """Worker que se ejecuta en un hilo para realizar la exportación."""
    try:
        # Actualizar UI - Inicio
        def update_status_start():
            parent_app.status_label.configure(text=f"Exportando a {format_name}...")
            parent_app.progress_bar.start()
        parent_app.after(0, update_status_start)

        # Generar ruta y ejecutar exportación
        output_filepath = _get_export_filepath(search_term, format_name)
        
        # Pasar argumentos específicos a la función de exportación
        export_kwargs = kwargs.copy()
        if export_function == generate_html_report:
            export_kwargs['app_version'] = parent_app.app_version
        
        filepath = export_function(records, output_filepath, **export_kwargs)

        # Actualizar UI - Éxito
        def update_status_success():
            parent_app.status_label.configure(text=f"Exportación a {format_name} completada.")
            parent_app.progress_bar.stop()
            parent_app.progress_bar.set(0)
            ui_components.show_export_success_dialog(parent_app, filepath)
        parent_app.after(0, update_status_success)

    except Exception as e:
        logger.exception(f"Error exportando a {format_name}")
        # Actualizar UI - Error
        def update_status_error():
            error_message = str(e)
            parent_app.status_label.configure(text=f"Error en exportación a {format_name}.")
            parent_app.progress_bar.stop()
            parent_app.progress_bar.set(0)
            ui_components.show_custom_messagebox(parent_app, 'Error', f"Error exportando a {format_name}: {error_message}", 'error')
        parent_app.after(0, update_status_error)

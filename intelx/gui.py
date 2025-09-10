"""
Módulo: gui.py
Interfaz gráfica principal usando CustomTkinter y Tkinter
Versión modular que mantiene toda la funcionalidad original
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, Menu, filedialog, ttk
import requests
import json
import time
import threading
import webbrowser
import os
from dotenv import load_dotenv, find_dotenv, set_key
from datetime import datetime, timezone, MINYEAR, MAXYEAR
import queue
import csv
import logging
import sys
import io
from collections import Counter
from typing import Optional, Tuple, List, Dict, Any, Union
try:
    from PIL import Image, ImageTk
except ImportError:
    _pillow_warning_root = None
    try:
        _pillow_warning_root = tk.Tk()
        _pillow_warning_root.withdraw()
        messagebox.showwarning(
            "Dependencia Faltante",
            "Pillow no está instalado.\nLa vista previa de imágenes no funcionará.\n\nInstálalo ejecutando:\npip install Pillow"
        )
    except tk.TclError:
        print("ADVERTENCIA: Pillow no está instalado y no se pudo mostrar el messagebox (quizás no hay entorno gráfico disponible).")
    finally:
        if _pillow_warning_root:
            _pillow_warning_root.destroy()
    Image = None
    ImageTk = None

# Imports de módulos propios
from .api import IntelXAPI, MEDIA_TYPE_MAP
from .analysis import extract_iocs
from .html_report import generate_html_report
from .utils import sanitize_filename, open_in_browser
from . import exports as exports_module
from . import ui_components

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(threadName)-15s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

class IntelXCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.preview_windows = {}
        self.title("IntelX Checker V2")
        # Establecer icono de la aplicación si existe
        try:
            # Compatibilidad con PyInstaller (atributo _MEIPASS) y modo script
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(__file__)))
            icon_path = os.path.join(base_dir, 'docs', 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                logger.debug(f"Icono no encontrado en ruta esperada: {icon_path}")
        except Exception as _icon_err:
            logger.debug(f"No se pudo establecer el icono: {_icon_err}")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.current_language = "es"
        self.app_version = "2.0.0"
        
        # --- Fuentes por defecto ---
        self.fonts = {
            "main": ("Arial", 14),
            "main_bold": ("Arial", 14, "bold"),
            "menu": ("Arial", 12),
            "secondary": ("Arial", 11),
            "tertiary": ("Arial", 10),
            "tree_content": ("Arial", 11),
            "tree_header": ("Arial", 12),
            "dialog_header": ("Arial", 13),
            "dialog_body": ("Arial", 11)
        }
        
        # --- Multilenguaje ---
        self.current_language = self._load_saved_language()
        self.languages = {
            "es": {
                "Correo o Dominio": "Correo o Dominio:",
                "Buscar": "Buscar",
                "Cancelar": "Cancelar",
                "Listo": "Listo.",
                "Filtrar resultados": "Filtrar resultados...",
                "Créditos": "Créditos:",
                "Archivo": "Archivo",
                "Exportar a CSV": "Exportar a CSV...",
                "Exportar a JSON": "Exportar a JSON...",
                "Exportar a PDF": "Exportar a PDF...",
                "Exportar a HTML": "Exportar a HTML...",
                "Vista Previa": "Vista Previa",
                "Seleccionar Todo": "Seleccionar Todo",
                "Deseleccionar": "Deseleccionar",
                "Copiar": "Copiar",
                "Exportar Selección": "Exportar Selección",
                "Refrescar": "Refrescar",
                "Ajustar Columnas": "Ajustar Columnas",
                "Salir": "Salir",
                "Configuración": "Configuración",
                "Gestionar Clave API": "Gestionar Clave API...",
                "Fuentes de Búsqueda": "Fuentes de Búsqueda (Buckets)...",
                "Ayuda": "Ayuda",
                "Refrescar Créditos": "Refrescar Créditos",
                "Obtener Clave API": "Obtener Clave API de IntelX",
                "Acerca de": "Acerca de"
            },
            "en": {
                "Correo o Dominio": "Email or Domain:",
                "Buscar": "Search",
                "Cancelar": "Cancel",
                "Listo": "Done.",
                "Filtrar resultados": "Filter results...",
                "Créditos": "Credits:",
                "Archivo": "File",
                "Exportar a CSV": "Export to CSV...",
                "Exportar a JSON": "Export to JSON...",
                "Exportar a PDF": "Export to PDF...",
                "Exportar a HTML": "Export to HTML...",
                "Vista Previa": "Preview",
                "Seleccionar Todo": "Select All",
                "Deseleccionar": "Deselect",
                "Copiar": "Copy",
                "Exportar Selección": "Export Selection",
                "Refrescar": "Refresh",
                "Ajustar Columnas": "Adjust Columns",
                "Salir": "Exit",
                "Configuración": "Settings",
                "Gestionar Clave API": "Manage API Key...",
                "Fuentes de Búsqueda": "Search Sources (Buckets)...",
                "Ayuda": "Help",
                "Refrescar Créditos": "Refresh Credits",
                "Obtener Clave API": "Get IntelX API Key",
                "Acerca de": "About"
            }
        }
        
        # Inicializar variables
        self.current_records = []
        self.credits = 0
        self.search_thread = None
        self.stop_search = False
        self.cancel_event = None
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        self.sort_column = "date"
        self.sort_reverse = True
        self.all_records = []
        
        # Crear UI
        self._setup_ui()
        self._setup_menus()
        self._update_language()
        
        # Cargar configuración
        self._load_api_config()
        
    def _load_saved_language(self):
        """Carga el idioma guardado"""
        try:
            if os.path.exists(self.config_file):
                load_dotenv(self.config_file)
                return os.getenv('LANGUAGE', 'es')
        except:
            pass
        return 'es'
    
    def _setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Label y entry para término de búsqueda
        self.search_label = ctk.CTkLabel(search_frame, text="Correo o Dominio:", font=self.fonts["main"])
        self.search_label.pack(side="left", padx=(10, 5))
        
        self.term_entry = ctk.CTkEntry(search_frame, font=self.fonts["main"], width=300)
        self.term_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.term_entry.bind("<Return>", lambda e: self.search_intelx())
        
        # Botones de búsqueda
        self.search_button = ctk.CTkButton(search_frame, text="Buscar", command=self.search_intelx, font=self.fonts["main"])
        self.search_button.pack(side="right", padx=(5, 10))
        
        self.cancel_button = ctk.CTkButton(search_frame, text="Cancelar", command=self.cancel_search, font=self.fonts["main"])
        self.cancel_button.pack(side="right", padx=5)
        self.cancel_button.configure(state="disabled")
        
        # Frame de filtros
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        self.filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Filtrar resultados...", font=self.fonts["secondary"])
        self.filter_entry.pack(side="left", padx=(10, 5), expand=True, fill="x")
        self.filter_entry.bind("<KeyRelease>", self.filter_results)
        
        # Year filter
        self.year_entry = ctk.CTkEntry(filter_frame, placeholder_text="Año", width=80)
        self.year_entry.pack(side="left", padx=5)
        self.filter_year_button = ctk.CTkButton(filter_frame, text="Filtrar Año", command=self._filter_by_year, width=100)
        self.filter_year_button.pack(side="left", padx=5)
        self.clear_year_filter_button = ctk.CTkButton(filter_frame, text="Limpiar", command=self._clear_year_filter, width=80)
        self.clear_year_filter_button.pack(side="left", padx=5)
        
        # Label de créditos
        self.credits_label = ctk.CTkLabel(filter_frame, text="Créditos: 0", font=self.fonts["secondary"])
        self.credits_label.pack(side="right", padx=(5, 10))
        
        # Frame de resultados
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para resultados con columnas reordenadas por prioridad
        columns = ("date", "name", "ip", "type", "media", "bucket", "size", "score", "systemid")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings", height=15)
        
        # Configurar columnas
        self.results_tree.heading("#0", text="", anchor="w")
        self.results_tree.column("#0", width=0, minwidth=0)
        
        # Configurar columnas con anchos específicos (fecha como prioridad)
        column_widths = {
            "date": 130,      # Fecha (primera prioridad)
            "name": 200,      # Nombre del archivo/documento
            "ip": 120,        # Dirección IP
            "type": 80,       # Tipo de contenido
            "media": 100,     # Tipo de media
            "bucket": 120,    # Bucket/fuente
            "size": 80,       # Tamaño
            "score": 60,      # Puntuación de relevancia
            "systemid": 200   # ID del sistema
        }
        
        for col in columns:
            self.results_tree.heading(col, text=col.capitalize(), anchor="w", command=lambda c=col: self._sort_by_column(c, False))
            width = column_widths.get(col, 120)
            self.results_tree.column(col, width=width, minwidth=60)
        
        # Scrollbars para treeview
        v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid para treeview y scrollbars
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Bind eventos del treeview
        self.results_tree.bind("<Double-1>", self.on_item_double_click)
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        
        # Status bar con barra de progreso
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Listo.", font=self.fonts["tertiary"])
        self.status_label.pack(side="left", padx=(10, 5))
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.pack(side="right", padx=(5, 10))
        self.progress_bar.set(0)
    
    def _setup_menus(self):
        """Configurar menús"""
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # Menú Archivo
        file_menu = Menu(menubar, tearoff=0, font=self.fonts["menu"])
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a CSV...", command=self.export_to_csv)
        file_menu.add_command(label="Exportar a JSON...", command=self.export_to_json)
        file_menu.add_command(label="Exportar a HTML...", command=self.export_to_html)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        
        # Menú Configuración
        config_menu = Menu(menubar, tearoff=0, font=self.fonts["menu"])
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Gestionar Clave API...", command=self.manage_api_key)
        config_menu.add_separator()
        config_menu.add_command(label="Español", command=lambda: self._set_language("es"))
        config_menu.add_command(label="English", command=lambda: self._set_language("en"))
        config_menu.add_separator()
        config_menu.add_command(label="Tema Claro", command=lambda: self._set_theme("light"))
        config_menu.add_command(label="Tema Oscuro", command=lambda: self._set_theme("dark"))
        
        # Menú Ayuda
        help_menu = Menu(menubar, tearoff=0, font=self.fonts["menu"])
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Refrescar Créditos", command=self.refresh_credits)
        help_menu.add_command(label="Obtener Clave API", command=self.open_intelx_api_page)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
        # Menú contextual para treeview
        self.context_menu = Menu(self, tearoff=0, font=self.fonts["menu"])
        self.context_menu.add_command(label="Vista Previa", command=self.preview_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Seleccionar Todo", command=self.select_all)
        self.context_menu.add_command(label="Deseleccionar", command=self.deselect_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copiar", command=self.copy_selected)
        self.context_menu.add_command(label="Exportar Selección", command=self.export_selection)

    def _set_language(self, lang):
        """Cambiar idioma"""
        self.current_language = lang
        self._save_language()
        self._update_language()
    
    def _set_theme(self, theme):
        """Cambiar tema"""
        ctk.set_appearance_mode(theme)
    
    def _save_language(self):
        """Guardar idioma seleccionado"""
        try:
            set_key(self.config_file, 'LANGUAGE', self.current_language)
        except:
            pass
    
    def _update_language(self):
        """Actualizar textos según idioma"""
        lang = self.languages.get(self.current_language, self.languages["es"])
        
        # Actualizar elementos UI
        self.search_label.configure(text=lang["Correo o Dominio"])
        self.search_button.configure(text=lang["Buscar"])
        self.cancel_button.configure(text=lang["Cancelar"])
        self.filter_entry.configure(placeholder_text=lang["Filtrar resultados"])
        self.credits_label.configure(text=f"{lang['Créditos']} {self.credits}")
        self.status_label.configure(text=lang["Listo"])
        
        # Actualizar headers del treeview
        self._update_treeview_headers()
    
    def _update_treeview_headers(self):
        """Actualizar headers del treeview según idioma"""
        lang = self.languages.get(self.current_language, self.languages["es"])
        
        headers = {
            "date": "Fecha" if self.current_language == "es" else "Date",
            "name": "Nombre" if self.current_language == "es" else "Name",
            "ip": "IP" if self.current_language == "es" else "IP",
            "type": "Tipo" if self.current_language == "es" else "Type", 
            "media": "Media",
            "bucket": "Fuente" if self.current_language == "es" else "Source",
            "size": "Tamaño" if self.current_language == "es" else "Size",
            "score": "Puntuación" if self.current_language == "es" else "Score",
            "systemid": "ID Sistema" if self.current_language == "es" else "System ID"
        }
        
        for col, header in headers.items():
            self.results_tree.heading(col, text=header)
    
    def _load_api_config(self):
        """Cargar configuración de API y crear cliente."""
        try:
            load_dotenv(self.config_file)
            self.api_key = os.getenv('INTELX_API_KEY', '')
            if self.api_key:
                self.api_client = IntelXAPI(self.api_key)
                self.refresh_credits()
            else:
                self.api_client = None
        except Exception as e:
            logger.error(f"Error al cargar la configuración de la API: {e}")
            self.api_key = ''
            self.api_client = None
    
    def search_intelx(self):
        """Inicia una búsqueda en IntelX en un hilo para evitar congelar la UI."""
        term = self.term_entry.get().strip()
        if not term:
            messagebox.showwarning("Error", "Ingrese un término de búsqueda")
            return
        if not self.api_client:
            messagebox.showwarning("Error", "Configure su clave API primero")
            self.manage_api_key()
            return

        # Async refresh de créditos (no bloquea la UI)
        self.refresh_credits_async()

        # Limpiar resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.current_records = []
        self.stop_search = False

        # Estado inicial UI
        self.search_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_label.configure(text="Iniciando búsqueda...")
        self.progress_bar.set(0.1)

        self.cancel_event = threading.Event()

        # Lanzar hilo de búsqueda
        self.search_thread = threading.Thread(target=self._search_worker, args=(term, self.cancel_event))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def _search_worker(self, term, cancel_event):
        """Worker para búsqueda en hilo separado"""
        try:
            self.after(0, lambda: self.progress_bar.set(0.3))
            self.after(0, lambda: self.status_label.configure(text="Conectando con IntelX..."))
            
            # Usar el cliente de API
            success, data_or_error, search_id = self.api_client.search(term, selected_buckets=self._get_selected_buckets(), cancel_event=cancel_event)
            
            self.after(0, lambda: self.progress_bar.set(0.7))
            
            if success:
                self.after(0, lambda: self.status_label.configure(text="Procesando resultados..."))
                
                # Normalizar los resultados a una lista de diccionarios
                normalized_records = self._normalize_records(data_or_error)
                self.current_records = normalized_records
                self.all_records = list(normalized_records) # Copia para el filtro
                
                self.after(0, lambda: self.progress_bar.set(1.0))
                
                if self.current_records and not self.stop_search:
                    # Poblar de forma incremental para evitar congelar la UI
                    self.after(0, lambda: self._populate_results_chunked(self.current_records))
                    self.after(0, lambda: self.status_label.configure(text=f"Insertando {len(self.current_records)} resultados..."))
                else:
                    self.after(0, lambda: self.status_label.configure(text="No se encontraron resultados"))
            else:
                error_msg = data_or_error if isinstance(data_or_error, str) else "Error en la búsqueda"
                self.after(0, lambda: self.status_label.configure(text=error_msg))
                self.after(0, lambda: self.progress_bar.set(0))
                
        except Exception as e:
            logger.exception("Error en búsqueda")
            self.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))
            self.after(0, lambda: self.progress_bar.set(0))
        finally:
            self.after(0, self._search_finished)

    def _get_selected_buckets(self) -> Optional[List[str]]:
        """
        Obtiene la lista de buckets de búsqueda seleccionados desde la configuración.
        Este es un placeholder. La lógica real para seleccionar buckets
        debería implementarse en un diálogo de configuración.
        """
        # Por ahora, devuelve None para buscar en todos los buckets.
        # TODO: Implementar un diálogo para que el usuario seleccione buckets.
        return None

    def _normalize_records(self, data: Union[Dict, List, str, None]) -> List[Dict]:
        """
        Normaliza los datos de los registros a una lista de diccionarios.
        Maneja diferentes formatos de entrada (dict, list, str).
        """
        if not data:
            return []

        if isinstance(data, dict) and 'records' in data:
            raw_records = data['records']
        elif isinstance(data, list):
            raw_records = data
        else:
            # Envuelve cualquier otro tipo en una lista para un manejo uniforme
            raw_records = [data]

        normalized_list = []
        for i, record in enumerate(raw_records):
            if isinstance(record, dict):
                # Asegurarse de que los campos clave existan con valores por defecto
                record.setdefault('systemid', record.get('storageid', f'record_{i}'))
                record.setdefault('name', f'Documento {i+1}')
                record.setdefault('date', '')
                record.setdefault('size', 0)
                record.setdefault('xscore', 0)
                record.setdefault('bucket', 'unknown')
                record.setdefault('type', 0)
                record.setdefault('media', 0)
                normalized_list.append(record)
            elif isinstance(record, str):
                # Convertir un resultado de tipo string a un diccionario estándar
                normalized_list.append({
                    'systemid': f'record_{i}',
                    'name': f'Resultado de texto {i+1}',
                    'date': '',
                    'size': len(record),
                    'xscore': 0,
                    'bucket': 'unknown',
                    'type': 1,  # Texto plano
                    'media': 1, # Paste Document
                    'data': record # Guardar el contenido original
                })
            # Ignorar otros tipos de datos no esperados para evitar errores
        
        return normalized_list

    def _populate_results(self, records_to_show):
        """Poblar treeview con resultados"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for i, record_dict in enumerate(records_to_show):
            if self.stop_search:
                break
                
            # Fecha formateada
            date_str = record_dict.get('date', '')
            date_text = date_str[:19] if date_str and len(date_str) > 19 else (date_str or 'N/A')
                
            # Formatear datos basándose en la estructura del diccionario
            name = record_dict.get('name', f'Documento {i+1}')
            name = name[:60] + "..." if len(name) > 60 else name
            
            # Extraer IP del nombre o datos
            ip_address = self._extract_ip_address(record_dict)
            
            # Tipo de contenido (type)
            type_text = self._get_type_description(record_dict.get('type', 0))
            
            # Media type (más descriptivo)
            media_text = self._get_media_description(record_dict.get('media', 0))
            
            # Bucket con nombre legible
            bucket = record_dict.get('bucket', 'unknown')
            bucket_text = record_dict.get('bucketh', bucket)  # bucketh es el nombre legible
            
            # Tamaño formateado
            size_text = self._format_file_size(record_dict.get('size', 0))
            
            # Puntuación de relevancia (xscore)
            score = record_dict.get('xscore', 0)
            score_text = str(score) if score > 0 else 'N/A'
            
            # System ID
            system_id = record_dict.get('systemid', str(i))
            
            # Nuevo orden: fecha, nombre, IP, tipo, media, bucket, tamaño, score, systemid
            self.results_tree.insert("", "end", values=(
                date_text, name, ip_address, type_text, media_text, 
                bucket_text, size_text, score_text, system_id
            ))

    def _populate_results_chunked(self, records, batch_size: int = 150, start_index: int = 0):
        """Inserta resultados en lotes para mantener la UI responsiva."""
        if self.stop_search:
            return
        end = min(start_index + batch_size, len(records))
        # Insertar lote
        for i in range(start_index, end):
            record_dict = records[i]
            # Fecha
            date_str = record_dict.get('date', '')
            date_text = date_str[:19] if date_str and len(date_str) > 19 else (date_str or 'N/A')
            name = record_dict.get('name', f'Documento {i+1}')
            name = name[:60] + "..." if len(name) > 60 else name
            ip_address = self._extract_ip_address(record_dict)
            type_text = self._get_type_description(record_dict.get('type', 0))
            media_text = self._get_media_description(record_dict.get('media', 0))
            bucket = record_dict.get('bucket', 'unknown')
            bucket_text = record_dict.get('bucketh', bucket)
            size_text = self._format_file_size(record_dict.get('size', 0))
            score = record_dict.get('xscore', 0)
            score_text = str(score) if score > 0 else 'N/A'
            system_id = record_dict.get('systemid', str(i))
            self.results_tree.insert("", "end", values=(
                date_text, name, ip_address, type_text, media_text, bucket_text, size_text, score_text, system_id
            ))
        # Actualizar barra de progreso basada en progreso de inserción
        if len(records) > 0:
            self.progress_bar.set(end / len(records))
        # Continuar si faltan registros
        if end < len(records) and not self.stop_search:
            self.after(25, lambda: self._populate_results_chunked(records, batch_size, end))
        else:
            self.status_label.configure(text=f"Encontrados {len(records)} resultados")
            # Reset progresivo para liberar visual luego
            self.after(1500, lambda: self.progress_bar.set(0))
    
    def _extract_ip_address(self, record_dict):
        """Extraer dirección IP del registro"""
        import re
        
        # Patrón para IPv4
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        # Patrón para IPv6 simplificado
        ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        
        # Buscar en diferentes campos
        search_fields = [
            record_dict.get('name', ''),
            record_dict.get('data', ''),
            str(record_dict)
        ]
        
        for field in search_fields:
            if field:
                # Buscar IPv4
                ipv4_match = re.search(ipv4_pattern, field)
                if ipv4_match:
                    return ipv4_match.group()
                
                # Buscar IPv6
                ipv6_match = re.search(ipv6_pattern, field)
                if ipv6_match:
                    return ipv6_match.group()
        
        return 'N/A'

    def _get_type_description(self, type_val):
        """
        Obtener descripción del tipo de contenido usando el mapeo oficial de IntelX API.
        Nunca devuelve números, siempre texto descriptivo.
        """
        try:
            # Convertir a entero si es necesario
            if isinstance(type_val, str):
                try:
                    type_val = int(type_val)
                except ValueError:
                    return "Tipo de Contenido Desconocido"
            
            # Mapeo según documentación oficial de IntelX SDK
            type_descriptions = {
                0: "Binario/Sin especificar",
                1: "Texto plano",
                2: "Imagen",
                3: "Video",
                4: "Audio",
                5: "Documento",
                6: "Ejecutable",
                7: "Contenedor",
                1001: "Usuario",
                1002: "Filtración",
                1004: "URL",
                1005: "Foro"
            }
            
            description = type_descriptions.get(type_val)
            
            if description:
                return description
            else:
                # Si no se encuentra, devolver descripción genérica (nunca un número)
                return f"Tipo de Contenido Desconocido ({type_val})"
                
        except Exception as e:
            logger.error(f"Error obteniendo descripción de tipo {type_val}: {e}")
            return "Tipo de Contenido Error"
    
    def _get_media_description(self, media_val):
        """
        Obtener descripción del tipo de media usando el mapeo oficial de IntelX API.
        Nunca devuelve números, siempre texto descriptivo.
        """
        try:
            # Convertir a entero si es necesario
            if isinstance(media_val, str):
                try:
                    media_val = int(media_val)
                except ValueError:
                    return "Tipo de Media Desconocido"
            
            # Usar el mapeo oficial de la API
            description = MEDIA_TYPE_MAP.get(media_val)
            
            if description:
                return description
            else:
                # Si no se encuentra, devolver descripción genérica (nunca un número)
                return f"Tipo de Media Desconocido ({media_val})"
                
        except Exception as e:
            logger.error(f"Error obteniendo descripción de media {media_val}: {e}")
            return "Tipo de Media Error"
    
    def _find_record_by_id(self, record_id):
        """Buscar registro por ID de manera robusta"""
        for i, record in enumerate(self.current_records):
            if isinstance(record, dict):
                # Buscar por systemid, storageid o índice
                if (record.get('systemid') == record_id or 
                    record.get('storageid') == record_id):
                    return record
            elif isinstance(record, str):
                # Para strings, usar el índice
                if f'record_{i}' == record_id:
                    return {
                        'name': f'Resultado {i+1}',
                        'type': 1,
                        'media': 1,
                        'bucket': 'unknown',
                        'size': len(record),
                        'date': '',
                        'xscore': 0,
                        'systemid': f'record_{i}',
                        'data': record
                    }
        return None

    def _format_file_size(self, size):
        """Formatear tamaño de archivo en formato legible"""
        if not size or size == 0:
            return "0 B"
        
        try:
            size = int(size)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}" if unit != 'B' else f"{size} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        except (ValueError, TypeError):
            return str(size)

    def _sort_by_column(self, col, reverse):
        """Sort records by a column."""
        if self.sort_column == col:
            reverse = not self.sort_reverse
        self.sort_column = col
        self.sort_reverse = reverse

        def sort_key(record):
            value = record.get(col)
            if col == 'date':
                if value:
                    try:
                        # Handle different date formats
                        if 'T' in value and 'Z' in value:
                            return datetime.fromisoformat(value.replace("Z", "+00:00"))
                        else:
                            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            return dt.replace(tzinfo=timezone.utc) # Make it timezone-aware
                    except (ValueError, TypeError):
                        return datetime.min.replace(tzinfo=timezone.utc)
                else:
                    return datetime.min.replace(tzinfo=timezone.utc)
            elif col == 'size':
                return int(record.get('size', 0))
            elif col == 'score':
                return int(record.get('xscore', 0))
            else:
                return str(record.get(col, '')).lower()

        # Sort the original data
        self.current_records.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Clear and repopulate treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self._populate_results(self.current_records)

        # Update heading command to toggle reverse
        self.results_tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))

    def _filter_by_year(self):
        year_str = self.year_entry.get()
        if not year_str:
            return

        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Error", "Año inválido.")
            return

        filtered_records = []
        for record in self.current_records:
            record_date_str = record.get('date')
            if record_date_str:
                try:
                    record_date = datetime.fromisoformat(record_date_str.replace("Z", "+00:00"))
                    if record_date.year == year:
                        filtered_records.append(record)
                except (ValueError, TypeError):
                    continue

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        original_records = self.current_records
        self.current_records = filtered_records
        self._populate_results(filtered_records)
        self.current_records = original_records

    def _clear_year_filter(self):
        self.year_entry.delete(0, 'end')
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self._populate_results(self.current_records)

    def _search_finished(self):
        """Finalizar búsqueda"""
        self.search_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.stop_search = False
        self.cancel_event = None
        # Resetear barra de progreso después de un momento
        self.after(2000, lambda: self.progress_bar.set(0))
        # Actualizar créditos después de la búsqueda
        self.after(1000, self.refresh_credits)

    def on_item_double_click(self, event):
        """Manejar doble clic en item"""
        self.preview_selected()

    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def manage_api_key(self):
        """Gestionar clave API"""
        dialog = ui_components.ApiKeyDialog(self, self.api_key)
        new_key = dialog.get_result()
        
        if new_key is not None:
            self.api_key = new_key
            try:
                # Guardar la clave y reinstanciar el cliente
                set_key(self.config_file, 'INTELX_API_KEY', self.api_key)
                if self.api_key:
                    self.api_client = IntelXAPI(self.api_key)
                    self.refresh_credits()
                else:
                    self.api_client = None
            except Exception as e:
                logger.exception("Error guardando API key")
                self.api_client = None

    def open_intelx_api_page(self):
        """Abrir página de API de IntelX"""
        webbrowser.open("https://intelx.io/account?tab=developer")

    def show_about(self):
        """Mostrar información sobre la aplicación"""
        ui_components.AboutDialog(self, self.app_version, self.current_language)

    def preview_selected(self):
        """Preview del item seleccionado"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        if values:
            record_id = values[-1]  # El systemid está en la última columna
            record = self._find_record_by_id(record_id)
            
            if record:
                self._show_preview_window(record)

    def _show_preview_window(self, record):
        """Mostrar ventana de preview"""
        preview_window = ui_components.PreviewWindow(self, record, self.api_client)
        self.preview_windows[record.get('systemid', '')] = preview_window

    def _on_preview_close(self, storage_id):
        """Callback cuando se cierra preview"""
        if storage_id in self.preview_windows:
            del self.preview_windows[storage_id]

    def select_all(self):
        """Seleccionar todos los items"""
        for item in self.results_tree.get_children():
            self.results_tree.selection_add(item)

    def deselect_all(self):
        """Deseleccionar todos los items"""
        self.results_tree.selection_remove(self.results_tree.selection())

    def copy_selected(self):
        """Copiar selección al clipboard"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        copied_data = []
        for item_id in selection:
            item = self.results_tree.item(item_id)
            copied_data.append('\t'.join(str(v) for v in item['values']))
        
        self.clipboard_clear()
        self.clipboard_append('\n'.join(copied_data))

    def export_selection(self):
        """Exportar selección"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Error", "No hay elementos seleccionados")
            return
        
        selected_records = []
        for item_id in selection:
            item = self.results_tree.item(item_id)
            values = item['values']
            if values:
                record_id = values[-1]  # El systemid está en la última columna
                record = self._find_record_by_id(record_id)
                if record:
                    selected_records.append(record)
        
        if selected_records:
            ui_components.show_export_selection_dialog(self, selected_records)

    def cancel_search(self):
        """Cancelar búsqueda en curso"""
        if self.search_thread and self.search_thread.is_alive():
            self.stop_search = True
            if self.cancel_event:
                self.cancel_event.set()
            self.status_label.configure(text="Cancelando búsqueda...")
            self.cancel_button.configure(state="disabled")

    def filter_results(self, event=None):
        """Filtrar resultados según el texto de búsqueda"""
        filter_text = self.filter_entry.get().strip().lower()
        
        if not filter_text:
            # Si no hay filtro, mostrar todos los registros
            self.current_records = list(self.all_records)
        else:
            # Filtrar registros que contengan el texto en cualquier campo
            filtered = []
            for record in self.all_records:
                if isinstance(record, dict):
                    # Buscar en todos los campos del registro
                    record_text = ' '.join(str(v) for v in record.values() if v).lower()
                    if filter_text in record_text:
                        filtered.append(record)
                elif isinstance(record, str):
                    if filter_text in record.lower():
                        filtered.append(record)
            self.current_records = filtered
        
        # Actualizar treeview con resultados filtrados
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self._populate_results(self.current_records)
        
        # Actualizar status
        self.status_label.configure(text=f"Mostrando {len(self.current_records)} de {len(self.all_records)} resultados")

    def refresh_credits(self):
        """Refrescar créditos disponibles"""
        if not self.api_client:
            self.credits_label.configure(text="Créditos: N/A")
            return
        
        try:
            success, credits_or_error = self.api_client.get_credits()
            if success:
                self.credits = credits_or_error
                lang = self.languages.get(self.current_language, self.languages["es"])
                self.credits_label.configure(text=f"{lang['Créditos']} {self.credits}")
            else:
                self.credits_label.configure(text="Créditos: Error")
        except Exception as e:
            logger.exception("Error refrescando créditos")
            self.credits_label.configure(text="Créditos: Error")

    # --- Async credits refresh para no bloquear la UI ---
    def refresh_credits_async(self):
        def _worker():
            if not self.api_client:
                return
            try:
                success, credits_or_error = self.api_client.get_credits()
                if success:
                    self.credits = credits_or_error
                    lang = self.languages.get(self.current_language, self.languages["es"])
                    self.after(0, lambda: self.credits_label.configure(text=f"{lang['Créditos']} {self.credits}"))
                else:
                    self.after(0, lambda: self.credits_label.configure(text="Créditos: Error"))
            except Exception:
                logger.exception("Error refrescando créditos (async)")
                self.after(0, lambda: self.credits_label.configure(text="Créditos: Error"))
        threading.Thread(target=_worker, daemon=True).start()

    def export_to_csv(self):
        """Exportar resultados a CSV"""
        if not self.current_records:
            messagebox.showwarning("Error", "No hay resultados para exportar")
            return
        
        try:
            search_term = self.term_entry.get().strip()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'csv')
            os.makedirs(reports_dir, exist_ok=True)
            sanitized_term = sanitize_filename(search_term or 'IntelX_Report')
            filename = f"{sanitized_term}_{timestamp}.csv"
            output_filepath = os.path.join(reports_dir, filename)
            
            exports_module.export_to_csv(self.current_records, output_filepath)
            messagebox.showinfo("Éxito", "Resultados exportados a CSV correctamente")
            
            # Preguntar si quiere abrir el archivo
            if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo CSV exportado?"):
                try:
                    os.startfile(output_filepath)
                except Exception as e:
                    logger.error(f"Error al abrir archivo CSV: {e}")
                    messagebox.showerror("Error", f"No se pudo abrir el archivo CSV: {str(e)}")
                    
        except Exception as e:
            logger.exception("Error exportando a CSV")
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")

    def export_to_json(self):
        """Exportar resultados a JSON"""
        if not self.current_records:
            messagebox.showwarning("Error", "No hay resultados para exportar")
            return
        
        try:
            search_term = self.term_entry.get().strip()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'json')
            os.makedirs(reports_dir, exist_ok=True)
            sanitized_term = sanitize_filename(search_term or 'IntelX_Report')
            filename = f"{sanitized_term}_{timestamp}.json"
            output_filepath = os.path.join(reports_dir, filename)
            
            exports_module.export_to_json(self.current_records, output_filepath)
            messagebox.showinfo("Éxito", "Resultados exportados a JSON correctamente")
            
            # Preguntar si quiere abrir el archivo
            if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo JSON exportado?"):
                try:
                    os.startfile(output_filepath)
                except Exception as e:
                    logger.error(f"Error al abrir archivo JSON: {e}")
                    messagebox.showerror("Error", f"No se pudo abrir el archivo JSON: {str(e)}")
                    
        except Exception as e:
            logger.exception("Error exportando a JSON")
            messagebox.showerror("Error", f"Error al exportar a JSON: {str(e)}")

    def export_to_html(self):
        """Exportar resultados a HTML"""
        if not self.current_records:
            messagebox.showwarning("Error", "No hay resultados para exportar")
            return
        
        try:
            search_term = self.term_entry.get().strip()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'html')
            os.makedirs(reports_dir, exist_ok=True)
            sanitized_term = sanitize_filename(search_term or 'IntelX_Report')
            filename = f"{sanitized_term}_{timestamp}.html"
            output_filepath = os.path.join(reports_dir, filename)
            
            exports_module.export_to_html(self.current_records, output_filepath, search_term=search_term, app_version=self.app_version)
            messagebox.showinfo("Éxito", "Resultados exportados a HTML correctamente")
            
            # Preguntar si quiere abrir el archivo
            if messagebox.askyesno("Abrir archivo", "¿Desea abrir el reporte HTML exportado en el navegador?"):
                try:
                    webbrowser.open(f'file://{output_filepath}')
                except Exception as e:
                    logger.error(f"Error al abrir archivo HTML: {e}")
                    messagebox.showerror("Error", f"No se pudo abrir el reporte HTML: {str(e)}")
                    
        except Exception as e:
            logger.exception("Error exportando a HTML")
            messagebox.showerror("Error", f"Error al exportar a HTML: {str(e)}")

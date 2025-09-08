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
from .api import check_intelx, retrieve_intelx_results, get_api_credits, MEDIA_TYPE_MAP, INTELX_API_URL_AUTH_INFO, INTELX_API_URL_TERMINATE, INTELX_API_URL_FILE_PREVIEW, USER_AGENT, REQUEST_TIMEOUT_AUTH, REQUEST_TIMEOUT_TERMINATE, REQUEST_TIMEOUT_PREVIEW, INTELX_RATE_LIMIT_DELAY, DEFAULT_DATE_MIN, DEFAULT_DATE_MAX
from .analysis import analyze_results_for_report, extract_iocs, clean_data_for_mandiant_report, prepare_mandiant_chart_data
from .reporting import generate_modern_html_content, generate_executive_summary_html, generate_iocs_html, generate_data_table_html
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
        file_menu.add_command(label="Exportar a CSV...", command=self.export_to_csv_safe)
        file_menu.add_command(label="Exportar a JSON...", command=self.export_to_json_safe)
        file_menu.add_command(label="Exportar a HTML...", command=self.export_to_html_safe)
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
        """Cargar configuración de API"""
        try:
            load_dotenv(self.config_file)
            self.api_key = os.getenv('INTELX_API_KEY', '')
            if self.api_key:
                self.refresh_credits()
        except:
            self.api_key = ''
    
    def search_intelx(self):
        """Buscar en IntelX"""
        term = self.term_entry.get().strip()
        if not term:
            messagebox.showwarning("Error", "Ingrese un término de búsqueda")
            return
        
        if not self.api_key:
            messagebox.showwarning("Error", "Configure su clave API primero")
            self.manage_api_key()
            return
        
        # Actualizar créditos antes de iniciar la búsqueda
        self.refresh_credits()
        
        # Limpiar resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_records = []
        self.stop_search = False
        
        # Actualizar UI
        self.search_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_label.configure(text="Iniciando búsqueda...")
        self.progress_bar.set(0.1)
        
        # Iniciar búsqueda en hilo separado
        self.search_thread = threading.Thread(target=self._search_worker, args=(term,))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def _search_worker(self, term):
        """Worker para búsqueda en hilo separado"""
        try:
            self.after(0, lambda: self.progress_bar.set(0.3))
            self.after(0, lambda: self.status_label.configure(text="Conectando con IntelX..."))
            
            success, data_or_error, search_id = check_intelx(term, self.api_key)
            
            self.after(0, lambda: self.progress_bar.set(0.7))
            
            if success:
                self.after(0, lambda: self.status_label.configure(text="Procesando resultados..."))
                
                if isinstance(data_or_error, dict) and 'records' in data_or_error:
                    self.current_records = data_or_error['records']
                elif isinstance(data_or_error, list):
                    self.current_records = data_or_error
                elif isinstance(data_or_error, dict):
                    self.current_records = [data_or_error]
                else:
                    self.current_records = []
                
                self.all_records = self.current_records
                
                self.after(0, lambda: self.progress_bar.set(1.0))
                
                if self.current_records and not self.stop_search:
                    self.after(0, self._populate_results, self.current_records)
                    self.after(0, lambda: self.status_label.configure(text=f"Encontrados {len(self.current_records)} resultados"))
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
    
    def _populate_results(self, records_to_show):
        """Poblar treeview con resultados"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for i, record in enumerate(records_to_show):
            if self.stop_search:
                break
                
            # Manejar diferentes tipos de datos de entrada
            if isinstance(record, str):
                # Si es string, crear un registro básico
                record_dict = {
                    'name': f'Resultado {i+1}',
                    'type': 1,  # Texto
                    'media': 1,  # Paste
                    'bucket': 'unknown',
                    'size': len(record),
                    'date': '',
                    'xscore': 0,
                    'systemid': f'record_{i}',
                    'data': record
                }
            elif isinstance(record, dict):
                record_dict = record
            else:
                # Fallback para otros tipos
                record_dict = {
                    'name': f'Resultado {i+1}',
                    'type': 0,
                    'media': 0,
                    'bucket': 'unknown',
                    'size': 0,
                    'date': '',
                    'xscore': 0,
                    'systemid': f'record_{i}',
                    'data': str(record)
                }
                
            # Fecha formateada (primera prioridad)
            date_str = record_dict.get('date', '')
            if date_str:
                try:
                    # Formatear fecha si está disponible
                    date_text = date_str[:19] if len(date_str) > 19 else date_str
                except:
                    date_text = date_str
            else:
                date_text = 'N/A'
                
            # Formatear datos basándose en la estructura del diccionario
            name = record_dict.get('name', f'Documento {i+1}')
            name = name[:60] + "..." if len(name) > 60 else name
            
            # Extraer IP del nombre o datos
            ip_address = self._extract_ip_address(record_dict)
            
            # Tipo de contenido (type)
            type_val = record_dict.get('type', 0)
            type_text = self._get_type_description(type_val)
            
            # Media type (más descriptivo)
            media_val = record_dict.get('media', 0)
            media_text = self._get_media_description(media_val)
            
            # Bucket con nombre legible
            bucket = record_dict.get('bucket', 'unknown')
            bucket_text = record_dict.get('bucketh', bucket)  # bucketh es el nombre legible
            
            # Tamaño formateado
            size = record_dict.get('size', 0)
            size_text = self._format_file_size(size)
            
            # Puntuación de relevancia (xscore)
            score = record_dict.get('xscore', 0)
            score_text = str(score) if score > 0 else 'N/A'
            
            # System ID
            system_id = record_dict.get('systemid', record_dict.get('storageid', str(i)))
            
            # Nuevo orden: fecha, nombre, IP, tipo, media, bucket, tamaño, score, systemid
            self.results_tree.insert("", "end", values=(
                date_text, name, ip_address, type_text, media_text, 
                bucket_text, size_text, score_text, system_id
            ))
    
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
        self._populate_results(self.current_records)
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
        # Resetear barra de progreso después de un momento
        self.after(2000, lambda: self.progress_bar.set(0))
        # Actualizar créditos después de la búsqueda
        self.after(1000, self.refresh_credits)
    
    def cancel_search(self):
        """Cancelar búsqueda"""
        self.stop_search = True
        # Señalar al evento de cancelación si existe
        if hasattr(self, 'cancel_event') and self.cancel_event:
            self.cancel_event.set()
        self.status_label.configure(text="Búsqueda cancelada")
        self._search_finished()
    
    def filter_results(self, event=None):
        """Filtrar resultados usando la nueva estructura de columnas"""
        filter_text = self.filter_entry.get().lower()
        
        # Limpiar treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Volver a poblar con filtro
        for i, record in enumerate(self.current_records):
            # Manejar diferentes tipos de datos de entrada
            if isinstance(record, str):
                record_dict = {
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
            elif isinstance(record, dict):
                record_dict = record
            else:
                record_dict = {
                    'name': f'Resultado {i+1}',
                    'type': 0,
                    'media': 0,
                    'bucket': 'unknown',
                    'size': 0,
                    'date': '',
                    'xscore': 0,
                    'systemid': f'record_{i}',
                    'data': str(record)
                }
            
            # Buscar en todos los campos del registro
            record_data = str(record_dict).lower()
            name = record_dict.get('name', f'Documento {i+1}').lower()
            bucket = record_dict.get('bucket', '').lower()
            
            if (filter_text in record_data or 
                filter_text in name or 
                filter_text in bucket):
                
                # Fecha formateada (primera prioridad)
                date_str = record_dict.get('date', '')
                if date_str:
                    try:
                        date_text = date_str[:19] if len(date_str) > 19 else date_str
                    except:
                        date_text = date_str
                else:
                    date_text = 'N/A'
                
                # Recrear la entrada usando los nuevos campos
                name_display = record_dict.get('name', f'Documento {i+1}')
                name_display = name_display[:60] + "..." if len(name_display) > 60 else name_display
                
                # Extraer IP
                ip_address = self._extract_ip_address(record_dict)
                
                type_val = record_dict.get('type', 0)
                type_text = self._get_type_description(type_val)
                
                media_val = record_dict.get('media', 0)
                media_text = self._get_media_description(media_val)
                
                bucket = record_dict.get('bucket', 'unknown')
                bucket_text = record_dict.get('bucketh', bucket)
                
                size = record_dict.get('size', 0)
                size_text = self._format_file_size(size)
                
                score = record_dict.get('xscore', 0)
                score_text = str(score) if score > 0 else 'N/A'
                
                system_id = record_dict.get('systemid', record_dict.get('storageid', str(i)))
                
                # Nuevo orden: fecha, nombre, IP, tipo, media, bucket, tamaño, score, systemid
                self.results_tree.insert("", "end", values=(
                    date_text, name_display, ip_address, type_text, media_text, 
                    bucket_text, size_text, score_text, system_id
                ))
    
    def refresh_credits(self):
        """Actualizar créditos en un hilo separado para no bloquear la UI"""
        if not self.api_key:
            return

        self.status_label.configure(text="Actualizando créditos...")
        
        thread = threading.Thread(target=self._refresh_credits_worker)
        thread.daemon = True
        thread.start()

    def _refresh_credits_worker(self):
        """Worker que se ejecuta en un hilo para obtener los créditos"""
        try:
            logger.info("Actualizando créditos desde la API...")
            success, credits_or_error = get_api_credits(self.api_key)
            
            if success:
                old_credits = getattr(self, 'credits', 0)
                self.credits = credits_or_error
                
                def update_ui():
                    lang = self.languages.get(self.current_language, self.languages["es"])
                    self.credits_label.configure(text=f"{lang['Créditos']} {self.credits}")
                    self.status_label.configure(text="Créditos actualizados.")
                
                self.after(0, update_ui)
                
                if old_credits != self.credits:
                    logger.info(f"Créditos actualizados: {old_credits} → {self.credits}")
                else:
                    logger.info(f"Créditos confirmados: {self.credits}")
            else:
                logger.error(f"Error obteniendo créditos: {credits_or_error}")
                def update_ui_error():
                    lang = self.languages.get(self.current_language, self.languages["es"])
                    self.credits_label.configure(text=f"{lang['Créditos']} Error")
                    self.status_label.configure(text="Error al actualizar créditos.")
                self.after(0, update_ui_error)
                
        except Exception as e:
            logger.exception("Error obteniendo créditos")
            def update_ui_exception():
                lang = self.languages.get(self.current_language, self.languages["es"])
                self.credits_label.configure(text=f"{lang['Créditos']} Error")
                self.status_label.configure(text="Error al actualizar créditos.")
            self.after(0, update_ui_exception)
    
    def _export_worker(self, export_function, records_to_export, format_name, **kwargs):
        """Worker genérico para exportaciones en segundo plano."""
        try:
            def update_status_start():
                self.status_label.configure(text=f"Exportando a {format_name}...")
                self.progress_bar.start()

            self.after(0, update_status_start)

            filepath = export_function(records_to_export, **kwargs)

            def update_status_success():
                self.status_label.configure(text=f"Exportación a {format_name} completada.")
                self.progress_bar.stop()
                self.progress_bar.set(0)
                ui_components.show_export_success_dialog(self, filepath)

            self.after(0, update_status_success)

        except Exception as e:
            logger.exception(f"Error exportando a {format_name}")
            def update_status_error():
                self.status_label.configure(text=f"Error en exportación a {format_name}.")
                self.progress_bar.stop()
                self.progress_bar.set(0)
                ui_components.show_custom_messagebox(self, 'Error', f"Error exportando a {format_name}: {e}", 'error')
            
            self.after(0, update_status_error)

    def _export_html_worker(self, search_term, records_to_export):
        """Worker para generar el dashboard HTML en segundo plano, usando los registros filtrados."""
        def update_status_start():
            self.status_label.configure(text="Generando dashboard HTML...")
            self.progress_bar.start()
        self.after(0, update_status_start)

        from .exports import build_dashboard_data, export_dashboard_html
        import re
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports", "html")
        os.makedirs(exports_dir, exist_ok=True)
        safe_search = re.sub(r'[^a-zA-Z0-9_\-]', '_', search_term)
        filename = f"IntelX_Dashboard_{safe_search}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        if not records_to_export or len(records_to_export) == 0:
            msg_es = "No hay resultados para exportar. Seleccione los datos que desea exportar."
            msg_en = "No results to export. Please select the data you want to export."
            msg = msg_es if self.current_language == "es" else msg_en
            self.after(0, lambda: messagebox.showwarning("Exportar a HTML", msg))
            self.after(0, self.progress_bar.stop)
            self.after(0, lambda: self.status_label.configure(text=msg))
            return
        dashboard_data = build_dashboard_data(records_to_export, lang=self.current_language)
        filepath = export_dashboard_html(dashboard_data, filename=filename, exports_dir=exports_dir, search_term=search_term, timestamp=timestamp)

        def update_status_success():
            self.status_label.configure(text="Dashboard HTML generado.")
            self.progress_bar.stop()
            self.progress_bar.set(0)
            if messagebox.askyesno("Dashboard HTML", "¿Desea abrir el dashboard en su navegador?"):
                open_in_browser(filepath)
        self.after(0, update_status_success)

    def manage_api_key(self):
        """Gestionar clave API"""
        dialog = ui_components.ApiKeyDialog(self, self.api_key)
        new_key = dialog.get_result()
        
        if new_key is not None:
            self.api_key = new_key
            try:
                set_key(self.config_file, 'INTELX_API_KEY', self.api_key)
                if self.api_key:
                    self.refresh_credits()
            except Exception as e:
                logger.exception("Error guardando API key")
    
    def open_intelx_api_page(self):
        """Abrir página de API de IntelX"""
        webbrowser.open("https://intelx.io/account?tab=developer")
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        ui_components.AboutDialog(self, self.app_version, self.current_language)
    
    # Event handlers
    def on_item_double_click(self, event):
        """Manejar doble clic en item"""
        self.preview_selected()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def preview_selected(self):
        """Preview del item seleccionado"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        # Obtener datos del item seleccionado
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        if values:
            record_id = values[-1]  # El systemid está en la última columna
            # Buscar record completo usando la función auxiliar
            record = self._find_record_by_id(record_id)
            
            if record:
                # Crear ventana de preview (implementar según necesidades)
                self._show_preview_window(record)
    
    def _show_preview_window(self, record):
        """Mostrar ventana de preview"""
        preview_window = ui_components.PreviewWindow(self, record)
        self.preview_windows[record.get('storageid', '')] = preview_window
    
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
        
        # Obtener records seleccionados
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
            # Usar dialogo de exportación
            ui_components.show_export_selection_dialog(self, selected_records)

    # --- Export methods (using modular architecture) ---
    def export_to_csv_safe(self):
        """Exportar a CSV usando un hilo para no bloquear la UI."""
        if not self.current_records:
            ui_components.show_custom_messagebox(self, "Sin Datos", "No hay resultados para exportar.", "warning")
            return
        
        selected_ids = list(self.results_tree.selection()) if hasattr(self, 'results_tree') else []
        records_to_export = ui_components.get_records_to_export_dialog(self, self.current_records, selected_ids)
        if not records_to_export:
            return
            
        search_term = self.term_entry.get().strip() or 'IntelX_Export'
        filename = f"IntelX_Report_{search_term}.csv"
        
        thread = threading.Thread(target=self._export_worker, args=(
            exports_module.export_to_csv,
            records_to_export,
            "CSV"
        ), kwargs={'filename': filename})
        thread.daemon = True
        thread.start()

    def export_to_json_safe(self):
        """Exportar a JSON usando un hilo para no bloquear la UI."""
        if not self.current_records:
            ui_components.show_custom_messagebox(self, "Sin Datos", "No hay resultados para exportar.", "warning")
            return
        
        selected_ids = list(self.results_tree.selection()) if hasattr(self, 'results_tree') else []
        records_to_export = ui_components.get_records_to_export_dialog(self, self.current_records, selected_ids)
        if not records_to_export:
            return
            
        search_term = self.term_entry.get().strip() or 'IntelX_Export'
        filename = f"IntelX_Report_{search_term}.json"

        thread = threading.Thread(target=self._export_worker, args=(
            exports_module.export_to_json,
            records_to_export,
            "JSON"
        ), kwargs={'filename': filename})
        thread.daemon = True
        thread.start()

    def export_to_html_safe(self):
        """Generar reporte HTML usando un hilo para no bloquear la UI y garantizando selección correcta."""
        selected_ids = list(self.results_tree.selection()) if hasattr(self, 'results_tree') else []
        records_to_export = ui_components.get_records_to_export_dialog(self, self.current_records, selected_ids)
        if not records_to_export:
            # El usuario canceló o no hay datos
            ui_components.show_custom_messagebox(self, "Sin Datos", "No hay resultados seleccionados para exportar.", "warning")
            return
        search_term = self.term_entry.get().strip() or "búsqueda_sin_nombre"
        thread = threading.Thread(target=self._export_html_worker, args=(search_term, records_to_export))
        thread.daemon = True
        thread.start()


# Provide compatibility for scripts that import the class directly
if __name__ == '__main__':
    app = IntelXCheckerApp()
    app.mainloop()

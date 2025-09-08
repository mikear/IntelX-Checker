"""
Módulo: gui.py
Interfaz gráfica principal usando CustomTkinter y Tkinter
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

from intelx.api import check_intelx, retrieve_intelx_results, MEDIA_TYPE_MAP, INTELX_API_URL_AUTH_INFO, INTELX_API_URL_TERMINATE, INTELX_API_URL_FILE_PREVIEW, USER_AGENT, REQUEST_TIMEOUT_AUTH, REQUEST_TIMEOUT_TERMINATE, REQUEST_TIMEOUT_PREVIEW, INTELX_RATE_LIMIT_DELAY, DEFAULT_DATE_MIN, DEFAULT_DATE_MAX

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(threadName)-15s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

class IntelXCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.preview_windows = {}
        self.title("IntelX Checker")
        self.geometry("950x600")
        self.app_version = "1.3.0"
        self._filter_job = None
        self.fonts = {
            "main": ("Segoe UI", 14),
            "main_bold": ("Segoe UI", 14, "bold"),
            "tree_header": ("Segoe UI", 13, "bold"),
            "tree_content": ("Segoe UI", 13),
            "secondary": ("Segoe UI", 12),
            "tertiary": ("Segoe UI", 11),
            "dialog_header": ("Segoe UI", 13, "bold"),
            "dialog_body": ("Segoe UI", 12),
            "menu": ("Segoe UI", 13)
        }
        load_dotenv(find_dotenv(filename='.env', raise_error_if_not_found=False), override=True)
        self.intelx_api_key = os.getenv('INTELX_API_KEY')
        self._has_api_key = bool(self.intelx_api_key)
        self.available_buckets_for_ui = [
            ("Pastes", "pastes", "Repositorios de texto pegado, como Pastebin y similares."),
            ("Leaks (Públicas)", "leaks.public.general", "Filtraciones públicas generales de datos."),
            ("Darknet (.onion)", "darknet.tor", "Sitios de la darknet accesibles por Tor (.onion)."),
            ("Darknet (I2P)", "darknet.i2p", "Sitios de la darknet accesibles por I2P."),
            ("Dumpsters", "dumpster", "Repositorios de datos desechados o expuestos accidentalmente."),
            ("Whois", "whois", "Información de registros de dominios (Whois)."),
            ("Usenet", "usenet", "Foros y grupos de noticias Usenet."),
            ("Bot Logs", "leaks.logs", "Registros de bots y malware que capturan credenciales."),
        ]
        self.selected_buckets_config = [bucket_id for _, bucket_id, _ in self.available_buckets_for_ui]
        self.current_records = []
        self._is_searching = False
        self.cancel_event = None
        self._setup_ui()
        self._setup_menu()
        self._fetch_and_display_credits_safe()

        self._set_app_icon()

    def _set_app_icon(self):
        import os
        from PIL import Image, ImageTk
        icon_png = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.png")
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        # Convertir PNG a ICO si no existe
        if os.path.exists(icon_png):
            try:
                self.icon_img = Image.open(icon_png)
                self.icon_img = self.icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icon_tk = ImageTk.PhotoImage(self.icon_img)
                if not os.path.exists(icon_ico):
                    self.icon_img.save(icon_ico, format="ICO", sizes=[(32,32)])
            except Exception as e:
                print(f"No se pudo procesar el icono PNG: {e}")
        else:
            self.icon_img = None
            self.icon_tk = None
        # Usar icon.ico para la ventana principal
        if os.path.exists(icon_ico):
            try:
                self.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo cargar el icono ICO: {e}")

    def _show_markdown_window(self, title, md_path):
        try:
            import markdown2
            from tkhtmlview import HTMLScrolledText
        except ImportError:
            import tkinter.messagebox as mb
            mb.showerror("Dependencia Faltante", "Instala los paquetes 'markdown2' y 'tkhtmlview' para ver el formato mejorado.\nEjecuta: pip install markdown2 tkhtmlview")
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("700x600")
        dialog.transient(self)
        dialog.grab_set()
        # Asignar icono a la ventana de diálogo
        import os
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        frame = ctk.CTkFrame(dialog)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html = markdown2.markdown(md_content)
            html_view = HTMLScrolledText(frame, html=html)
            html_view.pack(expand=True, fill="both")
        except Exception as e:
            error_label = ctk.CTkLabel(frame, text=f"No se pudo cargar el archivo: {e}", font=("Segoe UI", 12))
            error_label.pack(expand=True, fill="both")
        ok_btn = ctk.CTkButton(dialog, text="Cerrar", command=dialog.destroy)
        ok_btn.pack(pady=10)

    def _setup_menu(self):
        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        file_menu = Menu(self.menubar, tearoff=0, font=self.fonts["menu"])
        self.menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a CSV...", command=lambda: self.export_to_csv_safe(), font=self.fonts["menu"])
        file_menu.add_command(label="Exportar a JSON...", command=lambda: self.export_to_json_safe(), font=self.fonts["menu"])
        file_menu.add_command(label="Salir", command=lambda: self.quit(), font=self.fonts["menu"])

        config_menu = Menu(self.menubar, tearoff=0, font=self.fonts["menu"])
        self.menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Gestionar Clave API...", command=lambda: self.manage_api_key(), font=self.fonts["menu"])
        config_menu.add_command(label="Fuentes de Búsqueda (Buckets)...", command=lambda: self._configure_buckets_dialog(), font=self.fonts["menu"])

        help_menu = Menu(self.menubar, tearoff=0, font=self.fonts["menu"])
        self.menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Refrescar Créditos", command=lambda: self._fetch_and_display_credits_safe(), font=self.fonts["menu"])
        help_menu.add_command(label="Obtener Clave API de IntelX", command=lambda: self.get_api_key_link(), font=self.fonts["menu"])
        help_menu.add_command(label="Visitar Intelligence X", command=lambda: self.after(0, lambda: webbrowser.open("https://intelx.io")), font=self.fonts["menu"])
        help_menu.add_command(label="Manual de Usuario", command=lambda: self._show_markdown_window("Manual de Usuario", os.path.join(os.path.dirname(__file__), "..", "docs", "MANUAL_DE_USUARIO.md")), font=self.fonts["menu"])
        help_menu.add_command(label="Glosario de Resultados", command=lambda: self._show_markdown_window("Glosario de Resultados", os.path.join(os.path.dirname(__file__), "..", "docs", "GLOSARIO.md")), font=self.fonts["menu"])
        help_menu.add_command(label="Acerca de...", command=lambda: self._show_about_dialog(), font=self.fonts["menu"])

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.term_label = ctk.CTkLabel(self.input_frame, text="Correo o Dominio:", font=self.fonts["main"])
        self.term_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.term_entry = ctk.CTkEntry(self.input_frame, placeholder_text="ejemplo@dominio.com", font=self.fonts["main"])
        self.term_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.term_entry.bind("<Return>", self.start_check_thread_safe)

        self.button_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=10, pady=(5, 10))

        self.check_button = ctk.CTkButton(self.button_frame, text="Buscar", command=self.start_check_thread_safe, font=self.fonts["main"])
        self.check_button.pack(side="left", padx=(0, 10))

        self.cancel_button = ctk.CTkButton(
            self.button_frame, text="Cancelar", command=self.request_search_termination_safe,
            state="disabled", fg_color="firebrick", hover_color="darkred", width=80, font=self.fonts["main"]
        )
        self.cancel_button.pack(side="left")

        self.status_progress_frame = ctk.CTkFrame(self)
        self.status_progress_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.status_progress_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_progress_frame, text="Listo.", anchor="w", font=self.fonts["secondary"])
        self.status_label.grid(row=0, column=0, padx=10, pady=(5, 2), sticky="ew")

        self.progressbar = ctk.CTkProgressBar(self.status_progress_frame, height=10)
        self.progressbar.grid(row=1, column=0, padx=10, pady=(2, 5), sticky="ew")
        self.progressbar.set(0)

        self.results_controls_frame = ctk.CTkFrame(self)
        self.results_controls_frame.grid(row=2, column=0, padx=20, pady=(5,0), sticky="ew")
        self.results_controls_frame.grid_columnconfigure(1, weight=1)

        self.filter_entry = ctk.CTkEntry(self.results_controls_frame, placeholder_text="Filtrar resultados...", font=self.fonts["secondary"])
        self.filter_entry.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.filter_entry.bind("<KeyRelease>", self._on_filter_changed)

        self.credits_info_label = ctk.CTkLabel(
            self.results_controls_frame, text="Créditos:", anchor="e",
            text_color="gray", font=self.fonts["tertiary"]
        )
        self.credits_info_label.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")

        self._setup_treeview()

        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=4, column=0, padx=20, pady=(5, 5), sticky="ew")
        footer_font = self.fonts["tertiary"]
        link_color = "#60A5FA"
        footer_left = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_left.pack(side="left")
        version_label = ctk.CTkLabel(footer_left, text=f"v{self.app_version}", font=footer_font, text_color="gray")
        version_label.pack(side="left", padx=(0, 5))
        separator_label1 = ctk.CTkLabel(footer_left, text="|", font=footer_font, text_color="gray")
        separator_label1.pack(side="left", padx=5)
        dev_by_label = ctk.CTkLabel(footer_left, text="Desarrollado por", font=footer_font, text_color="gray")
        dev_by_label.pack(side="left", padx=(5, 0))
        dev_link = ctk.CTkLabel(footer_left, text="Diego A. Rábalo", text_color=link_color, cursor="hand2", font=footer_font)
        dev_link.pack(side="left", padx=5)
        dev_link.bind("<Button-1>", lambda event: self.after(0, lambda: webbrowser.open("https://github.com/mikear")))
        footer_right = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_right.pack(side="right")
        powered_by_label = ctk.CTkLabel(footer_right, text="Resultados por", font=footer_font, text_color="gray")
        powered_by_label.pack(side="left", padx=(5, 0))
        intelx_link = ctk.CTkLabel(footer_right, text="Intelligence X", text_color=link_color, cursor="hand2", font=footer_font)
        intelx_link.pack(side="left", padx=5)
        intelx_link.bind("<Button-1>", lambda event: self.after(0, lambda: webbrowser.open("https://intelx.io")))

    def _setup_treeview(self):
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="nsew")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        self.current_theme = ctk.get_appearance_mode().lower()
        fg_color = "#F9F9FA" if self.current_theme == "light" else "#2B2B2B"
        text_color = "#242424" if self.current_theme == "light" else "#DCE4EE"
        header_bg = "#EAEAEA" if self.current_theme == "light" else "#333333"
        header_fg = text_color
        selected_bg = "#3470B6"

        style.theme_use("default")
        style.configure("Treeview",
                        background=fg_color,
                        foreground=text_color,
                        fieldbackground=fg_color,
                        borderwidth=0,
                        font=self.fonts["tree_content"],
                        rowheight=int(self.fonts["tree_content"][1] * 2.5))
        style.map('Treeview', background=[('selected', selected_bg)])

        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        font=self.fonts["tree_header"],
                        relief="flat", anchor="center")
        style.map("Treeview.Heading", background=[('active', '#3C89E8')])

        columns = ("date", "name", "bucket", "systemid", "media")
        self.results_tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings"
        )

        vsb = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.results_tree.yview)
        hsb = ctk.CTkScrollbar(self.tree_frame, orientation="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.results_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        headings = {
            "date": "Fecha Aproximada",
            "name": "Titulo",
            "bucket": "Fuente (Bucket)",
            "systemid": "System ID",
            "media": "Tipo de Medio"
        }
        for col, text in headings.items():
            self.results_tree.heading(col, text=text, anchor='center', command=lambda _col=col: self._treeview_sort_column(_col, False))

        self.results_tree.column("date", width=150, stretch=False, anchor="w")
        self.results_tree.column("name", width=300, stretch=True, anchor="w")
        self.results_tree.column("bucket", width=120, stretch=False, anchor="w")
        self.results_tree.column("systemid", width=250, stretch=False, anchor="w")
        self.results_tree.column("media", width=120, stretch=False, anchor="w")

    def _on_filter_changed(self, event=None):
        if self._filter_job:
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(300, self._filter_results)

    def _filter_results(self):
        filter_text = self.filter_entry.get().lower()
        
        if not hasattr(self, "current_records"):
            return

        if not filter_text:
            self._populate_results_display(self.current_records)
            return

        filtered_records = []
        for record in self.current_records:
            if filter_text in (record.get('name', '') or '').lower():
                filtered_records.append(record)
        
        self._populate_results_display(filtered_records)

    def _treeview_sort_column(self, col, reverse):
        try:
            l = [(self.results_tree.set(k, col), k) for k in self.results_tree.get_children('')]
            l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
        except Exception:
            l = [(self.results_tree.set(k, col), k) for k in self.results_tree.get_children('')]
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.results_tree.move(k, '', index)

        self.results_tree.heading(col, command=lambda: self._treeview_sort_column(col, not reverse))

    def _populate_results_display(self, records_to_display):
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        
        if not records_to_display:
            return

        for record in records_to_display:
            date = record.get('date', 'N/A')
            name = record.get('name', 'Sin Título') or "Sin Título"
            bucket = record.get('bucket', 'N/A')
            systemid = record.get('systemid', 'N/A')
            media_type = MEDIA_TYPE_MAP.get(record.get('media'), 'Desconocido')
            
            self.results_tree.insert("", "end", values=(date, name, bucket, systemid, media_type), iid=record.get('systemid'))

    def start_check_thread_safe(self, event=None):
        if hasattr(self, '_is_searching') and self._is_searching:
            self._show_custom_messagebox("Búsqueda en Progreso", "Ya hay una búsqueda en curso.", mtype="warning")
            return
        if not hasattr(self, 'intelx_api_key') or not self.intelx_api_key:
            self._show_custom_messagebox("Falta Clave API", "La clave API de Intelligence X no está configurada.", mtype="error")
            return
        term_to_search = self.term_entry.get().strip()
        if not term_to_search:
            self._show_custom_messagebox("Término Vacío", "Por favor, introduce un correo electrónico o dominio para buscar.", mtype="error")
            return
        selected_buckets = self.selected_buckets_config.copy()
        if not selected_buckets:
            self._show_custom_messagebox("Sin Selección", "Debes seleccionar al menos una fuente (bucket) para buscar desde el menú Configuración.", mtype="warning")
            return
        self._is_searching = True
        self.cancel_event = threading.Event()
        threading.Thread(target=self._search_task, args=(term_to_search, selected_buckets), daemon=True).start()

    def request_search_termination_safe(self):
        if hasattr(self, 'cancel_event') and self.cancel_event:
            self.cancel_event.set()
            self._update_status_label("Solicitando cancelación de búsqueda...")
            self.after(100, lambda: self._update_gui_state())
        else:
            self._show_custom_messagebox("Información", "No hay búsqueda activa para cancelar.", mtype="info")

    def _search_task(self, term_to_search: str, selected_buckets: List[str]):
        self.after(0, lambda: self._update_gui_state())
        self.after(0, lambda: self._update_status_label(f"Buscando '{term_to_search}'..."))
        self.after(0, lambda: self.progressbar.set(0.1))
        api_key = self.intelx_api_key if self.intelx_api_key else ""
        success, data_or_error, search_id = check_intelx(
            search_term=term_to_search,
            api_key=api_key,
            selected_buckets=selected_buckets,
            cancel_event=self.cancel_event
        )
        self.after(0, lambda: self.progressbar.set(1.0))
        self._is_searching = False
        self.after(0, lambda: self._update_gui_state())
        if success:
            records = data_or_error["records"] if isinstance(data_or_error, dict) and "records" in data_or_error else []
            self.current_records = records # Store all fetched records
            self.after(0, lambda: self._populate_results_display(records))
            self.after(0, lambda: self._update_status_label(f"Búsqueda completada. Encontrados {len(records)} resultados."))
        else:
            error_msg = str(data_or_error) if not isinstance(data_or_error, dict) else json.dumps(data_or_error, ensure_ascii=False)
            self.after(0, lambda: messagebox.showerror("Error de Búsqueda", error_msg))
            self.after(0, lambda: self._update_status_label("Búsqueda fallida o cancelada."))
        if search_id:
            threading.Thread(target=self._terminate_intelx_search, args=(search_id,), daemon=True).start()

    def _terminate_intelx_search(self, search_id: str):
        try:
            headers = {'x-key': self.intelx_api_key, 'User-Agent': f"{USER_AGENT}/TerminateSearch"}
            response = requests.post(INTELX_API_URL_TERMINATE, headers=headers, json={'id': search_id}, timeout=REQUEST_TIMEOUT_TERMINATE)
            response.raise_for_status()
            logger.info(f"Búsqueda IntelX {search_id} terminada exitosamente.")
        except Exception as e:
            logger.error(f"Error al intentar terminar la búsqueda IntelX {search_id}: {e}")

    def _get_records_to_export(self):
        selected_ids = self.results_tree.selection()
        if not selected_ids:
            return self.current_records

        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Exportación")
        dialog.geometry("350x150")
        dialog.transient(self)
        dialog.grab_set()
        # Asignar icono
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        result = ["all"]
        def set_choice(choice):
            result[0] = choice
            dialog.destroy()
        label = ctk.CTkLabel(dialog, text="Hay filas seleccionadas. ¿Qué deseas exportar?", font=self.fonts["main"])
        label.pack(pady=20)
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        btn_selected = ctk.CTkButton(button_frame, text=f"Solo Selección ({len(selected_ids)})", command=lambda: set_choice("selected"), font=self.fonts["main"])
        btn_selected.pack(side="left", padx=10)
        btn_all = ctk.CTkButton(button_frame, text=f"Todo ({len(self.current_records)})", command=lambda: set_choice("all"), font=self.fonts["main"])
        btn_all.pack(side="left", padx=10)
        self.wait_window(dialog)
        if result[0] == "selected":
            return [rec for rec in self.current_records if rec.get('systemid') in selected_ids]
        else:
            return self.current_records

    def export_to_csv_safe(self):
        records_to_export = self._get_records_to_export()
        if not records_to_export:
            self._show_custom_messagebox("Sin Datos", "No hay resultados para exportar.", mtype="warning")
            return
        
        term = self.term_entry.get().strip().replace('@', '_at_').replace('.', '_dot_')
        timestamp = datetime.now().strftime("%Y%m%d")
        default_filename = f"intelx_{term}_{timestamp}.csv"
        
        exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "csv")
        os.makedirs(exports_dir, exist_ok=True)

        filepath = filedialog.asksaveasfilename(
            initialdir=exports_dir,
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ["Fecha Aproximada", "Titulo", "Fuente (Bucket)", "System ID", "Tipo de Medio"]
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                for record in records_to_export:
                    row = [
                        record.get('date', 'N/A'),
                        record.get('name', 'Sin Título') or "Sin Título",
                        record.get('bucket', 'N/A'),
                        record.get('systemid', 'N/A'),
                        MEDIA_TYPE_MAP.get(record.get('media'), 'Desconocido')
                    ]
                    writer.writerow(row)
            self._show_export_success_dialog(filepath)
        except IOError as e:
            self._show_custom_messagebox("Error de Exportación", f"No se pudo escribir en el archivo:\n{e}", mtype="error")

    def export_to_json_safe(self):
        records_to_export = self._get_records_to_export()
        if not records_to_export:
            self._show_custom_messagebox("Sin Datos", "No hay resultados para exportar.", mtype="warning")
            return

        term = self.term_entry.get().strip().replace('@', '_at_').replace('.', '_dot_')
        timestamp = datetime.now().strftime("%Y%m%d")
        default_filename = f"intelx_{term}_{timestamp}.json"

        exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", "json")
        os.makedirs(exports_dir, exist_ok=True)

        filepath = filedialog.asksaveasfilename(
            initialdir=exports_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(records_to_export, jsonfile, indent=4, ensure_ascii=False)
            self._show_export_success_dialog(filepath)
        except IOError as e:
            self._show_custom_messagebox("Error de Exportación", f"No se pudo escribir en el archivo:\n{e}", mtype="error")

    def _show_export_success_dialog(self, filepath: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Exportación Exitosa")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        # Asignar icono
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        message_label = ctk.CTkLabel(main_frame, text=f"Registros exportados a:\n{os.path.basename(filepath)}", font=self.fonts["main"])
        message_label.pack(pady=(10, 20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        def open_folder():
            try:
                os.startfile(os.path.dirname(filepath))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}", parent=dialog)
            dialog.destroy()
        open_button = ctk.CTkButton(button_frame, text="Abrir Carpeta", command=open_folder, font=self.fonts["main"])
        open_button.pack(side="left", padx=10)
        ok_button = ctk.CTkButton(button_frame, text="OK", command=dialog.destroy, font=self.fonts["main"])
        ok_button.pack(side="left", padx=10)

    def _show_about_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Acerca de IntelX Checker")
        dialog.geometry("400x320")
        dialog.transient(self)
        dialog.grab_set()
        # Asignar icono
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        dialog.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(dialog, text="IntelX Checker", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        version_label = ctk.CTkLabel(dialog, text=f"Versión {self.app_version}", font=self.fonts["secondary"])
        version_label.grid(row=1, column=0, padx=20, pady=0)
        separator = ttk.Separator(dialog, orient="horizontal")
        separator.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        created_by_label = ctk.CTkLabel(dialog, text="Creado por:", font=self.fonts["main"])
        created_by_label.grid(row=3, column=0, padx=20, pady=(0, 10))
        author_label = ctk.CTkLabel(dialog, text="Diego A. Rábalo", font=self.fonts["main_bold"])
        author_label.grid(row=4, column=0, padx=20, pady=0)
        job_title_label = ctk.CTkLabel(dialog, text="Criminólogo & Python Developer", font=self.fonts["secondary"], text_color="gray")
        job_title_label.grid(row=5, column=0, padx=20, pady=(0, 10))
        links_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        links_frame.grid(row=6, column=0)
        github_link = ctk.CTkLabel(links_frame, text="GitHub", text_color="#60A5FA", cursor="hand2", font=self.fonts["secondary"])
        github_link.pack(side="left", padx=10)
        github_link.bind("<Button-1>", lambda event: webbrowser.open("https://github.com/mikear"))
        linkedin_link = ctk.CTkLabel(links_frame, text="LinkedIn", text_color="#60A5FA", cursor="hand2", font=self.fonts["secondary"])
        linkedin_link.pack(side="left", padx=10)
        linkedin_link.bind("<Button-1>", lambda event: webbrowser.open("https://www.linkedin.com/in/rabalo"))
        email_link = ctk.CTkLabel(links_frame, text="Email", text_color="#60A5FA", cursor="hand2", font=self.fonts["secondary"])
        email_link.pack(side="left", padx=10)
        email_link.bind("<Button-1>", lambda event: webbrowser.open("mailto:diego_rabalo@hotmail.com"))
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100, font=self.fonts["main"])
        ok_button.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        dialog.grid_rowconfigure(7, weight=1)

    def _configure_buckets_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configurar Fuentes de Búsqueda")
        dialog.geometry("480x450")
        dialog.transient(self)
        dialog.grab_set()
        # Asignar icono
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        scroll_frame = ctk.CTkScrollableFrame(dialog, label_text="Selecciona las fuentes a consultar", label_font=self.fonts["main"])
        scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        vars = {}
        for i, (display_name, bucket_id, description) in enumerate(self.available_buckets_for_ui):
            var = ctk.StringVar(value="on" if bucket_id in self.selected_buckets_config else "off")
            cb = ctk.CTkCheckBox(scroll_frame, text=display_name, variable=var, onvalue="on", offvalue="off", font=self.fonts["dialog_header"])
            cb.grid(row=i*2, column=0, sticky="w", padx=10, pady=(10,0))
            desc = ctk.CTkLabel(scroll_frame, text=description, text_color="gray", font=self.fonts["dialog_body"], wraplength=380, justify="left")
            desc.grid(row=i*2+1, column=0, sticky="w", padx=25, pady=(0,10))
            vars[bucket_id] = var
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        def save():
            self.selected_buckets_config = [b_id for b_id, v in vars.items() if v.get() == "on"]
            dialog.destroy()
        def cancel():
            dialog.destroy()
        save_btn = ctk.CTkButton(button_frame, text="Guardar", command=save, width=100, font=self.fonts["main"])
        save_btn.pack(side="left", padx=5)
        cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=cancel, fg_color="gray", width=100, font=self.fonts["main"])
        cancel_btn.pack(side="left", padx=5)

    def _on_preview_close(self, storage_id: str):
        if storage_id in self.preview_windows:
            window = self.preview_windows[storage_id]
            try:
                if window and window.winfo_exists():
                    window.destroy()
            except Exception:
                pass
            finally:
                del self.preview_windows[storage_id]

    def _show_custom_messagebox(self, title, message, mtype="info"):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.transient(self)
        dialog.grab_set()
        icon_ico = os.path.join(os.path.dirname(__file__), "..", "docs", "icon.ico")
        if os.path.exists(icon_ico):
            try:
                dialog.iconbitmap(icon_ico)
            except Exception as e:
                print(f"No se pudo asignar el icono a la ventana de diálogo: {e}")
        color = {"info": "#2563eb", "warning": "#f59e42", "error": "#ef4444"}.get(mtype, "#2563eb")
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        label = ctk.CTkLabel(main_frame, text=message, font=self.fonts["main"], text_color=color, wraplength=350, justify="left")
        label.pack(pady=(10, 20))
        ok_btn = ctk.CTkButton(main_frame, text="OK", command=dialog.destroy, font=self.fonts["main"])
        ok_btn.pack(pady=10)

    def _fetch_and_display_credits_safe(self):
        if not hasattr(self, 'intelx_api_key') or not self.intelx_api_key:
            self._update_credits_label("Créditos: N/A (Sin Clave)")
            return
        threading.Thread(target=self._fetch_credits_task, daemon=True).start()

    def _fetch_credits_task(self):
        try:
            headers = {'x-key': self.intelx_api_key, 'User-Agent': f"{USER_AGENT}/CreditCheck"}
            response = requests.get(INTELX_API_URL_AUTH_INFO, headers=headers, timeout=REQUEST_TIMEOUT_AUTH)
            response.raise_for_status()
            data = response.json()
            paths = data.get("paths", {})
            search_credits_info = paths.get("/intelligent/search", {})
            credit_val = search_credits_info.get("Credit", "N/A")
            credits_text = f"Créditos de Búsqueda: {credit_val}"
        except Exception as e:
            logger.error(f"Error al consultar créditos: {e}")
            credits_text = "Créditos: Error"
        self.after(0, lambda: self._update_credits_label(credits_text))

    def _update_status_label(self, text: str):
        self.status_label.configure(text=text)

    def _update_gui_state(self):
        is_searching = hasattr(self, '_is_searching') and self._is_searching
        state = "disabled" if is_searching else "normal"
        self.check_button.configure(state=state)
        self.term_entry.configure(state=state)
        self.cancel_button.configure(state="normal" if is_searching else "disabled")

    def _update_credits_label(self, text: str):
        self.credits_info_label.configure(text=text)

    def get_api_key_link(self):
        import webbrowser
        webbrowser.open("https://intelx.io/account?tab=developer")
"""UI reusable dialogs and components for IntelX Checker.
Simplified and cleaned for public release (PDF export removed)."""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import webbrowser
import logging
import os
import sys
from typing import Dict, Any, Optional, List
from .api import IntelXAPI
from . import exports as exports_module

logger = logging.getLogger(__name__)

class ApiKeyDialog:
    def __init__(self, parent, current_key: str = ""):
        self.result: Optional[str] = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Gestionar Clave API")
        self.dialog.geometry("420x190")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 210
        y = (self.dialog.winfo_screenheight() // 2) - 95
        self.dialog.geometry(f"420x190+{x}+{y}")

        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frame, text="Configurar Clave API de IntelX", font=("Arial", 15, "bold")).pack(pady=(0, 8))
        ctk.CTkLabel(frame, text="Clave API:").pack(anchor="w")
        self.key_entry = ctk.CTkEntry(frame, width=360, show="*")
        self.key_entry.pack(fill="x", pady=(4, 10))
        self.key_entry.insert(0, current_key)
        btns = ctk.CTkFrame(frame)
        btns.pack(fill="x")
        ctk.CTkButton(btns, text="Obtener Clave", command=lambda: webbrowser.open("https://intelx.io/account?tab=developer")).pack(side="left")
        ctk.CTkButton(btns, text="Cancelar", command=self._cancel).pack(side="right")
        ctk.CTkButton(btns, text="Guardar", command=self._save).pack(side="right", padx=(0,5))
        self.key_entry.focus_set()
        self.dialog.bind('<Return>', lambda _e: self._save())
        self.dialog.bind('<Escape>', lambda _e: self._cancel())

    def _save(self):
        self.result = self.key_entry.get().strip()
        self.dialog.destroy()

    def _cancel(self):
        self.result = None
        self.dialog.destroy()

    def get_result(self) -> Optional[str]:
        self.dialog.wait_window()
        return self.result

class PreviewWindow:
    def __init__(self, parent, record: Dict[str, Any], api_client: Optional[IntelXAPI]):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Preview - {record.get('name','N/A')}")
        self.window.geometry("840x620")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.record = record
        self.api_client = api_client
        self.storage_id = record.get('systemid', record.get('storageid',''))
        self._build()
        self._load_content()

    def _build(self):
        top = ctk.CTkFrame(self.window)
        top.pack(fill="both", expand=True, padx=10, pady=10)
        info = ctk.CTkFrame(top)
        info.pack(fill="x", pady=(0,8))
        info_text = (
            f"Media: {self.record.get('media','N/A')}\n"
            f"Domain: {self.record.get('domain','N/A')}\n"
            f"Size: {self.record.get('size','N/A')}\n"
            f"Date: {self.record.get('date','N/A')}"
        )
        ctk.CTkLabel(info, text=info_text, justify="left").pack(anchor="w", padx=8, pady=8)
        body = ctk.CTkFrame(top)
        body.pack(fill="both", expand=True)
        self.content_text = tk.Text(body, wrap="word", font=("Consolas", 10))
        vs = tk.Scrollbar(body, orient="vertical", command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=vs.set)
        self.content_text.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        vs.pack(side="right", fill="y", pady=8, padx=(0,8))

    def _load_content(self):
        self.content_text.insert("1.0", "Cargando vista previa...")
        self.content_text.configure(state="disabled")
        if not self.api_client or not self.storage_id:
            self._update_content("Preview no disponible.")
            return
        import threading
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            ok, content = self.api_client.get_file_preview(self.storage_id)
            if ok:
                self._update_content(content)
            else:
                self._update_content(content)
        except Exception as e:
            logger.exception("Error obteniendo preview")
            self._update_content(str(e))

    def _update_content(self, text: str):
        def cb():
            self.content_text.configure(state="normal")
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", text)
            self.content_text.configure(state="disabled")
        self.window.after(0, cb)

    def _on_close(self):
        if hasattr(self.window.master, '_on_preview_close') and self.storage_id:
            try:
                self.window.master._on_preview_close(self.storage_id)
            except Exception:
                pass
        self.window.destroy()

def show_custom_messagebox(parent, title: str, message: str, msg_type: str = "info"):
    if msg_type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    elif msg_type == "error":
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)

def show_export_success_dialog(parent, filepath: str):
    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath)
    if messagebox.askyesno("Exportación Exitosa", f"Archivo exportado:\n{filename}\n\n¿Abrir carpeta?", parent=parent):
        try:
            if os.name == 'nt':
                os.startfile(folder)  # type: ignore
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        except Exception as e:
            logger.exception("No se pudo abrir carpeta")
            messagebox.showerror("Error", str(e), parent=parent)

def show_export_selection_dialog(parent, records: List[Dict[str, Any]]):
    if not records:
        show_custom_messagebox(parent, "Error", "No hay registros seleccionados", "warning")
        return
    dlg = ctk.CTkToplevel(parent)
    dlg.title("Exportar Selección")
    dlg.geometry("320x220")
    dlg.transient(parent)
    dlg.grab_set()
    frame = ctk.CTkFrame(dlg)
    frame.pack(fill="both", expand=True, padx=16, pady=16)
    ctk.CTkLabel(frame, text=f"Exportar {len(records)} elementos", font=("Arial",14,"bold")).pack(pady=(0,14))
    ctk.CTkButton(frame, text="CSV", command=lambda: _export_and_close(dlg, records, 'csv')).pack(fill="x", pady=4)
    ctk.CTkButton(frame, text="JSON", command=lambda: _export_and_close(dlg, records, 'json')).pack(fill="x", pady=4)
    ctk.CTkButton(frame, text="Cancelar", command=dlg.destroy).pack(fill="x", pady=(14,0))

def _export_and_close(dialog, records: List[Dict[str, Any]], fmt: str):
    try:
        from .utils import sanitize_filename
        search_term = "seleccion"
        timestamp = __import__('datetime').datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports', fmt)
        os.makedirs(base_dir, exist_ok=True)
        filename = f"{sanitize_filename(search_term)}_{timestamp}.{fmt}"
        output = os.path.join(base_dir, filename)
        if fmt == 'csv':
            exports_module.export_to_csv(records, output)
        elif fmt == 'json':
            exports_module.export_to_json(records, output)
        dialog.destroy()
        show_export_success_dialog(dialog.master, output)
    except Exception as e:
        logger.exception("Error exportando selección")
        show_custom_messagebox(dialog, "Error", f"Fallo exportando: {e}", "error")

class AboutDialog:
    def __init__(self, parent, app_version: str, current_language: str = 'es'):
        self.dialog = ctk.CTkToplevel(parent)
        title = "Acerca de" if current_language == 'es' else 'About'
        self.dialog.title(title)
        self.dialog.geometry("500x380")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 250
        y = (self.dialog.winfo_screenheight() // 2) - 190
        self.dialog.geometry(f"500x380+{x}+{y}")
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        ctk.CTkLabel(frame, text=f"IntelX Checker V{app_version}", font=("Arial",18,"bold")).pack(pady=(0,6))
        subtitle = "Herramienta profesional de búsqueda OSINT" if current_language=='es' else "Professional OSINT search tool"
        ctk.CTkLabel(frame, text=subtitle, font=("Arial",12)).pack(pady=(0,14))
        body = (
            "Autor: Diego A. Rábalo\n"
            "LinkedIn: https://www.linkedin.com/in/rabalo\n"
            "Email: diego_rabalo@hotmail.com\n\n"
            "Funciones clave:\n- Búsqueda IntelX\n- Reporte HTML resumido\n- Exportación CSV/JSON\n- Carga incremental\n- Mapeo descriptivo de Media Type"
        )
        txt = tk.Text(frame, height=10, wrap='word', font=("Consolas",10))
        txt.insert('1.0', body)
        txt.configure(state='disabled')
        txt.pack(fill='both', expand=True, pady=(0,10))
        ctk.CTkButton(frame, text="Cerrar" if current_language=='es' else 'Close', command=self.dialog.destroy, width=90).pack()
        self.dialog.bind('<Escape>', lambda _e: self.dialog.destroy())

def show_custom_messagebox(parent, title, message, msg_type="info"):
    """Show custom messagebox with consistent styling"""
    if msg_type == "info":
        messagebox.showinfo(title, message, parent=parent)
    elif msg_type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    elif msg_type == "error":
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)

def show_export_success_dialog(parent, filepath):
    """Show export success dialog with option to open file/folder"""
    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath)
    
    result = messagebox.askyesno(
        "Exportación Exitosa",
        f"Archivo exportado exitosamente:\n{filename}\n\n¿Desea abrir la carpeta de destino?",
        parent=parent
    )
    
    if result:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{folder}"' if sys.platform == 'darwin' else f'xdg-open "{folder}"')
        except Exception as e:
            logger.exception("Error opening folder")
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}", parent=parent)

def get_records_to_export_dialog(parent, all_records, selected_ids=None):
    """Dialog to choose what records to export"""
    if not selected_ids:
        # No selection, export all
        return all_records
    
    # Ask user what to export
    choice = messagebox.askyesnocancel(
        "Exportar Datos",
        f"¿Qué desea exportar?\n\n"
        f"Sí: Solo elementos seleccionados ({len(selected_ids)} elementos)\n"
        f"No: Todos los resultados ({len(all_records)} elementos)\n"
        f"Cancelar: Cancelar exportación",
        parent=parent
    )
    
    if choice is True:
        # Export selected only
        selected_records = []
        for item_id in selected_ids:
            item = parent.results_tree.item(item_id)
            values = item['values']
            if values:
                record_id = values[0]
                record = next((r for r in all_records if r.get('storageid') == record_id), None)
                if record:
                    selected_records.append(record)
        return selected_records
    elif choice is False:
        # Export all
        return all_records
    else:
        # Cancel
        return None

def show_export_selection_dialog(parent, records):
    """Show dialog for exporting selected records"""
    if not records:
        show_custom_messagebox(parent, "Error", "No hay registros para exportar", "warning")
        return
    
    # Create dialog
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Exportar Selección")
    dialog.geometry("300x200")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"300x200+{x}+{y}")
    
    # Main frame
    main_frame = ctk.CTkFrame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ctk.CTkLabel(main_frame, text=f"Exportar {len(records)} elementos", 
                               font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Export buttons
    csv_btn = ctk.CTkButton(main_frame, text="Exportar a CSV", 
                            command=lambda: _export_and_close(dialog, records, "csv"))
    csv_btn.pack(pady=5, fill="x")
    
    json_btn = ctk.CTkButton(main_frame, text="Exportar a JSON", 
                             command=lambda: _export_and_close(dialog, records, "json"))
    json_btn.pack(pady=5, fill="x")
    
    # Botón PDF removido (no implementado actualmente)
    
    # Cancel button
    cancel_btn = ctk.CTkButton(main_frame, text="Cancelar", command=dialog.destroy)
    cancel_btn.pack(pady=(10, 0), fill="x")

def _export_and_close(dialog, records, export_type):
    """Helper function to export and close dialog"""
    try:
        filepath = None
        if export_type == "csv":
            filepath = exports_module.export_to_csv(records, "seleccion")
        elif export_type == "json":
            filepath = exports_module.export_to_json(records, "seleccion")
    # PDF no implementado (funcionalidad desactivada)
        
        if filepath:
            dialog.destroy()
            show_export_success_dialog(dialog.master, filepath)
            
    except Exception as e:
        logger.exception(f"Error exporting {export_type}")
        show_custom_messagebox(dialog, "Error", f"Error exportando {export_type.upper()}: {e}", "error")

def safe_get_text_content(widget):
    """Safely get text content from widget"""
    try:
        if hasattr(widget, 'get'):
            if hasattr(widget, 'index'):  # Text widget
                return widget.get("1.0", "end-1c")
            else:  # Entry widget
                return widget.get()
        return ""
    except Exception as e:
        logger.exception("Error getting text content")
        return ""

def safe_set_text_content(widget, content):
    """Safely set text content in widget"""
    try:
        if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
            if hasattr(widget, 'index'):  # Text widget
                widget.delete("1.0", "end")
                widget.insert("1.0", content)
            else:  # Entry widget
                widget.delete(0, "end")
                widget.insert(0, content)
        elif hasattr(widget, 'configure'):
            widget.configure(text=content)
    except Exception as e:
        logger.exception("Error setting text content")


class AboutDialog:
    """Compact About dialog with clickable links"""
    def __init__(self, parent, app_version, current_language="es"):
        self.dialog = ctk.CTkToplevel(parent)
        self.current_language = current_language
        
        # Setup dialog
        title = "Acerca de" if current_language == "es" else "About"
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (250)
        y = (self.dialog.winfo_screenheight() // 2) - (200)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create content
        self._create_content(main_frame, app_version)
        
        # Close button
        close_btn = ctk.CTkButton(main_frame, text="Cerrar" if current_language == "es" else "Close", 
                                  command=self.dialog.destroy, width=100)
        close_btn.pack(pady=(15, 0))
        
        # Bind escape key
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.dialog.focus_set()
    
    def _create_content(self, parent, app_version):
        """Create dialog content"""
        # Title
        title_label = ctk.CTkLabel(parent, text=f"IntelX Checker V{app_version}", 
                                   font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        if self.current_language == "es":
            subtitle = "Herramienta profesional para búsqueda de inteligencia"
        else:
            subtitle = "Professional intelligence search tool"
            
        subtitle_label = ctk.CTkLabel(parent, text=subtitle, font=("Arial", 12))
        subtitle_label.pack(pady=(0, 15))
        
        # Developer info
        dev_frame = ctk.CTkFrame(parent)
        dev_frame.pack(fill="x", pady=(0, 10))
        
        dev_title = "👨‍💻 DESARROLLADO POR:" if self.current_language == "es" else "👨‍💻 DEVELOPED BY:"
        dev_label = ctk.CTkLabel(dev_frame, text=dev_title, font=("Arial", 12, "bold"))
        dev_label.pack(pady=(10, 5))
        
        name_label = ctk.CTkLabel(dev_frame, text="Diego A. Rábalo | @mikear", font=("Arial", 11))
        name_label.pack()
        
        title_text = "Criminólogo & Python Developer" if self.current_language == "es" else "Criminologist & Python Developer"
        title_label = ctk.CTkLabel(dev_frame, text=title_text, font=("Arial", 10))
        title_label.pack(pady=(0, 10))
        
        # Contact links frame
        contact_frame = ctk.CTkFrame(parent)
        contact_frame.pack(fill="x", pady=(0, 10))
        
        contact_title = "🔗 CONTACTO:" if self.current_language == "es" else "🔗 CONTACT:"
        contact_label = ctk.CTkLabel(contact_frame, text=contact_title, font=("Arial", 12, "bold"))
        contact_label.pack(pady=(10, 5))
        
        # GitHub link
        github_btn = ctk.CTkButton(contact_frame, text="📂 GitHub: mikear", 
                                   command=lambda: webbrowser.open("https://github.com/mikear"),
                                   width=200, height=30, font=("Arial", 10))
        github_btn.pack(pady=2)
        
        # LinkedIn link
        linkedin_btn = ctk.CTkButton(contact_frame, text="💼 LinkedIn: rabalo", 
                                     command=lambda: webbrowser.open("https://www.linkedin.com/in/rabalo"),
                                     width=200, height=30, font=("Arial", 10))
        linkedin_btn.pack(pady=2)
        
        # Email link
        email_btn = ctk.CTkButton(contact_frame, text="📧 Email", 
                                  command=lambda: webbrowser.open("mailto:diego_rabalo@hotmail.com"),
                                  width=200, height=30, font=("Arial", 10))
        email_btn.pack(pady=(2, 10))
        
        # Features
        features_frame = ctk.CTkFrame(parent)
        features_frame.pack(fill="x", pady=(0, 5))
        
        features_title = "🚀 CARACTERÍSTICAS:" if self.current_language == "es" else "🚀 FEATURES:"
        features_label = ctk.CTkLabel(features_frame, text=features_title, font=("Arial", 11, "bold"))
        features_label.pack(pady=(8, 3))
        
        if self.current_language == "es":
            features_text = "• Búsqueda avanzada • Exportación múltiple\n• Reportes Mandiant • Interfaz bilingüe"
        else:
            features_text = "• Advanced search • Multiple export formats\n• Mandiant reports • Bilingual interface"
            
        features_content = ctk.CTkLabel(features_frame, text=features_text, font=("Arial", 9))
        features_content.pack(pady=(0, 8))
        
        # Philosophy
        philosophy = "💡 \"VINE VIDI VICI\""
        philosophy_label = ctk.CTkLabel(parent, text=philosophy, font=("Arial", 10, "italic"))
        philosophy_label.pack(pady=(5, 0))

"""
UI Components Module
Provides reusable UI dialogs and components for the IntelX Checker application
"""
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ctk

import webbrowser
import logging
import os
import sys
from typing import Optional, List, Dict, Any
import exports as exports_module

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

logger = logging.getLogger(__name__)

def set_dialog_icon(dialog_window):
    """Configurar icono para ventanas de diálogo"""
    try:
        # Buscar archivo de icono
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'docs', 'icon.ico'),
            os.path.join(os.path.dirname(__file__), '..', 'docs', 'icon.png'),
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            os.path.join(os.path.dirname(__file__), 'icon.png')
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                if icon_path.endswith('.ico'):
                    dialog_window.iconbitmap(icon_path)
                    break
                elif icon_path.endswith('.png') and Image and ImageTk:
                    # Usar PIL para cargar PNG si está disponible
                    img = Image.open(icon_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    dialog_window.iconphoto(True, photo)
                    # Mantener referencia en el dialog para evitar garbage collection
                    dialog_window._icon_photo = photo
                    break
    except Exception as e:
        logger.debug(f"No se pudo cargar el icono del diálogo: {e}")

class ApiKeyDialog:
    """Dialog for managing API key"""
    def __init__(self, parent, current_key=""):
        self.result = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Gestionar Clave API")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar icono del diálogo
        set_dialog_icon(self.dialog)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"400x200+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Configurar Clave API de IntelX", 
                                   font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # API Key entry
        key_label = ctk.CTkLabel(main_frame, text="Clave API:")
        key_label.pack(anchor="w")
        
        self.key_entry = ctk.CTkEntry(main_frame, width=350, show="*")
        self.key_entry.pack(pady=(5, 10), fill="x")
        self.key_entry.insert(0, current_key)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = ctk.CTkButton(buttons_frame, text="Guardar", command=self._save)
        save_btn.pack(side="right", padx=(5, 0))
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancelar", command=self._cancel)
        cancel_btn.pack(side="right")
        
        get_key_btn = ctk.CTkButton(buttons_frame, text="Obtener Clave", command=self._open_api_page)
        get_key_btn.pack(side="left")
        
        # Focus and bind
        self.key_entry.focus_set()
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _save(self):
        self.result = self.key_entry.get().strip()
        self.dialog.destroy()
    
    def _cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def _open_api_page(self):
        webbrowser.open("https://intelx.io/account?tab=developer")
    
    def get_result(self):
        self.dialog.wait_window()
        return self.result

class PreviewWindow:
    """Window for previewing file contents"""
    def __init__(self, parent, record):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Preview - {record.get('media', 'Unknown')}")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        # Configurar icono del diálogo
        set_dialog_icon(self.window)
        
        self.record = record
        self.storage_id = record.get('storageid', '')
        
        # Setup UI
        self._setup_ui()
        
        # Load content
        self._load_content()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        """Setup preview UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Info frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Record info
        info_text = f"""Media: {self.record.get('media', 'N/A')}
Domain: {self.record.get('domain', 'N/A')}
Size: {self.record.get('size', 'N/A')}
Date: {self.record.get('date', 'N/A')}"""
        
        info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left")
        info_label.pack(padx=10, pady=10, anchor="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Text widget for content
        self.content_text = tk.Text(content_frame, wrap="word", font=("Consolas", 10))
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        self.content_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
    
    def _load_content(self):
        """Load and display content"""
        try:
            # Show basic data first
            data = self.record.get('data', 'No data available')
            self.content_text.insert("1.0", data)
            self.content_text.configure(state="disabled")
            
            # TODO: Implement actual file preview from IntelX API
            # This would require calling the preview API endpoint
            
        except Exception as e:
            logger.exception("Error loading preview content")
            self.content_text.insert("1.0", f"Error loading content: {e}")
            self.content_text.configure(state="disabled")
    
    def _on_close(self):
        """Handle window close"""
        # Notify parent about close
        if hasattr(self.window.master, '_on_preview_close'):
            self.window.master._on_preview_close(self.storage_id)
        self.window.destroy()

def show_custom_messagebox(parent, title, message, msg_type="info"):
    """Show custom messagebox with consistent styling and icons"""
    # Para mayor compatibilidad, crear un diálogo personalizado con icono
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    # Configurar icono del diálogo
    set_dialog_icon(dialog)
    
    # Centrar diálogo
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    
    # Marco principal
    main_frame = ctk.CTkFrame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Mensaje
    message_label = ctk.CTkLabel(main_frame, text=message, font=("Arial", 12), 
                                wraplength=350, justify="left")
    message_label.pack(pady=20, expand=True)
    
    # Botón OK
    ok_btn = ctk.CTkButton(main_frame, text="OK", command=dialog.destroy, width=100)
    ok_btn.pack(pady=(0, 10))
    
    # Esperar a que se cierre el diálogo
    dialog.wait_window()

def show_custom_question_dialog(parent, title, message):
    """Show custom yes/no question dialog with consistent styling and icons"""
    result = {"value": False}
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    # Configurar icono del diálogo
    set_dialog_icon(dialog)
    
    # Centrar diálogo
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    
    # Marco principal
    main_frame = ctk.CTkFrame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Mensaje
    message_label = ctk.CTkLabel(main_frame, text=message, font=("Arial", 12), 
                                wraplength=350, justify="left")
    message_label.pack(pady=20, expand=True)
    
    # Marco de botones
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(pady=(0, 10))
    
    def on_yes():
        result["value"] = True
        dialog.destroy()
    
    def on_no():
        result["value"] = False
        dialog.destroy()
    
    # Botones
    yes_btn = ctk.CTkButton(button_frame, text="Sí", command=on_yes, width=80)
    yes_btn.pack(side="left", padx=(0, 10))
    
    no_btn = ctk.CTkButton(button_frame, text="No", command=on_no, width=80)
    no_btn.pack(side="left")
    
    # Esperar a que se cierre el diálogo
    dialog.wait_window()
    return result["value"]

def show_custom_yesnocancel_dialog(parent, title, message):
    """Show custom yes/no/cancel question dialog with consistent styling and icons"""
    result = {"value": None}
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    # Configurar icono del diálogo
    set_dialog_icon(dialog)
    
    # Centrar diálogo
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (250 // 2)
    dialog.geometry(f"450x250+{x}+{y}")
    
    # Marco principal
    main_frame = ctk.CTkFrame(dialog)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Mensaje
    message_label = ctk.CTkLabel(main_frame, text=message, font=("Arial", 12), 
                                wraplength=400, justify="left")
    message_label.pack(pady=20, expand=True)
    
    # Marco de botones
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(pady=(0, 10))
    
    def on_yes():
        result["value"] = True
        dialog.destroy()
    
    def on_no():
        result["value"] = False
        dialog.destroy()
    
    def on_cancel():
        result["value"] = None
        dialog.destroy()
    
    # Botones
    yes_btn = ctk.CTkButton(button_frame, text="Sí", command=on_yes, width=80)
    yes_btn.pack(side="left", padx=(0, 10))
    
    no_btn = ctk.CTkButton(button_frame, text="No", command=on_no, width=80)
    no_btn.pack(side="left", padx=(0, 10))
    
    cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=on_cancel, width=80)
    cancel_btn.pack(side="left")
    
    # Esperar a que se cierre el diálogo
    dialog.wait_window()
    return result["value"]

def show_export_success_dialog(parent, filepath):
    """Show export success dialog with option to open file/folder"""
    filename = os.path.basename(filepath)
    folder = os.path.dirname(filepath)
    
    # Usar diálogo personalizado con icono
    result = show_custom_question_dialog(
        parent,
        "Exportación Exitosa",
        f"Archivo exportado exitosamente:\n{filename}\n\n¿Desea abrir la carpeta de destino?"
    )
    
    if result:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{folder}"' if sys.platform == 'darwin' else f'xdg-open "{folder}"')
        except Exception as e:
            logger.exception("Error opening folder")
            show_custom_messagebox(parent, "Error", f"No se pudo abrir la carpeta: {e}", "error")

def get_records_to_export_dialog(parent, all_records, selected_ids=None):
    """Dialog to choose what records to export"""
    if not selected_ids:
        # No selection, export all
        return all_records
    
    # Ask user what to export usando diálogo personalizado
    choice = show_custom_yesnocancel_dialog(
        parent,
        "Exportar Datos",
        f"¿Qué desea exportar?\n\n"
        f"Sí: Solo elementos seleccionados ({len(selected_ids)} elementos)\n"
        f"No: Todos los resultados ({len(all_records)} elementos)\n"
        f"Cancelar: Cancelar exportación"
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
    
    # Configurar icono del diálogo
    set_dialog_icon(dialog)
    
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
    # elif export_type == "pdf":
    #     filepath = exports_module.generate_pdf_report(records, title="Selección")
        
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
        
        # Configurar icono del diálogo
        set_dialog_icon(self.dialog)
        
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

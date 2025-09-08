"""
UI Components Module
Provides reusable UI dialogs and components for the IntelX Checker application
"""
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
try:
    import customtkinter as ctk
except ImportError:
    import tkinter as ctk
    ctk.CTk = ctk.Tk
    ctk.CTkFrame = ctk.Frame
    ctk.CTkLabel = ctk.Label
    ctk.CTkEntry = ctk.Entry
    ctk.CTkButton = ctk.Button
    ctk.CTkToplevel = ctk.Toplevel

import webbrowser
import logging
import os
import sys
from typing import Optional, List, Dict, Any
from . import exports as exports_module

logger = logging.getLogger(__name__)

class ApiKeyDialog:
    """Dialog for managing API key"""
    def __init__(self, parent, current_key=""):
        self.result = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Gestionar Clave API")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
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
    
    pdf_btn = ctk.CTkButton(main_frame, text="Exportar a PDF", 
                            command=lambda: _export_and_close(dialog, records, "pdf"))
    pdf_btn.pack(pady=5, fill="x")
    
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
        elif export_type == "pdf":
            filepath = exports_module.generate_pdf_report(records, title="Selección")
        
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

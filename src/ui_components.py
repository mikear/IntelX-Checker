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

COLORS = {
    "accent": "#6366f1",
    "accent_hover": "#4f46e5",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "success": "#22c55e",
    "card": ("#ffffff", "#1e293b"),
    "border": ("#e2e8f0", "#334155"),
    "text_primary": ("#1e293b", "#f1f5f9"),
    "text_secondary": ("#64748b", "#94a3b8"),
    "entry_bg": ("#ffffff", "#1e293b"),
    "entry_border": ("#cbd5e1", "#475569"),
}

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
        self.dialog.geometry("480x260")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar icono del diálogo
        set_dialog_icon(self.dialog)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (260 // 2)
        self.dialog.geometry(f"480x260+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog, fg_color=COLORS["card"], corner_radius=16)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔑 Configurar Clave API de IntelX",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(5, 12))
        
        # API Key entry
        key_label = ctk.CTkLabel(
            main_frame,
            text="Clave API:",
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"]
        )
        key_label.pack(anchor="w", padx=5)

        self.key_entry = ctk.CTkEntry(
            main_frame,
            height=40,
            corner_radius=20,
            border_width=2,
            border_color=COLORS["entry_border"],
            fg_color=COLORS["entry_bg"],
            font=("Segoe UI", 13),
            show="*"
        )
        self.key_entry.pack(pady=(5, 15), fill="x", padx=5)
        self.key_entry.insert(0, current_key)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(5, 0), padx=5)

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=self._save,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            corner_radius=20,
            height=38,
            font=("Segoe UI", 12, "bold"),
            text_color="white",
            width=120
        )
        save_btn.pack(side="right", padx=(8, 0))

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=self._cancel,
            fg_color="#6b7280",
            hover_color="#4b5563",
            corner_radius=20,
            height=38,
            font=("Segoe UI", 12),
            text_color="white",
            width=120
        )
        cancel_btn.pack(side="right", padx=8)

        get_key_btn = ctk.CTkButton(
            buttons_frame,
            text="Obtener Clave",
            command=self._open_api_page,
            fg_color="#22c55e",
            hover_color="#16a34a",
            corner_radius=20,
            height=38,
            font=("Segoe UI", 12),
            text_color="white",
            width=140
        )
        get_key_btn.pack(side="left", padx=(0, 8))
        
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
        
        set_dialog_icon(self.window)
        
        self.record = record
        self.storage_id = record.get('storageid', '')
        
        self._setup_ui()
        self._load_content()
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        """Setup preview UI"""
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["card"], corner_radius=16)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        info_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_text = f"""Media: {self.record.get('media', 'N/A')}
Domain: {self.record.get('domain', 'N/A')}
Size: {self.record.get('size', 'N/A')}
Date: {self.record.get('date', 'N/A')}"""
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            justify="left",
            font=("Segoe UI", 11),
            text_color=COLORS["text_primary"]
        )
        info_label.pack(padx=12, pady=10, anchor="w")
        
        content_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        content_frame.pack(fill="both", expand=True)
        
        self.content_text = tk.Text(
            content_frame,
            wrap="word",
            font=("Consolas", 11),
            bg="#0f172a" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#f1f5f9" if ctk.get_appearance_mode() == "Dark" else "#1e293b",
            relief="flat",
            borderwidth=0
        )
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
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("450x220")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    set_dialog_icon(dialog)
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (220 // 2)
    dialog.geometry(f"450x220+{x}+{y}")
    
    main_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=16)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    icon_prefix = "ℹ️ "
    btn_color = "#6366f1"
    btn_hover = "#4f46e5"
    if msg_type == "error":
        icon_prefix = "❌ "
        btn_color = "#ef4444"
        btn_hover = "#dc2626"
    elif msg_type == "warning":
        icon_prefix = "⚠️ "
        btn_color = "#f59e0b"
        btn_hover = "#d97706"
    elif msg_type == "success":
        icon_prefix = "✅ "
        btn_color = "#22c55e"
        btn_hover = "#16a34a"

    message_label = ctk.CTkLabel(
        main_frame,
        text=f"{icon_prefix}{message}",
        font=("Segoe UI", 13),
        text_color=COLORS["text_primary"],
        wraplength=390,
        justify="left"
    )
    message_label.pack(pady=20, expand=True)
    
    ok_btn = ctk.CTkButton(
        main_frame,
        text="OK",
        command=dialog.destroy,
        fg_color=btn_color,
        hover_color=btn_hover,
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12, "bold"),
        text_color="white",
        width=120
    )
    ok_btn.pack(pady=(0, 10))
    
    dialog.wait_window()

def show_custom_question_dialog(parent, title, message):
    """Show custom yes/no question dialog with consistent styling and icons"""
    result = {"value": False}
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("480x250")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    set_dialog_icon(dialog)
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
    y = (dialog.winfo_screenheight() // 2) - (250 // 2)
    dialog.geometry(f"480x250+{x}+{y}")
    
    main_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=16)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    message_label = ctk.CTkLabel(
        main_frame,
        text=f"❓ {message}",
        font=("Segoe UI", 13),
        text_color=COLORS["text_primary"],
        wraplength=420,
        justify="left"
    )
    message_label.pack(pady=20, expand=True)
    
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=(0, 10))
    
    def on_yes():
        result["value"] = True
        dialog.destroy()
    
    def on_no():
        result["value"] = False
        dialog.destroy()
    
    yes_btn = ctk.CTkButton(
        button_frame,
        text="Sí",
        command=on_yes,
        fg_color="#6366f1",
        hover_color="#4f46e5",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12, "bold"),
        text_color="white",
        width=100
    )
    yes_btn.pack(side="left", padx=(0, 10))
    
    no_btn = ctk.CTkButton(
        button_frame,
        text="No",
        command=on_no,
        fg_color="#6b7280",
        hover_color="#4b5563",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12),
        text_color="white",
        width=100
    )
    no_btn.pack(side="left")
    
    dialog.wait_window()
    return result["value"]

def show_custom_yesnocancel_dialog(parent, title, message):
    """Show custom yes/no/cancel question dialog with consistent styling and icons"""
    result = {"value": None}
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("500x280")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    set_dialog_icon(dialog)
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (280 // 2)
    dialog.geometry(f"500x280+{x}+{y}")
    
    main_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=16)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    message_label = ctk.CTkLabel(
        main_frame,
        text=f"❓ {message}",
        font=("Segoe UI", 13),
        text_color=COLORS["text_primary"],
        wraplength=440,
        justify="left"
    )
    message_label.pack(pady=20, expand=True)
    
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
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
    
    yes_btn = ctk.CTkButton(
        button_frame,
        text="Sí",
        command=on_yes,
        fg_color="#6366f1",
        hover_color="#4f46e5",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12, "bold"),
        text_color="white",
        width=100
    )
    yes_btn.pack(side="left", padx=(0, 10))
    
    no_btn = ctk.CTkButton(
        button_frame,
        text="No",
        command=on_no,
        fg_color="#6b7280",
        hover_color="#4b5563",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12),
        text_color="white",
        width=100
    )
    no_btn.pack(side="left", padx=(0, 10))
    
    cancel_btn = ctk.CTkButton(
        button_frame,
        text="Cancelar",
        command=on_cancel,
        fg_color="#ef4444",
        hover_color="#dc2626",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12),
        text_color="white",
        width=100
    )
    cancel_btn.pack(side="left")
    
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
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Exportar Selección")
    dialog.geometry("400x350")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    set_dialog_icon(dialog)
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (350 // 2)
    dialog.geometry(f"400x350+{x}+{y}")
    
    main_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=16)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    title_label = ctk.CTkLabel(
        main_frame,
        text=f"📤 Exportar {len(records)} elementos",
        font=("Segoe UI", 16, "bold"),
        text_color=COLORS["text_primary"]
    )
    title_label.pack(pady=(5, 20))

    csv_btn = ctk.CTkButton(
        main_frame,
        text="Exportar a CSV",
        command=lambda: _export_and_close(dialog, records, "csv"),
        fg_color="#6366f1",
        hover_color="#4f46e5",
        corner_radius=20,
        height=40,
        font=("Segoe UI", 12, "bold"),
        text_color="white"
    )
    csv_btn.pack(pady=6, fill="x", padx=10)

    json_btn = ctk.CTkButton(
        main_frame,
        text="Exportar a JSON",
        command=lambda: _export_and_close(dialog, records, "json"),
        fg_color="#6366f1",
        hover_color="#4f46e5",
        corner_radius=20,
        height=40,
        font=("Segoe UI", 12, "bold"),
        text_color="white"
    )
    json_btn.pack(pady=6, fill="x", padx=10)

    cancel_btn = ctk.CTkButton(
        main_frame,
        text="Cancelar",
        command=dialog.destroy,
        fg_color="#6b7280",
        hover_color="#4b5563",
        corner_radius=20,
        height=38,
        font=("Segoe UI", 12),
        text_color="white"
    )
    cancel_btn.pack(pady=(15, 0), fill="x", padx=10)

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
        
        title = "Acerca de" if current_language == "es" else "About"
        self.dialog.title(title)
        self.dialog.geometry("520x460")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        set_dialog_icon(self.dialog)
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (260)
        y = (self.dialog.winfo_screenheight() // 2) - (230)
        self.dialog.geometry(f"520x460+{x}+{y}")
        
        main_frame = ctk.CTkFrame(self.dialog, fg_color=COLORS["card"], corner_radius=16)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._create_content(main_frame, app_version)
        
        close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar" if current_language == "es" else "Close",
            command=self.dialog.destroy,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            corner_radius=20,
            height=38,
            font=("Segoe UI", 12, "bold"),
            text_color="white",
            width=120
        )
        close_btn.pack(pady=(12, 0))
        
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.dialog.focus_set()
    
    def _create_content(self, parent, app_version):
        """Create dialog content"""
        title_label = ctk.CTkLabel(
            parent,
            text=f"IntelX Checker V{app_version}",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["accent"]
        )
        title_label.pack(pady=(0, 4))

        subtitle = "Herramienta profesional para búsqueda de inteligencia" if self.current_language == "es" else "Professional intelligence search tool"
            
        subtitle_label = ctk.CTkLabel(
            parent,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 10))
        
        dev_frame = ctk.CTkFrame(parent, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        dev_frame.pack(fill="x", pady=(0, 8), ipady=4)
        
        dev_title = "👨‍💻 DESARROLLADO POR:" if self.current_language == "es" else "👨‍💻 DEVELOPED BY:"
        dev_label = ctk.CTkLabel(dev_frame, text=dev_title, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_primary"])
        dev_label.pack(pady=(6, 2))
        
        name_label = ctk.CTkLabel(dev_frame, text="Diego A. Rábalo | @mikear", font=("Segoe UI", 11), text_color=COLORS["text_primary"])
        name_label.pack()
        
        title_text = "Criminólogo & Python Developer" if self.current_language == "es" else "Criminologist & Python Developer"
        title_label = ctk.CTkLabel(dev_frame, text=title_text, font=("Segoe UI", 10), text_color=COLORS["text_secondary"])
        title_label.pack(pady=(0, 6))
        
        contact_frame = ctk.CTkFrame(parent, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        contact_frame.pack(fill="x", pady=(0, 8), ipady=4)
        
        contact_title = "🔗 CONTACTO:" if self.current_language == "es" else "🔗 CONTACT:"
        contact_label = ctk.CTkLabel(contact_frame, text=contact_title, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_primary"])
        contact_label.pack(pady=(6, 4))

        github_btn = ctk.CTkButton(
            contact_frame,
            text="📂 GitHub: mikear",
            command=lambda: webbrowser.open("https://github.com/mikear"),
            fg_color="transparent",
            text_color="#6366f1",
            hover_color=("gray86", "gray25"),
            font=("Segoe UI", 11),
            anchor="center",
            height=26
        )
        github_btn.pack(pady=1)

        linkedin_btn = ctk.CTkButton(
            contact_frame,
            text="💼 LinkedIn: rabalo",
            command=lambda: webbrowser.open("https://www.linkedin.com/in/rabalo"),
            fg_color="transparent",
            text_color="#6366f1",
            hover_color=("gray86", "gray25"),
            font=("Segoe UI", 11),
            anchor="center",
            height=26
        )
        linkedin_btn.pack(pady=1)

        email_btn = ctk.CTkButton(
            contact_frame,
            text="📧 Email: diego_rabalo@hotmail.com",
            command=lambda: webbrowser.open("mailto:diego_rabalo@hotmail.com"),
            fg_color="transparent",
            text_color="#6366f1",
            hover_color=("gray86", "gray25"),
            font=("Segoe UI", 11),
            anchor="center",
            height=26
        )
        email_btn.pack(pady=(1, 6))

        features_frame = ctk.CTkFrame(parent, fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        features_frame.pack(fill="x", pady=(0, 4))
        
        features_title = "🚀 CARACTERÍSTICAS:" if self.current_language == "es" else "🚀 FEATURES:"
        features_label = ctk.CTkLabel(features_frame, text=features_title, font=("Segoe UI", 11, "bold"), text_color=COLORS["text_primary"])
        features_label.pack(pady=(6, 2))
        
        features_text = "• Búsqueda avanzada • Exportación múltiple • Reportes SVG • Interfaz bilingüe" if self.current_language == "es" else "• Advanced search • Multiple exports • SVG reports • Bilingual interface"
            
        features_content = ctk.CTkLabel(features_frame, text=features_text, font=("Segoe UI", 10), text_color=COLORS["text_secondary"])
        features_content.pack(pady=(0, 6))
        
        philosophy = "💡 \"VENI VIDI VICI\""
        philosophy_label = ctk.CTkLabel(parent, text=philosophy, font=("Segoe UI", 10, "italic"), text_color=COLORS["text_secondary"])
        philosophy_label.pack(pady=(2, 0))

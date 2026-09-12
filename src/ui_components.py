"""
UI Components Module (PySide6)
Provides reusable UI dialogs and components for the IntelX Checker application
"""
import os
import sys
import webbrowser
import logging
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices

logger = logging.getLogger(__name__)

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "surface": "#FFFFFF",
    "border": "#E2E8F0",
    "text_heading": "#0F172A",
    "text_body": "#334155",
    "text_subtle": "#64748B",
    "text_disabled": "#94A3B8",
    "success": "#22C55E",
    "success_hover": "#16A34A",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "gray": "#6B7280",
    "gray_hover": "#4B5563",
    "bg_main": "#F8FAFC",
}


class ApiKeyDialog(QDialog):
    """Dialog for managing API key"""
    def __init__(self, parent=None, current_key=""):
        super().__init__(parent)
        self.result = None
        self.setWindowTitle("Gestionar Clave API")
        self.setFixedSize(480, 260)
        self.setModal(True)

        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("🔑 Configurar Clave API de IntelX")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_heading']};")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(12)

        key_label = QLabel("Clave API:")
        key_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_subtle']};")
        layout.addWidget(key_label)

        self.key_entry = QLineEdit()
        self.key_entry.setEchoMode(QLineEdit.Password)
        self.key_entry.setFixedHeight(40)
        self.key_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {COLORS['border']};
                border-radius: 20px;
                padding: 5px 15px;
                font-size: 13px;
                background-color: {COLORS['surface']};
                color: {COLORS['text_heading']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        self.key_entry.setText(current_key)
        layout.addWidget(self.key_entry)
        layout.addSpacing(15)

        buttons_layout = QHBoxLayout()

        get_key_btn = QPushButton("Obtener Clave")
        get_key_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['success_hover']}; }}
        """)
        get_key_btn.clicked.connect(self._open_api_page)
        buttons_layout.addWidget(get_key_btn)

        buttons_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['gray']};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {COLORS['gray_hover']}; }}
        """)
        cancel_btn.clicked.connect(self._cancel)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        save_btn.clicked.connect(self._save)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_frame)

        self.key_entry.setFocus()
        self.key_entry.returnPressed.connect(self._save)

    def _save(self):
        self.result = self.key_entry.text().strip()
        self.accept()

    def _cancel(self):
        self.result = None
        self.reject()

    def _open_api_page(self):
        webbrowser.open("https://intelx.io/account?tab=developer")

    def get_result(self):
        if self.exec() == QDialog.Accepted:
            return self.result
        return None


class PreviewWindow(QDialog):
    """Window for previewing file contents"""
    def __init__(self, parent, record):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle(f"Preview - {record.get('media', 'Unknown')}")
        self.setMinimumSize(800, 600)
        self.setModal(False)

        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(15, 15, 15, 15)

        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 10, 12, 10)

        info_text = f"""Media: {record.get('media', 'N/A')}
Domain: {record.get('domain', 'N/A')}
Size: {record.get('size', 'N/A')}
Date: {record.get('date', 'N/A')}"""
        info_label = QLabel(info_text)
        info_label.setStyleSheet(f"font-size: 11px; color: {COLORS['text_heading']};")
        info_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(info_label)
        layout.addWidget(info_frame)

        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(4, 4, 4, 4)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet(
            f"font-family: 'Consolas', monospace; font-size: 11px; "
            f"background-color: {COLORS['bg_main']}; color: {COLORS['text_heading']};"
        )
        data = record.get('data', 'No data available')
        self.content_text.setText(str(data))
        content_layout.addWidget(self.content_text)
        layout.addWidget(content_frame, stretch=1)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_frame)


class AboutDialog(QDialog):
    """Compact About dialog with clickable links"""
    def __init__(self, parent, app_version, current_language="es"):
        super().__init__(parent)
        self.setWindowTitle("Acerca de" if current_language == "es" else "About")
        self.setFixedSize(520, 460)
        self.setModal(True)

        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(f"IntelX Checker V{app_version}")
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['primary']};")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle = "Herramienta profesional para búsqueda de inteligencia" if current_language == "es" else "Professional intelligence search tool"
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_subtle']};")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)

        # Developer section
        dev_frame = QFrame()
        dev_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['surface']};
            }}
        """)
        dev_layout = QVBoxLayout(dev_frame)
        dev_layout.setContentsMargins(10, 8, 10, 8)

        dev_title = "👨‍💻 DESARROLLADO POR:" if current_language == "es" else "👨‍💻 DEVELOPED BY:"
        dev_title_lbl = QLabel(dev_title)
        dev_title_lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {COLORS['text_heading']};")
        dev_title_lbl.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(dev_title_lbl)

        name_lbl = QLabel("Diego A. Rábalo | @mikear")
        name_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_heading']};")
        name_lbl.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(name_lbl)

        title_text = "Criminólogo & Python Developer" if current_language == "es" else "Criminologist & Python Developer"
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet(f"font-size: 10px; color: {COLORS['text_subtle']};")
        title_lbl.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(title_lbl)

        layout.addWidget(dev_frame)
        layout.addSpacing(6)

        # Contact section
        contact_frame = QFrame()
        contact_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['surface']};
            }}
        """)
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setContentsMargins(10, 8, 10, 8)

        contact_title = "🔗 CONTACTO:" if current_language == "es" else "🔗 CONTACT:"
        contact_title_lbl = QLabel(contact_title)
        contact_title_lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {COLORS['text_heading']};")
        contact_title_lbl.setAlignment(Qt.AlignCenter)
        contact_layout.addWidget(contact_title_lbl)

        links = [
            ("📂 GitHub: mikear", "https://github.com/mikear"),
            ("💼 LinkedIn: rabalo", "https://www.linkedin.com/in/rabalo"),
            ("📧 Email: diego_rabalo@hotmail.com", "mailto:diego_rabalo@hotmail.com"),
        ]
        for text, url in links:
            link_lbl = QLabel(f'<a href="{url}" style="color: {COLORS["primary"]}; text-decoration: none;">{text}</a>')
            link_lbl.setStyleSheet(f"font-size: 11px;")
            link_lbl.setOpenExternalLinks(True)
            link_lbl.setAlignment(Qt.AlignCenter)
            contact_layout.addWidget(link_lbl)

        layout.addWidget(contact_frame)
        layout.addSpacing(6)

        # Features section
        features_frame = QFrame()
        features_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                background-color: {COLORS['surface']};
            }}
        """)
        features_layout = QVBoxLayout(features_frame)
        features_layout.setContentsMargins(10, 8, 10, 8)

        features_title = "🚀 CARACTERÍSTICAS:" if current_language == "es" else "🚀 FEATURES:"
        features_title_lbl = QLabel(features_title)
        features_title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['text_heading']};")
        features_title_lbl.setAlignment(Qt.AlignCenter)
        features_layout.addWidget(features_title_lbl)

        features_text = "• Búsqueda avanzada • Exportación múltiple • Reportes SVG • Interfaz bilingüe" if current_language == "es" else "• Advanced search • Multiple exports • SVG reports • Bilingual interface"
        features_lbl = QLabel(features_text)
        features_lbl.setStyleSheet(f"font-size: 10px; color: {COLORS['text_subtle']};")
        features_lbl.setAlignment(Qt.AlignCenter)
        features_layout.addWidget(features_lbl)

        layout.addWidget(features_frame)
        layout.addSpacing(6)

        philosophy = QLabel('💡 "VENI VIDI VICI"')
        philosophy.setStyleSheet(f"font-size: 10px; font-style: italic; color: {COLORS['text_subtle']};")
        philosophy.setAlignment(Qt.AlignCenter)
        layout.addWidget(philosophy)

        layout.addStretch()

        close_btn = QPushButton("Cerrar" if current_language == "es" else "Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(main_frame)

        self.exec()


def show_export_selection_dialog(parent, records):
    """Show dialog for exporting selected records"""
    if not records:
        QMessageBox.warning(parent, "Error", "No hay registros para exportar")
        return

    dialog = QDialog(parent)
    dialog.setWindowTitle("Exportar Selección")
    dialog.setFixedSize(400, 350)
    dialog.setModal(True)

    main_frame = QFrame()
    main_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {COLORS['surface']};
            border-radius: 16px;
        }}
    """)
    layout = QVBoxLayout(main_frame)
    layout.setContentsMargins(20, 20, 20, 20)

    title_label = QLabel(f"📤 Exportar {len(records)} elementos")
    title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_heading']};")
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)
    layout.addSpacing(20)

    csv_btn = QPushButton("Exportar a CSV")
    csv_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
    """)
    csv_btn.clicked.connect(lambda: _export_and_close(dialog, records, "csv", parent))
    layout.addWidget(csv_btn)

    json_btn = QPushButton("Exportar a JSON")
    json_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
    """)
    json_btn.clicked.connect(lambda: _export_and_close(dialog, records, "json", parent))
    layout.addWidget(json_btn)

    layout.addSpacing(15)

    cancel_btn = QPushButton("Cancelar")
    cancel_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLORS['gray']};
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px;
            font-size: 12px;
        }}
        QPushButton:hover {{ background-color: {COLORS['gray_hover']}; }}
    """)
    cancel_btn.clicked.connect(dialog.reject)
    layout.addWidget(cancel_btn)

    outer_layout = QVBoxLayout(dialog)
    outer_layout.setContentsMargins(0, 0, 0, 0)
    outer_layout.addWidget(main_frame)

    dialog.exec()


def _export_and_close(dialog, records, export_type, parent):
    """Helper function to export and close dialog"""
    try:
        filepath = None
        if export_type == "csv":
            filepath = exports_module.export_to_csv(records, "seleccion")
        elif export_type == "json":
            filepath = exports_module.export_to_json(records, "seleccion")

        if filepath:
            dialog.accept()
            reply = QMessageBox.question(
                parent, "Exportación Exitosa",
                f"Archivo exportado: {os.path.basename(filepath)}\n\n¿Desea abrir la carpeta?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if os.name == 'nt':
                    os.startfile(os.path.dirname(filepath))
                elif os.name == 'posix':
                    os.system(f'open "{os.path.dirname(filepath)}"' if sys.platform == 'darwin' else f'xdg-open "{os.path.dirname(filepath)}"')

    except Exception as e:
        logger.exception(f"Error exporting {export_type}")
        QMessageBox.critical(dialog, "Error", f"Error exportando {export_type.upper()}: {e}")


import exports as exports_module
from PySide6.QtWidgets import QMessageBox

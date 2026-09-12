"""
Módulo: gui.py
Interfaz gráfica principal usando PySide6 (Qt)
Diseño inspirado en IP-Analyzer: Tailwind blue palette, KPI cards, dark log console
"""
import sys
import os
import re
import logging
import threading
import webbrowser

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QGroupBox, QLabel, QLineEdit, QPushButton,
    QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSplitter, QTextEdit,
    QMenu, QMessageBox, QDialog, QStatusBar
)
from PySide6.QtCore import (
    Qt, QThread, QObject, Signal, Slot, QTimer
)
from PySide6.QtGui import (
    QFont, QColor, QAction, QIcon
)

try:
    import qtawesome as qta
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False
    print("ADVERTENCIA: qtawesome no instalado. Los iconos no estarán disponibles.")

from config import get_stored_api_key, save_stored_api_key
from i18n import LANGUAGES, t
from api import check_intelx, get_api_credits, MEDIA_TYPE_MAP
from utils import open_in_browser, load_history, save_history, merge_records
import exports as exports_module

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(threadName)-15s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Tailwind Blue Color Palette (matching IP-Analyzer) ---
COLORS = {
    "bg_main": "#F8FAFC",
    "surface": "#FFFFFF",
    "border": "#E2E8F0",
    "border_hover": "#CBD5E1",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_light": "#DBEAFE",
    "primary_text": "#1E3A8A",
    "text_heading": "#0F172A",
    "text_body": "#334155",
    "text_muted": "#475569",
    "text_subtle": "#64748B",
    "text_disabled": "#94A3B8",
    "success_bg": "#DCFCE7",
    "success_text": "#166534",
    "warning_bg": "#FEF9C3",
    "warning_text": "#854D0E",
    "error_bg": "#FEE2E2",
    "error_text": "#991B1B",
    "private_bg": "#E0E7FF",
    "private_text": "#3730A3",
    "log_bg": "#0F172A",
    "log_text": "#F8FAFC",
    "log_warning": "#FBBF24",
    "log_error": "#F87171",
    "log_debug": "#94A3B8",
    "progress_bg": "#F1F5F9",
    "progress_chunk": "#3B82F6",
    "table_header_bg": "#F1F5F9",
    "table_alt_row": "#F8FAFC",
    "table_selection_bg": "#DBEAFE",
    "table_selection_text": "#1E3A8A",
}

# --- Icon initialization ---
ICONS = {}

def init_icons():
    """Initialize qtawesome icons. Call after QApplication construction."""
    global ICONS
    if not ICONS_AVAILABLE:
        return
    icon_color = "#475569"
    icon_blue = "#3B82F6"
    white = "#FFFFFF"
    ICONS = {
        'search': qta.icon('fa5s.search', color=white),
        'times': qta.icon('fa5s.times', color=white),
        'key': qta.icon('fa5s.key', color=icon_color),
        'key_blue': qta.icon('fa5s.key', color=icon_blue),
        'globe': qta.icon('fa5s.globe', color=icon_blue),
        'building': qta.icon('fa5s.building', color=icon_blue),
        'lock': qta.icon('fa5s.lock', color=icon_blue),
        'database': qta.icon('fa5s.database', color=icon_blue),
        'file_export': qta.icon('fa5s.file-export', color=icon_color),
        'clipboard': qta.icon('fa5s.clipboard-list', color=icon_color),
        'info': qta.icon('fa5s.info-circle', color=icon_color),
        'sync': qta.icon('fa5s.sync', color=icon_color),
        'folder_open': qta.icon('fa5s.folder-open', color=icon_blue),
        'file': qta.icon('fa5s.file', color=icon_blue),
        'check': qta.icon('fa5s.check-circle', color='#22c55e'),
        'exclamation': qta.icon('fa5s.exclamation-triangle', color='#f59e0b'),
        'play': qta.icon('fa5s.play', color=white),
        'stop': qta.icon('fa5s.stop', color=white),
        'trash': qta.icon('fa5s.trash', color=icon_color),
        'copy': qta.icon('fa5s.copy', color=icon_color),
        'eye': qta.icon('fa5s.eye', color=icon_color),
        'sign_out': qta.icon('fa5s.sign-out-alt', color=icon_color),
    }


# --- Qt Log Handler ---
class QtLogHandler(QObject, logging.Handler):
    """Routes Python logging records to the Qt log console via signal."""
    log_message = Signal(str, str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname
            self.log_message.emit(msg, level)
        except Exception:
            pass


# --- Analysis Worker Thread ---
class AnalysisWorker(QObject):
    """Worker thread for IntelX API searches."""
    progress_updated = Signal(int, str)
    log_emitted = Signal(str, str)
    finished = Signal(bool, object, str)
    search_completed = Signal(list)

    def __init__(self, term, api_key, cancel_event=None):
        super().__init__()
        self.term = term
        self.api_key = api_key
        self.cancel_event = cancel_event or threading.Event()

    @Slot()
    def run(self):
        try:
            self.progress_updated.emit(10, "Preparando...")
            self.log_emitted.emit(f"Iniciando búsqueda para: {self.term}", "INFO")

            self.progress_updated.emit(30, "Conectando...")
            success, data_or_error, search_id = check_intelx(
                self.term, self.api_key, cancel_event=self.cancel_event
            )

            self.progress_updated.emit(70, "Procesando...")

            if success:
                new_records = []
                if isinstance(data_or_error, dict) and 'records' in data_or_error:
                    new_records = data_or_error['records']
                elif isinstance(data_or_error, list):
                    new_records = data_or_error
                elif isinstance(data_or_error, dict):
                    new_records = [data_or_error]

                self.log_emitted.emit(f"Registros obtenidos: {len(new_records)}", "INFO")
                self.progress_updated.emit(100, "Completado")
                self.finished.emit(True, new_records, search_id)
            else:
                error_msg = data_or_error if isinstance(data_or_error, str) else "Error en la búsqueda"
                self.log_emitted.emit(f"Error: {error_msg}", "ERROR")
                self.progress_updated.emit(0, "Error")
                self.finished.emit(False, error_msg, "")

        except Exception as e:
            logger.exception("Error en worker de búsqueda")
            self.log_emitted.emit(f"Excepción: {str(e)}", "CRITICAL")
            self.progress_updated.emit(0, "Error")
            self.finished.emit(False, str(e), "")


# --- StatCard Widget ---
class StatCard(QFrame):
    """Dashboard KPI card widget matching IP-Analyzer style."""
    def __init__(self, title, value="0", icon=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        icon_lbl = QLabel()
        if icon:
            icon_lbl.setPixmap(icon.pixmap(28, 28))
        layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_heading']};")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {COLORS['text_subtle']}; text-transform: uppercase;")

        text_layout.addWidget(self.val_lbl)
        text_layout.addWidget(title_lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, value):
        self.val_lbl.setText(str(value))


# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IntelX Checker V2")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1100, 700)

        self.current_language = "es"
        self.app_version = "2.0.0"
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '.env')

        # State
        self.current_records = load_history()
        self.credits = 0
        self.api_key = ''
        self.search_thread = None
        self.worker = None
        self.stop_search = False
        self.cancel_event = None
        self.preview_windows = {}

        # Setup
        self._init_icons_safe()
        self._setup_ui()
        self._setup_menu()
        self._setup_log_handler()
        self._apply_styles()
        self._load_api_config()
        self._update_language()

        if self.current_records:
            QTimer.singleShot(100, self._populate_results)

    def _init_icons_safe(self):
        try:
            init_icons()
        except Exception as e:
            logger.debug(f"Error initializing icons: {e}")

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_main']};
            }}
            #HeaderFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            #SearchFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            #FilterFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            #ResultsFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 6px;
                background-color: {COLORS['surface']};
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: {COLORS['primary']};
            }}
            QTableWidget {{
                gridline-color: {COLORS['border']};
                background-color: {COLORS['surface']};
                alternate-background-color: {COLORS['table_alt_row']};
                selection-background-color: {COLORS['table_selection_bg']};
                selection-color: {COLORS['table_selection_text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 4px 6px;
                color: {COLORS['text_heading']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['table_header_bg']};
                color: {COLORS['text_body']};
                font-weight: bold;
                font-size: 12px;
                padding: 6px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['border_hover']};
            }}
            QLineEdit {{
                border: 1px solid {COLORS['border_hover']};
                border-radius: 6px;
                padding: 5px 10px;
                background-color: {COLORS['surface']};
                color: {COLORS['text_heading']};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox {{
                border: 1px solid {COLORS['border_hover']};
                border-radius: 6px;
                padding: 5px 10px;
                background-color: {COLORS['surface']};
                color: {COLORS['text_heading']};
                font-size: 12px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_heading']};
                selection-background-color: {COLORS['table_selection_bg']};
                selection-color: {COLORS['table_selection_text']};
                border: 1px solid {COLORS['border_hover']};
                padding: 4px;
            }}
            QPushButton {{
                border: 1px solid {COLORS['border_hover']};
                border-radius: 6px;
                padding: 6px 14px;
                background-color: {COLORS['surface']};
                color: {COLORS['text_body']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['progress_bg']};
                border-color: {COLORS['text_disabled']};
            }}
            QPushButton#primaryBtn {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton#primaryBtn:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton#dangerBtn {{
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton#dangerBtn:hover {{
                background-color: #DC2626;
            }}
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 7px;
                background-color: {COLORS['progress_bg']};
                text-align: center;
                font-size: 10px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['progress_chunk']};
                border-radius: 6px;
            }}
            QMessageBox {{
                background-color: {COLORS['surface']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['text_heading']};
                font-size: 12px;
            }}
            QMessageBox QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 60px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # --- Header ---
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 6, 10, 6)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        title_lbl = QLabel(f"IntelX Checker V{self.app_version}")
        title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['text_heading']};")
        sub_lbl = QLabel("Herramienta de Inteligencia y Fugas de Datos")
        sub_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_subtle']};")
        brand_layout.addWidget(title_lbl)
        brand_layout.addWidget(sub_lbl)
        header_layout.addLayout(brand_layout)

        header_layout.addStretch()

        self.token_status_lbl = QLabel()
        self.token_status_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 10px;")
        header_layout.addWidget(self.token_status_lbl)

        self.btn_manage_token = QPushButton(" Gestionar Token")
        if ICONS_AVAILABLE:
            self.btn_manage_token.setIcon(ICONS.get('key', QIcon()))
        self.btn_manage_token.setFixedHeight(28)
        self.btn_manage_token.clicked.connect(self.manage_api_key)
        header_layout.addWidget(self.btn_manage_token)

        main_layout.addWidget(header_frame)

        # --- Search Card ---
        search_frame = QFrame()
        search_frame.setObjectName("SearchFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 8, 10, 8)

        self.search_label = QLabel("Correo o Dominio:")
        self.search_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['text_heading']};")
        search_layout.addWidget(self.search_label)

        self.term_entry = QLineEdit()
        self.term_entry.setPlaceholderText("🔍  Buscar email o dominio...")
        self.term_entry.setFixedHeight(40)
        self.term_entry.returnPressed.connect(self.search_intelx)
        search_layout.addWidget(self.term_entry, stretch=1)

        self.search_button = QPushButton("🔍  Buscar")
        self.search_button.setObjectName("primaryBtn")
        self.search_button.setFixedWidth(150)
        self.search_button.setFixedHeight(40)
        self.search_button.clicked.connect(self.search_intelx)
        search_layout.addWidget(self.search_button)

        self.cancel_button = QPushButton("✕  Cancelar")
        self.cancel_button.setObjectName("dangerBtn")
        self.cancel_button.setFixedWidth(150)
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_search)
        search_layout.addWidget(self.cancel_button)

        main_layout.addWidget(search_frame)

        # --- Filter Bar ---
        filter_frame = QFrame()
        filter_frame.setObjectName("FilterFrame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 4, 10, 4)

        self.filter_entry = QLineEdit()
        self.filter_entry.setPlaceholderText("🔎  Filtrar resultados...")
        self.filter_entry.setFixedHeight(34)
        self.filter_entry.textChanged.connect(self.filter_results)
        filter_layout.addWidget(self.filter_entry, stretch=1)

        self.credits_label = QLabel("Créditos: 0")
        self.credits_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['primary']};")
        filter_layout.addWidget(self.credits_label)

        main_layout.addWidget(filter_frame)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(12)
        main_layout.addWidget(self.progress_bar)

        # --- KPI Stats Cards ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(6)
        self.card_total = StatCard("Total Resultados", "0", ICONS.get('globe'))
        self.card_sources = StatCard("Fuentes Únicas", "0", ICONS.get('building'))
        self.card_types = StatCard("Tipos de Contenido", "0", ICONS.get('database'))
        self.card_score = StatCard("Puntuación Promedio", "0", ICONS.get('lock'))
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_sources)
        stats_layout.addWidget(self.card_types)
        stats_layout.addWidget(self.card_score)
        main_layout.addLayout(stats_layout)

        # --- Splitter (Table + Log) ---
        self.splitter = QSplitter(Qt.Vertical)

        # Results Table
        results_widget = QWidget()
        res_vbox = QVBoxLayout(results_widget)
        res_vbox.setContentsMargins(0, 0, 0, 0)
        res_vbox.setSpacing(4)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Nombre", "IP", "Tipo", "Media",
            "Fuente", "Tamaño", "Puntuación", "ID Sistema"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.on_item_double_click)

        header = self.table.horizontalHeader()
        header.resizeSection(0, 130)
        header.resizeSection(1, 200)
        header.resizeSection(2, 120)
        header.resizeSection(3, 100)
        header.resizeSection(4, 100)
        header.resizeSection(5, 120)
        header.resizeSection(6, 80)
        header.resizeSection(7, 80)
        header.resizeSection(8, 180)

        res_vbox.addWidget(self.table)
        self.splitter.addWidget(results_widget)

        # Log Console
        self.log_widget = QGroupBox(" Log de Ejecucion del Sistema")
        log_vbox = QVBoxLayout(self.log_widget)
        log_vbox.setContentsMargins(4, 4, 4, 4)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            f"font-family: 'Cascadia Code', 'Consolas', monospace; "
            f"font-size: 11px; background-color: {COLORS['log_bg']}; "
            f"color: {COLORS['log_text']};"
        )
        log_vbox.addWidget(self.log_text)
        self.splitter.addWidget(self.log_widget)
        self.log_widget.setVisible(False)
        self.splitter.setSizes([700, 120])

        main_layout.addWidget(self.splitter, stretch=1)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Listo.")
        self.status_bar.addWidget(self.status_label)

        self.progress_label = QLabel("")
        self.status_bar.addPermanentWidget(self.progress_label)

    def _setup_menu(self):
        menu_bar = self.menuBar()

        # Archivo
        file_menu = menu_bar.addMenu("&Archivo")

        action_csv = QAction("Exportar a CSV...", self)
        if ICONS_AVAILABLE:
            action_csv.setIcon(ICONS.get('file_export', QIcon()))
        action_csv.triggered.connect(self.export_to_csv_safe)
        file_menu.addAction(action_csv)

        action_json = QAction("Exportar a JSON...", self)
        if ICONS_AVAILABLE:
            action_json.setIcon(ICONS.get('file_export', QIcon()))
        action_json.triggered.connect(self.export_to_json_safe)
        file_menu.addAction(action_json)

        action_pdf = QAction("Exportar a PDF...", self)
        if ICONS_AVAILABLE:
            action_pdf.setIcon(ICONS.get('file_export', QIcon()))
        action_pdf.triggered.connect(self.export_to_pdf_safe)
        file_menu.addAction(action_pdf)

        action_html = QAction("Exportar a HTML...", self)
        if ICONS_AVAILABLE:
            action_html.setIcon(ICONS.get('file_export', QIcon()))
        action_html.triggered.connect(self.export_to_html_safe)
        file_menu.addAction(action_html)

        file_menu.addSeparator()

        action_clear = QAction("Limpiar Historial", self)
        if ICONS_AVAILABLE:
            action_clear.setIcon(ICONS.get('trash', QIcon()))
        action_clear.triggered.connect(self._clear_history)
        file_menu.addAction(action_clear)

        file_menu.addSeparator()

        action_exit = QAction("Salir", self)
        if ICONS_AVAILABLE:
            action_exit.setIcon(ICONS.get('sign_out', QIcon()))
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        # Ver
        view_menu = menu_bar.addMenu("&Ver")
        self.action_toggle_log = QAction("Log de Ejecucion", self, checkable=True)
        if ICONS_AVAILABLE:
            self.action_toggle_log.setIcon(ICONS.get('clipboard', QIcon()))
        self.action_toggle_log.toggled.connect(self._toggle_log)
        view_menu.addAction(self.action_toggle_log)

        view_menu.addSeparator()

        action_lang_es = QAction("Español", self)
        action_lang_es.triggered.connect(lambda: self._set_language("es"))
        view_menu.addAction(action_lang_es)

        action_lang_en = QAction("English", self)
        action_lang_en.triggered.connect(lambda: self._set_language("en"))
        view_menu.addAction(action_lang_en)

        # Ayuda
        help_menu = menu_bar.addMenu("&Ayuda")

        action_refresh = QAction("Refrescar Créditos", self)
        if ICONS_AVAILABLE:
            action_refresh.setIcon(ICONS.get('sync', QIcon()))
        action_refresh.triggered.connect(self.refresh_credits)
        help_menu.addAction(action_refresh)

        action_get_key = QAction("Obtener Clave API", self)
        if ICONS_AVAILABLE:
            action_get_key.setIcon(ICONS.get('key', QIcon()))
        action_get_key.triggered.connect(self.open_intelx_api_page)
        help_menu.addAction(action_get_key)

        help_menu.addSeparator()

        action_about = QAction("Acerca de", self)
        if ICONS_AVAILABLE:
            action_about.setIcon(ICONS.get('info', QIcon()))
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def _setup_log_handler(self):
        self.log_handler = QtLogHandler()
        self.log_handler.log_message.connect(self._append_log)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.log_handler)

    @Slot(str, str)
    def _append_log(self, msg, level):
        color = COLORS['log_text']
        if level == "WARNING":
            color = COLORS['log_warning']
        elif level in ("ERROR", "CRITICAL"):
            color = COLORS['log_error']
        elif level == "DEBUG":
            color = COLORS['log_debug']
        self.log_text.append(f'<font color="{color}">{msg}</font>')

    def _toggle_log(self, checked):
        self.log_widget.setVisible(checked)

    def _update_token_status(self):
        if self.api_key:
            self.token_status_lbl.setText("Token API Activo")
            self.token_status_lbl.setStyleSheet(
                f"font-size: 11px; font-weight: 600; padding: 3px 8px; "
                f"border-radius: 10px; background-color: {COLORS['success_bg']}; "
                f"color: {COLORS['success_text']};"
            )
        else:
            self.token_status_lbl.setText("Sin Token (Modo Local)")
            self.token_status_lbl.setStyleSheet(
                f"font-size: 11px; font-weight: 600; padding: 3px 8px; "
                f"border-radius: 10px; background-color: {COLORS['warning_bg']}; "
                f"color: {COLORS['warning_text']};"
            )

    def _update_kpi_cards(self):
        total = len(self.current_records)
        sources = set()
        types = set()
        scores = []

        for record in self.current_records:
            if isinstance(record, dict):
                bucket = record.get('bucket', record.get('bucketh', ''))
                if bucket:
                    sources.add(bucket)
                media = record.get('media', 0)
                types.add(str(media))
                score = record.get('xscore', 0)
                if score and score > 0:
                    scores.append(score)

        avg_score = f"{sum(scores) / len(scores):.1f}" if scores else "0"

        self.card_total.set_value(str(total))
        self.card_sources.set_value(str(len(sources)))
        self.card_types.set_value(str(len(types)))
        self.card_score.set_value(avg_score)

    # --- Language & Theme ---
    def _set_language(self, lang):
        self.current_language = lang
        try:
            from dotenv import set_key
            set_key(self.config_file, 'LANGUAGE', lang)
        except Exception:
            pass
        self._update_language()

    def _update_language(self):
        lang = self.current_language
        self.search_label.setText(t("Correo o Dominio", lang))
        self.search_button.setText(t("Buscar", lang))
        self.cancel_button.setText(t("Cancelar", lang))
        self.filter_entry.setPlaceholderText(t("Filtrar resultados", lang))
        self.credits_label.setText(f"{t('Créditos', lang)} {self.credits}")
        self.status_label.setText(t("Listo", lang))

        headers = [
            t("Fecha", lang), t("Nombre", lang), "IP",
            t("Tipo", lang), t("Media", lang), t("Fuente", lang),
            t("Tamaño", lang), t("Puntuación", lang), t("ID Sistema", lang)
        ]
        self.table.setHorizontalHeaderLabels(headers)

    # --- API Config ---
    def _load_api_config(self):
        try:
            self.api_key = get_stored_api_key()
            self._update_token_status()
            if self.api_key:
                self.refresh_credits()
        except Exception:
            self.api_key = ''
            self._update_token_status()

    def manage_api_key(self):
        from ui_components import ApiKeyDialog
        dialog = ApiKeyDialog(self, self.api_key)
        new_key = dialog.get_result()
        if new_key is not None:
            self.api_key = new_key
            try:
                save_stored_api_key(self.api_key, self.config_file)
                self._update_token_status()
                if self.api_key:
                    self.refresh_credits()
            except Exception as e:
                logger.exception("Error guardando API key")

    def open_intelx_api_page(self):
        webbrowser.open("https://intelx.io/account?tab=developer")

    def refresh_credits(self):
        if not self.api_key:
            return
        try:
            success, credits_or_error = get_api_credits(self.api_key)
            if success:
                self.credits = credits_or_error
                lang = self.current_language
                self.credits_label.setText(f"{t('Créditos', lang)} {self.credits}")
            else:
                self.credits_label.setText(f"{t('Créditos', self.current_language)} Error")
        except Exception as e:
            logger.exception("Error obteniendo créditos")
            self.credits_label.setText(f"{t('Créditos', self.current_language)} Error")

    def show_about(self):
        from ui_components import AboutDialog
        AboutDialog(self, self.app_version, self.current_language)

    # --- Search ---
    def search_intelx(self):
        term = self.term_entry.text().strip()
        if not term:
            QMessageBox.warning(self, "Error", t("Ingrese un término de búsqueda", self.current_language))
            return
        if not self.api_key:
            QMessageBox.warning(self, "Error", t("Configure su clave API primero", self.current_language))
            self.manage_api_key()
            return

        self.refresh_credits()
        self._existing_count_before_search = len(self.current_records)
        self.stop_search = False
        self.cancel_event = threading.Event()

        self.search_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(10)
        self.progress_label.setText("Preparando...")
        self.status_label.setText(t("Iniciando búsqueda...", self.current_language))

        self.worker = AnalysisWorker(term, self.api_key, self.cancel_event)
        self.search_thread = QThread()
        self.worker.moveToThread(self.search_thread)

        self.worker.progress_updated.connect(self._on_worker_progress)
        self.worker.log_emitted.connect(self._append_log)
        self.worker.finished.connect(self._on_search_finished)

        self.search_thread.started.connect(self.worker.run)
        self.search_thread.start()

    @Slot(int, str)
    def _on_worker_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.progress_label.setText(msg)

    @Slot(bool, object, str)
    def _on_search_finished(self, success, data, search_id):
        if success:
            new_records = data if isinstance(data, list) else []
            self.current_records = merge_records(self.current_records, new_records)
            save_history(self.current_records)
            self.progress_bar.setValue(100)
            self.progress_label.setText(t("Completado", self.current_language))
            self.status_label.setText(
                f"{t('Resultados', self.current_language)}: {len(self.current_records)} registros"
            )
            self._populate_results()
            self._update_kpi_cards()
        else:
            error_msg = data if isinstance(data, str) else "Error"
            self.status_label.setText(error_msg)
            self.progress_bar.setValue(0)
            self.progress_label.setText(t("Error", self.current_language))

        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QTimer.singleShot(2000, lambda: self.progress_bar.setValue(0))
        QTimer.singleShot(2000, lambda: self.progress_label.setText(""))
        QTimer.singleShot(1000, self.refresh_credits)

        self.search_thread.quit()
        self.search_thread.wait()

    def cancel_search(self):
        self.stop_search = True
        if self.cancel_event:
            self.cancel_event.set()
        self.status_label.setText(t("Búsqueda cancelada", self.current_language))
        self.progress_label.setText(t("Cancelado", self.current_language))
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    # --- Populate Table ---
    def _populate_results(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for i, record in enumerate(self.current_records):
            if self.stop_search:
                break

            if isinstance(record, str):
                record_dict = {
                    'name': f'Resultado {i+1}', 'type': 1, 'media': 1,
                    'bucket': 'unknown', 'size': len(record), 'date': '',
                    'xscore': 0, 'systemid': f'record_{i}', 'data': record
                }
            elif isinstance(record, dict):
                record_dict = record
            else:
                record_dict = {
                    'name': f'Resultado {i+1}', 'type': 0, 'media': 0,
                    'bucket': 'unknown', 'size': 0, 'date': '',
                    'xscore': 0, 'systemid': f'record_{i}', 'data': str(record)
                }

            date_str = record_dict.get('date', '')
            date_text = date_str[:19] if date_str and len(date_str) > 19 else (date_str or 'N/A')

            name = record_dict.get('name', f'Documento {i+1}')
            name = name[:60] + "..." if len(name) > 60 else name

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

            row = self.table.rowCount()
            self.table.insertRow(row)

            items = [date_text, name, ip_address, type_text, media_text,
                     bucket_text, size_text, score_text, system_id]

            for col, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 2:  # IP column - monospace bold
                    item.setFont(QFont("Consolas", 10, QFont.Bold))
                self.table.setItem(row, col, item)

            # Color-code ISP column (col 5) based on content
            isp_item = self.table.item(row, 5)
            if isp_item:
                isp_text = str(bucket_text).lower()
                if 'error' in isp_text or 'red privada' in isp_text or 'private' in isp_text:
                    isp_item.setBackground(QColor(COLORS['private_bg']))
                    isp_item.setForeground(QColor(COLORS['private_text']))
                elif 'error' in isp_text:
                    isp_item.setBackground(QColor(COLORS['error_bg']))
                    isp_item.setForeground(QColor(COLORS['error_text']))

        self.table.setSortingEnabled(True)

    def _extract_ip_address(self, record_dict):
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        search_fields = [
            record_dict.get('name', ''),
            record_dict.get('data', ''),
            str(record_dict)
        ]
        for field in search_fields:
            if field:
                ipv4_match = re.search(ipv4_pattern, field)
                if ipv4_match:
                    return ipv4_match.group()
                ipv6_match = re.search(ipv6_pattern, field)
                if ipv6_match:
                    return ipv6_match.group()
        return 'N/A'

    def _get_type_description(self, type_val):
        try:
            if isinstance(type_val, str):
                try:
                    type_val = int(type_val)
                except ValueError:
                    return "Tipo Desconocido"
            type_descriptions = {
                0: "Binario", 1: "Texto", 2: "Imagen", 3: "Video",
                4: "Audio", 5: "Documento", 6: "Ejecutable", 7: "Contenedor",
                1001: "Usuario", 1002: "Filtración", 1004: "URL", 1005: "Foro"
            }
            return type_descriptions.get(type_val, f"Tipo ({type_val})")
        except Exception:
            return "Error"

    def _get_media_description(self, media_val):
        try:
            if isinstance(media_val, str):
                try:
                    media_val = int(media_val)
                except ValueError:
                    return "Media Desconocido"
            return MEDIA_TYPE_MAP.get(media_val, f"Media ({media_val})")
        except Exception:
            return "Error"

    def _format_file_size(self, size):
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

    # --- Filter ---
    def filter_results(self, text):
        filter_text = text.lower() if text else ""
        for row in range(self.table.rowCount()):
            show = True
            if filter_text:
                show = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and filter_text in item.text().lower():
                        show = True
                        break
            self.table.setRowHidden(row, not show)

    # --- Sort ---
    # Sorting is handled natively by QTableWidget with setSortingEnabled(True)

    # --- Table Events ---
    def on_item_double_click(self, index):
        self.preview_selected()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        action_preview = menu.addAction("Vista Previa")
        menu.addSeparator()
        action_select_all = menu.addAction("Seleccionar Todo")
        action_deselect = menu.addAction("Deseleccionar")
        menu.addSeparator()
        action_copy = menu.addAction("Copiar")
        action_export = menu.addAction("Exportar Selección")

        action_preview.triggered.connect(self.preview_selected)
        action_select_all.triggered.connect(self.select_all)
        action_deselect.triggered.connect(self.deselect_all)
        action_copy.triggered.connect(self.copy_selected)
        action_export.triggered.connect(self.export_selection)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def preview_selected(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return
        row = selection[0].row()
        system_id = self.table.item(row, 8).text()
        record = self._find_record_by_id(system_id)
        if record:
            from ui_components import PreviewWindow
            PreviewWindow(self, record)

    def _find_record_by_id(self, record_id):
        for i, record in enumerate(self.current_records):
            if isinstance(record, dict):
                if (record.get('systemid') == record_id or
                    record.get('storageid') == record_id):
                    return record
            elif isinstance(record, str):
                if f'record_{i}' == record_id:
                    return {
                        'name': f'Resultado {i+1}', 'type': 1, 'media': 1,
                        'bucket': 'unknown', 'size': len(record), 'date': '',
                        'xscore': 0, 'systemid': f'record_{i}', 'data': record
                    }
        return None

    def select_all(self):
        self.table.selectAll()

    def deselect_all(self):
        self.table.clearSelection()

    def copy_selected(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return
        lines = []
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        lines.append('\t'.join(headers))
        for idx in selection:
            row = idx.row()
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            lines.append('\t'.join(row_data))
        QApplication.clipboard().setText('\n'.join(lines))

    def export_selection(self):
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            QMessageBox.warning(self, "Error", t("No hay elementos seleccionados", self.current_language))
            return
        selected_records = []
        for idx in selection:
            row = idx.row()
            system_id = self.table.item(row, 8).text()
            record = self._find_record_by_id(system_id)
            if record:
                selected_records.append(record)
        if selected_records:
            from ui_components import show_export_selection_dialog
            show_export_selection_dialog(self, selected_records)

    # --- History ---
    def _clear_history(self):
        reply = QMessageBox.question(
            self, "Limpiar Historial",
            "¿Está seguro de que desea eliminar todo el historial de resultados? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.current_records = []
            save_history([])
            self.table.setRowCount(0)
            self._update_kpi_cards()
            self.status_label.setText(t("Historial limpiado", self.current_language))

    # --- Export Methods ---
    def export_to_csv_safe(self):
        try:
            if not self.current_records:
                QMessageBox.warning(self, "Sin Datos", t("No hay resultados para exportar", self.current_language))
                return
            search_term = self.term_entry.text().strip() or 'IntelX_Export'
            filepath = exports_module.export_to_csv(self.current_records, search_term)
            if filepath:
                reply = QMessageBox.question(
                    self, "Exportación Exitosa",
                    f"Archivo exportado: {os.path.basename(filepath)}\n\n¿Desea abrir la carpeta?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    os.startfile(os.path.dirname(filepath))
        except Exception as e:
            logger.exception('Error exporting CSV')
            QMessageBox.critical(self, 'Error', f'Error exportando CSV: {e}')

    def export_to_json_safe(self):
        try:
            if not self.current_records:
                QMessageBox.warning(self, "Sin Datos", t("No hay resultados para exportar", self.current_language))
                return
            search_term = self.term_entry.text().strip() or 'IntelX_Export'
            filepath = exports_module.export_to_json(self.current_records, search_term)
            if filepath:
                reply = QMessageBox.question(
                    self, "Exportación Exitosa",
                    f"Archivo exportado: {os.path.basename(filepath)}\n\n¿Desea abrir la carpeta?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    os.startfile(os.path.dirname(filepath))
        except Exception as e:
            logger.exception('Error exporting JSON')
            QMessageBox.critical(self, 'Error', f'Error exportando JSON: {e}')

    def export_to_pdf_safe(self):
        try:
            if not self.current_records:
                QMessageBox.warning(self, "Sin Datos", t("No hay resultados para exportar", self.current_language))
                return
            search_term = self.term_entry.text().strip() or 'IntelX Export'
            filepath = exports_module.generate_pdf_report(self.current_records, title=search_term)
            if filepath:
                reply = QMessageBox.question(
                    self, "Exportación Exitosa",
                    f"Archivo exportado: {os.path.basename(filepath)}\n\n¿Desea abrir la carpeta?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    os.startfile(os.path.dirname(filepath))
        except Exception as e:
            logger.exception('Error exporting PDF')
            QMessageBox.critical(self, 'Error', f'Error exportando PDF: {e}')

    def export_to_html_safe(self):
        try:
            if not self.current_records:
                QMessageBox.warning(self, "Sin Datos", t("No hay resultados para exportar", self.current_language))
                return
            search_term = self.term_entry.text().strip() or "búsqueda_sin_nombre"
            from exports import export_to_interactive_html
            filepath = export_to_interactive_html(
                records=self.current_records,
                search_term=search_term,
                app_version="2.0.0"
            )
            if filepath:
                reply = QMessageBox.question(
                    self, "Reporte HTML Interactivo",
                    "¿Desea abrir el reporte interactivo en su navegador?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    open_in_browser(filepath)
        except Exception as e:
            logger.exception("Error generando reporte HTML interactivo")
            QMessageBox.critical(self, "Error", f"Error generando reporte: {e}")

    # --- Close ---
    def closeEvent(self, event):
        logger.info("Cerrando la aplicación...")
        if self.preview_windows:
            for sid in list(self.preview_windows.keys()):
                try:
                    w = self.preview_windows[sid]
                    if hasattr(w, 'close'):
                        w.close()
                except Exception:
                    pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    init_icons()
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

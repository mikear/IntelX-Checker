"""
Archivo principal: main.py
Punto de entrada de la aplicación
"""
import logging
import sys
from intelx.gui import IntelXCheckerApp

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("=============================================")
    logger.info("Iniciando la aplicación IntelX Checker...")
    logger.info(f"Python Versión: {sys.version}")
    logger.info(f"Plataforma: {sys.platform}")
    logger.info(f"Empaquetado (Frozen): {getattr(sys, 'frozen', False)}")
    app = IntelXCheckerApp()
    def on_closing():
        logger.info("Cerrando la aplicación...")
        open_previews = list(app.preview_windows.keys())
        if open_previews:
            logger.info(f"Cerrando {len(open_previews)} ventanas de preview abiertas...")
            for sid in open_previews:
                app._on_preview_close(sid)
        app.destroy()
        logger.info("Aplicación IntelX Checker cerrada.")
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

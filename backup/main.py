"""
Archivo principal: main.py
Punto de entrada de la aplicación
"""
import logging
import sys
from intelx.gui import IntelXCheckerApp

if __name__ == "__main__":
    # Configuración de logging para archivo y consola
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("intelx_checker.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("=============================================")
    logger.info("Iniciando la aplicación IntelX Checker...")
    logger.info(f"Python Versión: {sys.version}")
    logger.info(f"Plataforma: {sys.platform}")
    logger.info(f"Empaquetado (Frozen): {getattr(sys, 'frozen', False)}")
    try:
        app = IntelXCheckerApp()
        def on_closing():
            logger.info("Cerrando la aplicación...")
            # Check if preview_windows exists (for compatibility with full GUI)
            if hasattr(app, 'preview_windows'):
                open_previews = list(app.preview_windows.keys())
                if open_previews:
                    logger.info(f"Cerrando {len(open_previews)} ventanas de preview abiertas...")
                    for sid in open_previews:
                        if hasattr(app, '_on_preview_close'):
                            app._on_preview_close(sid)
            app.destroy()
            logger.info("Aplicación IntelX Checker cerrada.")
        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}", exc_info=True)
        import tkinter.messagebox as mb
        mb.showerror("Error Crítico", f"Ocurrió un error grave. Revisa el archivo intelx_checker.log para más detalles.\n\n{e}")

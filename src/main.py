"""
Archivo principal: main.py
Punto de entrada de la aplicación
"""
import argparse
import os
import sys
import logging
from config import get_stored_api_key
from api import check_intelx
from exports import export_to_csv, export_to_json, export_to_interactive_html, generate_pdf_report


def run_cli_mode(args) -> int:
    """Executes an IntelX search in CLI mode without launching the GUI."""
    logger = logging.getLogger("IntelX_CLI")
    print("=== IntelX Checker - CLI Mode ===")

    api_key = args.api_key or get_stored_api_key()
    if not api_key:
        print("❌ Error: No API key found. Provide it with --api-key or configure INTELX_API_KEY env/keyring.")
        return 1

    search_term = args.search
    print(f"🔍 Searching for: {search_term} ...")

    success, data_or_err, search_id = check_intelx(search_term, api_key)
    if not success:
        print(f"❌ Search failed: {data_or_err}")
        return 1

    records = data_or_err.get("records", []) if isinstance(data_or_err, dict) else []
    print(f"✅ Search completed! Records found: {len(records)}")

    if not records:
        print("ℹ️ No records to export.")
        return 0

    export_format = (args.export or "json").lower()
    out_dir = args.output_dir or os.path.join(os.getcwd(), "exports")
    os.makedirs(out_dir, exist_ok=True)

    try:
        if export_format == "csv":
            out_file = export_to_csv(records, exports_dir=out_dir)
        elif export_format == "html":
            out_file = export_to_interactive_html(records, exports_dir=out_dir, search_term=search_term)
        elif export_format == "pdf":
            out_file = generate_pdf_report(records, title=f"IntelX Export - {search_term}", exports_dir=out_dir)
        else:
            out_file = export_to_json(records, exports_dir=out_dir)

        print(f"💾 Report generated successfully: {out_file}")
        return 0
    except Exception as e:
        print(f"❌ Error exporting report: {e}")
        logger.exception("CLI Export error")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IntelX Checker - Data Leak & OSINT Intelligence Tool")
    parser.add_argument("--cli", action="store_true", help="Run in command line interface mode")
    parser.add_argument("-s", "--search", type=str, help="Search term (email or domain) for CLI mode")
    parser.add_argument("-e", "--export", type=str, choices=["json", "csv", "html", "pdf"], default="json", help="Export format in CLI mode")
    parser.add_argument("-o", "--output-dir", type=str, help="Directory to save exported results")
    parser.add_argument("-k", "--api-key", type=str, help="IntelX API Key (optional override)")

    args = parser.parse_args()
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
    if args.cli or args.search:
        if not args.search:
            print("❌ Error: --search parameter is required when running in CLI mode.")
            sys.exit(1)
        sys.exit(run_cli_mode(args))

    try:
        from gui import IntelXCheckerApp
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

"""
Módulo centralizado de logging para FACRET.
Proporciona loggers configurados con rotación de archivos y salida en consola.
"""
import logging
import logging.handlers
import os


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.

    Args:
        name: Nombre del módulo (típicamente __name__)

    Returns:
        logging.Logger configurado con archivo + consola

    Niveles:
        - DEBUG: Detalles para diagnóstico
        - INFO: Confirmación de progreso
        - WARNING: Algo inesperado (sin error)
        - ERROR: Falla en operación
        - CRITICAL: Falla grave
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Crear carpeta de logs si no existe
    logs_dir = os.path.join(os.path.dirname(__file__), "../../logs")
    os.makedirs(logs_dir, exist_ok=True)

    # ── Handler para archivo con rotación (máx 5MB, 10 backups) ────────────
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, "facret.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    # ── Handler para consola (solo INFO y superiores) ─────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # ── Formato consistente ───────────────────────────────────────────────
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Logger raíz de FACRET
root_logger = get_logger("facret")

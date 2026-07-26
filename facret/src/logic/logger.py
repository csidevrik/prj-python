# =============================
# logic/logger.py
# =============================
"""
Sistema centralizado de logging para FACRET.

Proporciona trazabilidad de errores, advertencias e información de la app.
Soporta:
  - Logs a archivo (facret.log)
  - Logs a consola con colores
  - Diferentes niveles (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Directorio de logs
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "facret.log"

# Crear directorio si no existe
LOG_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Formateador con colores para consola."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(level=logging.INFO):
    """
    Configura el sistema de logging para la app.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("facret")
    logger.setLevel(level)

    # Evitar handlers duplicados
    if logger.handlers:
        return logger

    # Formato de logs
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para archivo
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Mantener 5 backups
    )
    file_handler.setLevel(logging.DEBUG)  # Archivo siempre en DEBUG para máxima trazabilidad
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        "%(levelname)s | %(name)s | %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "facret") -> logging.Logger:
    """
    Obtiene un logger configurado.

    Args:
        name: Nombre del logger (típicamente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Inicializar logging al importar
logger = setup_logging()

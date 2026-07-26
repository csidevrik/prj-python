# =============================
# logic/folder_stats.py
# =============================
"""
Utilidad para calcular estadísticas de carpetas:
- Cantidad de archivos
- Cantidad de carpetas
- Tamaño total en MB
- Información formateada para UI
"""
from pathlib import Path
from typing import NamedTuple


class FolderStats(NamedTuple):
    """Estadísticas de una carpeta."""
    num_archivos: int
    num_carpetas: int
    tamanio_mb: float
    tamanio_str: str  # "123.45 MB" o "1.23 GB"


def get_folder_stats(folder_path: str | Path) -> FolderStats | None:
    """
    Calcula estadísticas de una carpeta.

    Args:
        folder_path: Ruta de la carpeta

    Returns:
        FolderStats con estadísticas, o None si la carpeta no existe o hay error
    """
    try:
        path = Path(folder_path)

        if not path.exists():
            return None
        if not path.is_dir():
            return None

        num_archivos = 0
        num_carpetas = 0
        tamanio_bytes = 0

        # Recorrer recursivamente la carpeta
        for item in path.rglob("*"):
            if item.is_file():
                num_archivos += 1
                try:
                    tamanio_bytes += item.stat().st_size
                except (OSError, PermissionError):
                    pass
            elif item.is_dir():
                num_carpetas += 1

        # Convertir bytes a MB
        tamanio_mb = tamanio_bytes / (1024 * 1024)

        # Formatear según el tamaño
        if tamanio_mb >= 1024:
            tamanio_str = f"{tamanio_mb / 1024:.2f} GB"
        else:
            tamanio_str = f"{tamanio_mb:.2f} MB"

        return FolderStats(
            num_archivos=num_archivos,
            num_carpetas=num_carpetas,
            tamanio_mb=tamanio_mb,
            tamanio_str=tamanio_str,
        )

    except Exception as e:
        print(f"Error al obtener estadísticas de {folder_path}: {e}")
        return None

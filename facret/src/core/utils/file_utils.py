import os
import shutil
from pathlib import Path
from typing import List, Optional

class FileUtils:
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """Asegurar que un directorio existe"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """Copiar archivo"""
        try:
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """Mover archivo"""
        try:
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Error moving file from {source} to {destination}: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Eliminar archivo"""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_size_formatted(size_bytes: int) -> str:
        """Formatear tamaño de archivo"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
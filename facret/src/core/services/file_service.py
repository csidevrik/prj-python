import os
import pathlib
from typing import List, Optional
from ..models.file_model import FileModel

class FileService:
    def __init__(self):
        self.work_directory = ""
        
    def set_work_directory(self, directory: str):
        """Establecer directorio de trabajo"""
        if os.path.exists(directory):
            self.work_directory = directory
            return True
        return False
    
    def get_xml_files(self, directory: Optional[str] = None) -> List[FileModel]:
        """Obtener lista de archivos XML"""
        target_dir = directory or self.work_directory
        if not target_dir or not os.path.exists(target_dir):
            return []
        
        xml_files = []
        for file_path in pathlib.Path(target_dir).glob("*.xml"):
            if file_path.is_file():
                file_model = FileModel(
                    name=file_path.name,
                    path=str(file_path),
                    size=file_path.stat().st_size,
                    extension=file_path.suffix
                )
                xml_files.append(file_model)
        
        return xml_files
    
    def get_pdf_files(self, directory: Optional[str] = None) -> List[FileModel]:
        """Obtener lista de archivos PDF"""
        target_dir = directory or self.work_directory
        if not target_dir or not os.path.exists(target_dir):
            return []
        
        pdf_files = []
        for file_path in pathlib.Path(target_dir).glob("*.pdf"):
            if file_path.is_file():
                file_model = FileModel(
                    name=file_path.name,
                    path=str(file_path),
                    size=file_path.stat().st_size,
                    extension=file_path.suffix
                )
                pdf_files.append(file_model)
        
        return pdf_files
    
    def search_files(self, pattern: str, file_extension: str = "*") -> List[FileModel]:
        """Buscar archivos por patrón"""
        if not self.work_directory:
            return []
        
        search_pattern = f"*{pattern}*.{file_extension}" if file_extension != "*" else f"*{pattern}*"
        found_files = []
        
        for file_path in pathlib.Path(self.work_directory).glob(search_pattern):
            if file_path.is_file():
                file_model = FileModel(
                    name=file_path.name,
                    path=str(file_path),
                    size=file_path.stat().st_size,
                    extension=file_path.suffix
                )
                found_files.append(file_model)
        
        return found_files

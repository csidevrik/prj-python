from dataclasses import dataclass, field
from typing import List, Optional
from .file_model import FileModel

@dataclass
class AppState:
    current_directory: Optional[str] = None
    selected_files: List[FileModel] = field(default_factory=list)
    current_view: str = "facturas_view"
    sidebar_collapsed: bool = False
    is_mobile: bool = False
    is_tablet: bool = False
    
    def add_selected_file(self, file: FileModel):
        """Agregar archivo a selección"""
        if file not in self.selected_files:
            self.selected_files.append(file)
    
    def remove_selected_file(self, file: FileModel):
        """Remover archivo de selección"""
        if file in self.selected_files:
            self.selected_files.remove(file)
    
    def clear_selected_files(self):
        """Limpiar selección de archivos"""
        self.selected_files.clear()
    
    def get_selected_count(self) -> int:
        """Obtener cantidad de archivos seleccionados"""
        return len(self.selected_files)

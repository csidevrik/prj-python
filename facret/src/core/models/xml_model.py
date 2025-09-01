from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class XMLModel:
    file_path: str
    root_element: str
    namespace: str
    elements_count: int
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    @property
    def has_namespace(self) -> bool:
        """Verificar si el XML tiene namespace"""
        return bool(self.namespace)
    
    @property
    def file_name(self) -> str:
        """Obtener nombre del archivo"""
        import os
        return os.path.basename(self.file_path)
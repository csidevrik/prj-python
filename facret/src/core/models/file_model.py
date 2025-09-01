from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FileModel:
    name: str
    path: str
    size: int
    extension: str
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            import os
            stat = os.stat(self.path)
            self.created_date = datetime.fromtimestamp(stat.st_ctime)
            self.modified_date = datetime.fromtimestamp(stat.st_mtime)
    
    @property
    def size_mb(self) -> float:
        """Tamaño en megabytes"""
        return round(self.size / (1024 * 1024), 2)
    
    @property
    def is_xml(self) -> bool:
        """Verificar si es archivo XML"""
        return self.extension.lower() == '.xml'
    
    @property
    def is_pdf(self) -> bool:
        """Verificar si es archivo PDF"""
        return self.extension.lower() == '.pdf'

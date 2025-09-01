import hashlib
import os
from typing import List, Dict
from ..models.file_model import FileModel

class DuplicateService:
    def __init__(self):
        self.comparison_methods = {
            'name': self._compare_by_name,
            'size': self._compare_by_size,
            'content': self._compare_by_content
        }
    
    def find_duplicates(self, files: List[FileModel], methods: List[str]) -> Dict[str, List[FileModel]]:
        """Encontrar archivos duplicados usando múltiples métodos"""
        duplicates = {}
        
        for method in methods:
            if method in self.comparison_methods:
                method_duplicates = self.comparison_methods[method](files)
                duplicates[method] = method_duplicates
        
        return duplicates
    
    def _compare_by_name(self, files: List[FileModel]) -> List[List[FileModel]]:
        """Comparar archivos por nombre"""
        name_groups = {}
        
        for file in files:
            name = os.path.splitext(file.name)[0].lower()  # Sin extensión
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(file)
        
        # Retornar solo grupos con duplicados
        return [group for group in name_groups.values() if len(group) > 1]
    
    def _compare_by_size(self, files: List[FileModel]) -> List[List[FileModel]]:
        """Comparar archivos por tamaño"""
        size_groups = {}
        
        for file in files:
            if file.size not in size_groups:
                size_groups[file.size] = []
            size_groups[file.size].append(file)
        
        return [group for group in size_groups.values() if len(group) > 1]
    
    def _compare_by_content(self, files: List[FileModel]) -> List[List[FileModel]]:
        """Comparar archivos por contenido (hash MD5)"""
        hash_groups = {}
        
        for file in files:
            file_hash = self._calculate_file_hash(file.path)
            if file_hash:
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file)
        
        return [group for group in hash_groups.values() if len(group) > 1]
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcular hash MD5 de un archivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""

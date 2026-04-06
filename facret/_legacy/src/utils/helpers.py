import os
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Union, Optional
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileUtilities:
    """Clase para operaciones de utilidad con archivos"""
    
    @staticmethod
    def validate_folder(folder: str) -> Path:
        """
        Valida que la carpeta existe y es accesible
        :param folder: Ruta de la carpeta
        :return: Path object de la carpeta
        :raises: FileNotFoundError, PermissionError
        """
        folder_path = Path(folder)
        if not folder_path.exists():
            raise FileNotFoundError(f"La carpeta no existe: {folder}")
        if not folder_path.is_dir():
            raise NotADirectoryError(f"La ruta no es una carpeta: {folder}")
        if not os.access(folder_path, os.R_OK):
            raise PermissionError(f"Sin permisos de lectura para: {folder}")
        return folder_path

    @staticmethod
    def get_files_by_extensions(folder: str, extensions: Union[str, List[str]]) -> List[Path]:
        """
        Obtiene archivos con extensiones específicas de una carpeta
        :param folder: Ruta de la carpeta
        :param extensions: Extensión o lista de extensiones (ej: '.txt' o ['.txt', '.csv'])
        :return: Lista de objetos Path de archivos encontrados
        """
        try:
            folder_path = FileUtilities.validate_folder(folder)
            
            if isinstance(extensions, str):
                extensions = [extensions]
            
            extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
            
            files = []
            for item in folder_path.iterdir():
                if item.is_file() and item.suffix.lower() in extensions:
                    files.append(item)
            
            logger.info(f"Encontrados {len(files)} archivos con extensiones {extensions} en {folder}")
            return files
            
        except Exception as e:
            logger.error(f"Error al buscar archivos en {folder}: {e}")
            return []

class PrefixRemover:
    """Clase para eliminar prefijos de nombres de archivos"""
    
    @staticmethod
    def remove_prefix_from_filename(filename: str, prefix: str) -> str:
        """
        Elimina prefijo de un nombre de archivo
        :param filename: Nombre del archivo
        :param prefix: Prefijo a eliminar
        :return: Nuevo nombre sin prefijo
        """
        file_path = Path(filename)
        name_without_ext = file_path.stem
        
        if name_without_ext.startswith(prefix):
            new_name = name_without_ext[len(prefix):] + file_path.suffix
            # Evitar nombres vacíos
            if not new_name.replace(file_path.suffix, '').strip():
                logger.warning(f"Eliminar prefijo '{prefix}' dejaría nombre vacío para {filename}")
                return filename
            return new_name
        return filename

    @staticmethod
    def remove_prefix_from_files(folder: str, prefix: str, extensions: Union[str, List[str]], 
                               dry_run: bool = False) -> Dict[str, str]:
        """
        Elimina prefijo de archivos con extensiones específicas
        :param folder: Carpeta donde buscar archivos
        :param prefix: Prefijo a eliminar
        :param extensions: Extensión o lista de extensiones
        :param dry_run: Si True, solo simula sin hacer cambios
        :return: Diccionario {archivo_original: archivo_nuevo}
        """
        try:
            files = FileUtilities.get_files_by_extensions(folder, extensions)
            renamed_files = {}
            
            for file_path in files:
                if file_path.stem.startswith(prefix):
                    new_name = PrefixRemover.remove_prefix_from_filename(file_path.name, prefix)
                    new_path = file_path.parent / new_name
                    
                    if new_path.exists() and new_path != file_path:
                        logger.warning(f"El archivo destino ya existe: {new_path}")
                        continue
                    
                    if not dry_run:
                        try:
                            file_path.rename(new_path)
                            renamed_files[str(file_path)] = str(new_path)
                            logger.info(f"Renombrado: {file_path.name} -> {new_name}")
                        except OSError as e:
                            logger.error(f"Error al renombrar {file_path}: {e}")
                    else:
                        renamed_files[str(file_path)] = str(new_path)
                        logger.info(f"[DRY RUN] Renombraría: {file_path.name} -> {new_name}")
            
            return renamed_files
            
        except Exception as e:
            logger.error(f"Error al eliminar prefijos: {e}")
            return {}

    # Métodos de conveniencia para extensiones específicas
    @staticmethod
    def remove_prefix_csv(folder: str, prefix: str, dry_run: bool = False) -> Dict[str, str]:
        return PrefixRemover.remove_prefix_from_files(folder, prefix, '.csv', dry_run)
    
    @staticmethod
    def remove_prefix_txt(folder: str, prefix: str, dry_run: bool = False) -> Dict[str, str]:
        return PrefixRemover.remove_prefix_from_files(folder, prefix, '.txt', dry_run)
    
    @staticmethod
    def remove_prefix_xml(folder: str, prefix: str, dry_run: bool = False) -> Dict[str, str]:
        return PrefixRemover.remove_prefix_from_files(folder, prefix, '.xml', dry_run)

class DuplicateRemover:
    """Clase para eliminar archivos duplicados"""
    
    @staticmethod
    def get_file_hash(file_path: Path) -> Optional[str]:
        """
        Calcula hash SHA-256 de un archivo
        :param file_path: Ruta del archivo
        :return: Hash en hexadecimal o None si hay error
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Leer en chunks para archivos grandes
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash de {file_path}: {e}")
            return None

    @staticmethod
    def find_duplicates(folder: str) -> Dict[str, List[Path]]:
        """
        Encuentra archivos duplicados basado en hash SHA-256
        :param folder: Carpeta donde buscar
        :return: Diccionario {hash: [archivos_con_mismo_hash]}
        """
        try:
            folder_path = FileUtilities.validate_folder(folder)
            file_hashes = defaultdict(list)
            
            for item in folder_path.iterdir():
                if item.is_file():
                    file_hash = DuplicateRemover.get_file_hash(item)
                    if file_hash:
                        file_hashes[file_hash].append(item)
            
            # Retornar solo grupos con duplicados
            duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
            logger.info(f"Encontrados {len(duplicates)} grupos de archivos duplicados")
            return duplicates
            
        except Exception as e:
            logger.error(f"Error buscando duplicados: {e}")
            return {}

    @staticmethod
    def remove_duplicates(folder: str, keep_oldest: bool = True, dry_run: bool = False) -> List[str]:
        """
        Elimina archivos duplicados
        :param folder: Carpeta donde buscar duplicados
        :param keep_oldest: Si True mantiene el más antiguo, si False mantiene el más reciente
        :param dry_run: Si True, solo simula sin eliminar
        :return: Lista de archivos eliminados
        """
        duplicates = DuplicateRemover.find_duplicates(folder)
        removed_files = []
        
        for file_hash, file_group in duplicates.items():
            if len(file_group) <= 1:
                continue
                
            # Ordenar por fecha de creación
            sorted_files = sorted(file_group, key=lambda x: x.stat().st_ctime)
            
            if keep_oldest:
                files_to_remove = sorted_files[1:]  # Mantener el primero (más antiguo)
                kept_file = sorted_files[0]
            else:
                files_to_remove = sorted_files[:-1]  # Mantener el último (más reciente)
                kept_file = sorted_files[-1]
            
            logger.info(f"Manteniendo: {kept_file.name}")
            
            for file_to_remove in files_to_remove:
                if not dry_run:
                    try:
                        file_to_remove.unlink()
                        removed_files.append(str(file_to_remove))
                        logger.info(f"Eliminado duplicado: {file_to_remove.name}")
                    except OSError as e:
                        logger.error(f"Error eliminando {file_to_remove}: {e}")
                else:
                    removed_files.append(str(file_to_remove))
                    logger.info(f"[DRY RUN] Eliminaría: {file_to_remove.name}")
        
        return removed_files

class XMLProcessor:
    """Clase para procesar archivos XML"""
    
    # Configuración de reemplazos predeterminados
    DEFAULT_REPLACEMENTS = {
        '<![CDATA[<?xml version="1.0" encoding="UTF-8"?><comprobanteRetencion id="comprobante" version="1.0.0">': '',
        '</comprobanteRetencion>]]>': '',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': "'"
    }

    @staticmethod
    def process_xml_file(file_path: Path, replacements: Dict[str, str]) -> bool:
        """
        Aplica reemplazos de texto a un archivo XML
        :param file_path: Ruta del archivo XML
        :param replacements: Diccionario de reemplazos {buscar: reemplazar}
        :return: True si se hicieron cambios, False si no
        """
        try:
            # Leer contenido
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar todos los reemplazos
            for search_str, replace_str in replacements.items():
                content = content.replace(search_str, replace_str)
            
            # Escribir solo si hay cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Procesado: {file_path.name}")
                return True
            else:
                logger.debug(f"Sin cambios en: {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            return False

    @staticmethod
    def clean_xml_files(folder: str, custom_replacements: Optional[Dict[str, str]] = None, 
                       dry_run: bool = False) -> List[str]:
        """
        Limpia archivos XML aplicando reemplazos estándar
        :param folder: Carpeta con archivos XML
        :param custom_replacements: Reemplazos adicionales personalizados
        :param dry_run: Si True, solo simula sin hacer cambios
        :return: Lista de archivos procesados
        """
        try:
            xml_files = FileUtilities.get_files_by_extensions(folder, '.xml')
            
            # Combinar reemplazos predeterminados con personalizados
            replacements = XMLProcessor.DEFAULT_REPLACEMENTS.copy()
            if custom_replacements:
                replacements.update(custom_replacements)
            
            processed_files = []
            
            for xml_file in xml_files:
                if dry_run:
                    logger.info(f"[DRY RUN] Procesaría: {xml_file.name}")
                    processed_files.append(str(xml_file))
                else:
                    if XMLProcessor.process_xml_file(xml_file, replacements):
                        processed_files.append(str(xml_file))
            
            logger.info(f"Procesados {len(processed_files)} archivos XML")
            return processed_files
            
        except Exception as e:
            logger.error(f"Error limpiando archivos XML: {e}")
            return []

# Funciones de conveniencia para mantener compatibilidad con el código anterior
def remove_prefix_files_csv(folder: str, prefix: str):
    """Función de compatibilidad"""
    return PrefixRemover.remove_prefix_csv(folder, prefix)

def remove_prefix_files_txt(folder: str, prefix: str):
    """Función de compatibilidad"""
    return PrefixRemover.remove_prefix_txt(folder, prefix)

def remove_prefix_files_xml(folder: str, prefix: str):
    """Función de compatibilidad"""
    return PrefixRemover.remove_prefix_xml(folder, prefix)

def remove_duplicate_files(folder: str):
    """Función de compatibilidad"""
    return DuplicateRemover.remove_duplicates(folder)

def clean_xml_files(folder: str):
    """Función de compatibilidad"""
    return XMLProcessor.clean_xml_files(folder)

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de uso del código refactorizado
    folder_path = "./mi_carpeta"
    
    # Eliminar prefijos
    print("=== Eliminando prefijos ===")
    renamed = PrefixRemover.remove_prefix_csv(folder_path, "OLD_", dry_run=True)
    print(f"Archivos que se renombrarían: {len(renamed)}")
    
    # Buscar duplicados
    print("\n=== Buscando duplicados ===")
    removed = DuplicateRemover.remove_duplicates(folder_path, dry_run=True)
    print(f"Archivos duplicados que se eliminarían: {len(removed)}")
    
    # Limpiar XMLs
    print("\n=== Limpiando archivos XML ===")
    processed = XMLProcessor.clean_xml_files(folder_path, dry_run=True)
    print(f"Archivos XML que se procesarían: {len(processed)}")
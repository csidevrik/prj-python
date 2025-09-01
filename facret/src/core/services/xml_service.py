import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from ..models.xml_model import XMLModel
from ..utils.xml_utils import XMLUtils

class XMLService:
    def __init__(self):
        self.xml_utils = XMLUtils()
    
    def parse_xml_file(self, file_path: str) -> Optional[XMLModel]:
        """Parsear archivo XML y crear modelo"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            xml_model = XMLModel(
                file_path=file_path,
                root_element=root.tag,
                namespace=self._extract_namespace(root),
                elements_count=len(list(root.iter()))
            )
            
            return xml_model
        except ET.ParseError as e:
            print(f"Error parsing XML {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def validate_xml(self, file_path: str) -> Dict[str, any]:
        """Validar estructura XML"""
        result = {
            "is_valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            ET.parse(file_path)
            result["is_valid"] = True
        except ET.ParseError as e:
            result["errors"].append(f"Parse error: {e}")
        except Exception as e:
            result["errors"].append(f"File error: {e}")
        
        return result
    
    def extract_xml_data(self, file_path: str, elements: List[str]) -> Dict[str, str]:
        """Extraer datos específicos del XML"""
        data = {}
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for element in elements:
                found_element = root.find(element)
                if found_element is not None:
                    data[element] = found_element.text
                else:
                    data[element] = None
        except Exception as e:
            print(f"Error extracting data from {file_path}: {e}")
        
        return data
    
    def _extract_namespace(self, root) -> str:
        """Extraer namespace del elemento raíz"""
        if root.tag.startswith('{'):
            return root.tag.split('}')[0][1:]
        return ""
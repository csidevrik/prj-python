import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class XMLUtils:
    @staticmethod
    def prettify_xml(xml_string: str) -> str:
        """Formatear XML para mejor legibilidad"""
        try:
            root = ET.fromstring(xml_string)
            return ET.tostring(root, encoding='unicode', method='xml')
        except Exception as e:
            print(f"Error prettifying XML: {e}")
            return xml_string
    
    @staticmethod
    def extract_text_content(element: ET.Element) -> str:
        """Extraer todo el contenido de texto de un elemento"""
        return ''.join(element.itertext()).strip()
    
    @staticmethod
    def find_elements_by_name(root: ET.Element, element_name: str) -> List[ET.Element]:
        """Encontrar todos los elementos por nombre"""
        return root.findall(f".//{element_name}")
    
    @staticmethod
    def get_element_attributes(element: ET.Element) -> Dict[str, str]:
        """Obtener todos los atributos de un elemento"""
        return dict(element.attrib)
    
    @staticmethod
    def validate_xml_structure(xml_content: str, required_elements: List[str]) -> Dict[str, bool]:
        """Validar que el XML contiene elementos requeridos"""
        result = {}
        try:
            root = ET.fromstring(xml_content)
            for element_name in required_elements:
                result[element_name] = root.find(f".//{element_name}") is not None
        except Exception as e:
            print(f"Error validating XML structure: {e}")
            for element_name in required_elements:
                result[element_name] = False
        
        return result
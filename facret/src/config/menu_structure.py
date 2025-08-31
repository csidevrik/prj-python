import flet as ft

MENU_STRUCTURE = [
    {
        "key": "home",
        "icon": ft.Icons.HOME_OUTLINED,
        "label": "Página principal",
        "submenus": []
    },
    {
        "key": "my_drive",
        "icon": ft.Icons.FOLDER_OUTLINED,
        "label": "Mi unidad",
        "submenus": []
    },
    {
        "key": "computers",
        "icon": ft.Icons.COMPUTER_OUTLINED,
        "label": "Ordenadores",
        "submenus": []
    },
    {
        "key": "shared",
        "icon": ft.Icons.PEOPLE_OUTLINED,
        "label": "Compartido conmigo",
        "submenus": []
    },
    {
        "key": "facturas",
        "icon": ft.Icons.RECEIPT,
        "label": "Facturas",
        "submenus": [
            {"key": "facturas_pendientes", "label": "Pendientes"},
            {"key": "facturas_procesadas", "label": "Procesadas"},
            {"key": "facturas_vencidas", "label": "Vencidas"},
        ]
    },
    {
        "key": "documentos",
        "icon": ft.Icons.DESCRIPTION_OUTLINED,
        "label": "Documentos",
        "submenus": [
            {"key": "documentos_contratos", "label": "Contratos"},
            {"key": "documentos_reportes", "label": "Reportes"},
            {"key": "documentos_manuales", "label": "Manuales"},
        ]
    },
    {
        "key": "recent",
        "icon": ft.Icons.ACCESS_TIME,
        "label": "Reciente",
        "submenus": []
    },
    {
        "key": "starred",
        "icon": ft.Icons.STAR_OUTLINE,
        "label": "Destacados",
        "submenus": []
    },
    {
        "key": "trash",
        "icon": ft.Icons.DELETE_OUTLINE,
        "label": "Papelera",
        "submenus": []
    }
]

TOOL_BUTTONS = [
    {"key": "chrome", "icon": ft.Icons.OPEN_IN_BROWSER, "label": "Chrome"},
    {"key": "firefox", "icon": ft.Icons.WEB, "label": "Firefox"},
    {"key": "notepad", "icon": ft.Icons.EDIT_NOTE, "label": "Notepad"},
    {"key": "calculator", "icon": ft.Icons.CALCULATE, "label": "Calculadora"},
    {"key": "file_explorer", "icon": ft.Icons.FOLDER_OPEN, "label": "Explorador"},
]

class MenuStructure:
    def __init__(self):
        self.items = MENU_STRUCTURE.copy()  # Copia para permitir modificaciones
    
    def add_item(self, item):
        """Agrega un nuevo elemento al menú"""
        self.items.append(item)
    
    def remove_item(self, key):
        """Remueve un elemento del menú por su key"""
        self.items = [item for item in self.items if item["key"] != key]
    
    def get_items(self):
        """Obtiene todos los elementos del menú"""
        return self.items
    
    def get_item_by_key(self, key):
        """Obtiene un elemento específico por su key"""
        for item in self.items:
            if item["key"] == key:
                return item
        return None
    
    def add_submenu(self, parent_key, submenu_item):
        """Agrega un submenú a un elemento existente"""
        for item in self.items:
            if item["key"] == parent_key:
                item["submenus"].append(submenu_item)
                return True
        return False
    
    def remove_submenu(self, parent_key, submenu_key):
        """Remueve un submenú específico"""
        for item in self.items:
            if item["key"] == parent_key:
                item["submenus"] = [
                    submenu for submenu in item["submenus"] 
                    if submenu["key"] != submenu_key
                ]
                return True
        return False
    
    def find_item_path(self, target_key):
        """Encuentra la ruta completa de un elemento (incluye padre si es submenú)"""
        # Buscar en elementos principales
        for item in self.items:
            if item["key"] == target_key:
                return [item["key"]]            
            # Buscar en submenús
            for submenu in item.get("submenus", []):
                if submenu["key"] == target_key:
                    return [item["key"], submenu["key"]]
        
        return []
    
    def get_submenu_parent(self, submenu_key):
        """Obtiene el elemento padre de un submenú"""
        for item in self.items:
            for submenu in item.get("submenus", []):
                if submenu["key"] == submenu_key:
                    return item["key"]
        return None

# Función utilitaria para crear nuevos elementos de menú
def create_menu_item(key, icon, label, submenus=None):
    """Crea un nuevo elemento de menú con la estructura correcta"""
    return {
        "key": key,
        "icon": icon,
        "label": label,
        "submenus": submenus or []
    }

# Función utilitaria para crear submenús
def create_submenu_item(key, label):
    """Crea un nuevo elemento de submenú"""
    return {
        "key": key,
        "label": label
    }

# Ejemplo de uso:
# menu = MenuStructure()
# nuevo_item = create_menu_item("proyectos", ft.Icons.WORK, "Proyectos", [
#     create_submenu_item("proyectos_activos", "Activos"),
#     create_submenu_item("proyectos_completados", "Completados")
# ])
# menu.add_item(nuevo_item)
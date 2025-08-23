import flet as ft

MENU_STRUCTURE = [
    {
        "key": "home",
        "icon": ft.Icons.HOME,
        "label": "Home",
        "submenus": []  # <- submenús vacíos
    },
    {
        "key": "facturas",
        "icon": ft.Icons.RECEIPT,
        "label": "Facturas",
        "submenus": [  # <- submenús presentes
            {"key": "facturas_pendientes", "label": "Pendientes"},
            {"key": "facturas_procesadas", "label": "Procesadas"},
        ]
    },
    # ...resto de la estructura del menú...
]

TOOL_BUTTONS = [
    {"key": "chrome", "icon": ft.Icons.OPEN_IN_BROWSER, "label": "Chrome"},
    {"key": "firefox", "icon": ft.Icons.OPEN_IN_BROWSER, "label": "Firefox"},
    # ...resto de botones de herramientas...
]

class MenuStructure:
    def __init__(self):
        self.items = MENU_STRUCTURE  # Ahora usa la estructura global

    def add_item(self, item):
        self.items.append(item)

    def get_items(self):
        return self.items

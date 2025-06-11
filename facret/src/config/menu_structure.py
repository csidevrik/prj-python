import flet as ft

MENU_STRUCTURE = [
    {
        "key": "home",
        "icon": ft.Icons.HOME,
        "label": "Inicio",
        "submenus": []
    },
    {
        "key": "facturas",
        "icon": ft.Icons.RECEIPT,
        "label": "Facturas",
        "submenus": [
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

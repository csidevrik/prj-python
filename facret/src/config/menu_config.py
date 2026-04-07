# =============================
# config/menu_config.py
# =============================
"""
Fuente única de verdad para la estructura de navegación.
Para agregar una nueva sección al menú basta con:
  1. Añadir un MenuItem aquí.
  2. Crear el componente/página correspondiente.
  3. Apuntar page_class al nuevo componente.
"""
from dataclasses import dataclass, field
from typing import Optional, List
import flet as ft


@dataclass
class MenuItem:
    key: str
    label: str
    icon: str
    # "module.path.ClassName" — se importa dinámicamente en el router
    page_class: Optional[str] = None
    # Subítems (para búsqueda jerárquica futura)
    children: List["MenuItem"] = field(default_factory=list)


MENU_ITEMS: List[MenuItem] = [
    MenuItem(
        key="home",
        label="Página principal",
        icon=ft.Icons.HOME_OUTLINED,
        page_class="pages.home_page.HomePage",
    ),
    MenuItem(
        key="my_drive",
        label="Download FACS",
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        page_class="pages.facs_downloader_page.FacsDownloaderPage",
    ),
    MenuItem(
        key="gestion_facs",
        label="Gestión FACS",
        icon=ft.Icons.FOLDER_SPECIAL_OUTLINED,
        page_class="pages.facs_manager_page.FacsManagerPage",
    ),
    MenuItem(
        key="contracts",
        label="Contratos ETAPA",
        icon=ft.Icons.RECEIPT_LONG_OUTLINED,
        page_class="pages.contracts_page.ContractsPage",
    ),
    MenuItem(key="computers", label="Ordenadores",        icon=ft.Icons.COMPUTER_OUTLINED),
    MenuItem(key="shared",    label="Compartido conmigo", icon=ft.Icons.PEOPLE_OUTLINED),
    MenuItem(key="recent",    label="Reciente",           icon=ft.Icons.ACCESS_TIME),
    MenuItem(key="starred",   label="Destacados",         icon=ft.Icons.STAR_OUTLINE),
    MenuItem(key="trash",     label="Papelera",           icon=ft.Icons.DELETE_OUTLINE),
]

# Ítems del sistema (no aparecen en el sidebar principal, pero el router los conoce)
SYSTEM_ITEMS: List[MenuItem] = [
    MenuItem(
        key="settings",
        label="Configuración",
        icon=ft.Icons.SETTINGS_OUTLINED,
        page_class="components.settings_panel.SettingsPanel",
    ),
    MenuItem(key="profile",  label="Perfil",        icon=ft.Icons.PERSON_OUTLINE),
    MenuItem(key="help",     label="Ayuda",         icon=ft.Icons.HELP_OUTLINE),
]

# Índice completo (nav + system) para búsqueda y router
ALL_ITEMS: List[MenuItem] = MENU_ITEMS + SYSTEM_ITEMS


def flat_menu() -> List[tuple]:
    """
    Retorna lista plana de (MenuItem, parent_MenuItem | None).
    Útil para búsqueda: incluye tanto ítems raíz como hijos de cualquier nivel.
    """
    result: List[tuple] = []

    def _walk(items: List[MenuItem], parent: Optional[MenuItem] = None):
        for item in items:
            result.append((item, parent))
            if item.children:
                _walk(item.children, item)

    _walk(MENU_ITEMS)
    return result


# Mapa rápido key → label (usado por toolbar y cualquier componente que muestre nombres)
LABEL_MAP: dict = {item.key: item.label for item in MENU_ITEMS}

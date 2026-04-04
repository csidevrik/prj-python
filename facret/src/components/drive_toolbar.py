# =============================
# components/drive_toolbar.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme

NAV_LABELS = {
    "home":      "Página principal",
    "my_drive":  "Mi unidad",
    "computers": "Ordenadores",
    "shared":    "Compartido conmigo",
    "recent":    "Reciente",
    "starred":   "Destacados",
    "trash":     "Papelera",
}

class DriveToolbarComponent:
    def __init__(self, page: ft.Page, on_toggle_sidebar):
        self.page = page
        self._on_toggle_sidebar = on_toggle_sidebar
        self._breadcrumb_text = ft.Text(
            NAV_LABELS["home"],
            size=14,
            color=DriveTheme.GREY_800,
            weight=ft.FontWeight.W_500,
        )

    def build(self):
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=DriveTheme.GREY_600,
                    tooltip="Mostrar/ocultar menú",
                    on_click=self._on_toggle_sidebar,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=DriveTheme.GREY_600),
                self._breadcrumb_text,
            ], spacing=4),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, DriveTheme.GREY_200)),
        )

    def update_breadcrumb(self, key: str):
        self._breadcrumb_text.value = NAV_LABELS.get(key, key)
        self._breadcrumb_text.update()

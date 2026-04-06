# =============================
# components/toolbar.py
# =============================
import flet as ft
from config.theme import DriveTheme
from config.menu_config import ALL_ITEMS

LABEL_MAP = {item.key: item.label for item in ALL_ITEMS}


class DriveToolbarComponent:
    def __init__(self, page: ft.Page, on_toggle_sidebar):
        self.page = page
        self._on_toggle_sidebar = on_toggle_sidebar
        self._breadcrumb_text = ft.Text(
            LABEL_MAP.get("home", "Página principal"),
            size=14,
            color=DriveTheme.GREY_800,
            weight=ft.FontWeight.W_500,
        )

    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=DriveTheme.GREY_600,
                        tooltip="Mostrar/ocultar menú",
                        on_click=self._on_toggle_sidebar,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=DriveTheme.GREY_600),
                    self._breadcrumb_text,
                ],
                spacing=4,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, DriveTheme.GREY_200)),
        )

    def update_breadcrumb(self, key: str):
        self._breadcrumb_text.value = LABEL_MAP.get(key, key)
        self._breadcrumb_text.update()

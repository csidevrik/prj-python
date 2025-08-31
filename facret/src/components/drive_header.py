# =============================
# components/drive_header.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme

class DriveHeaderComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.search_query = ""
    
    def build(self):
        return ft.Container(
            content=ft.Row([
                # Logo y título
                ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.FOLDER_SPECIAL,
                            color=DriveTheme.PRIMARY_BLUE,
                            size=22
                        ),
                        padding=8,
                    ),
                    ft.Text(
                        "Facret Drive",
                        size=22,
                        weight=ft.FontWeight.W_400,
                        color=DriveTheme.GREY_600
                    )
                ], spacing=8),
                
                # Barra de búsqueda
                ft.Container(
                    content=ft.TextField(
                        hint_text="Search on Folder",
                        prefix_icon=ft.Icons.SEARCH,
                        filled=True,
                        fill_color=DriveTheme.GREY_100,
                        border_radius=24,
                        border=ft.InputBorder.NONE,
                        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        on_change=self._on_search_change,
                    ),
                    width=600,
                    margin=ft.margin.symmetric(horizontal=40),
                ),
                
                # Controles de usuario
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Ayuda",
                        icon_color=DriveTheme.GREY_600,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        tooltip="Configuración",
                        icon_color=DriveTheme.GREY_600,
                    ),
                    ft.Container(
                        content=ft.CircleAvatar(
                            content=ft.Text("U", color=ft.Colors.WHITE),
                            bgcolor=DriveTheme.PRIMARY_BLUE,
                            radius=16,
                        ),
                        margin=ft.margin.only(left=8),
                    )
                ], spacing=4)
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, DriveTheme.GREY_200)),
        )
    
    def _on_search_change(self, e):
        self.search_query = e.control.value
        # Implementar lógica de búsqueda

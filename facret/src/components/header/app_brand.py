# =============================
# components/header/app_brand.py (CORREGIDO)
# =============================
import flet as ft
from config.drive_theme import DriveTheme

class AppBrandComponent:
    def __init__(self, app_name: str = "Facret Drive", icon: str = ft.Icons.FOLDER_SPECIAL, compact_mode: bool = False):
        self.app_name = app_name
        self.icon = icon
        self.compact_mode = compact_mode
    
    def build(self):
        # En modo compacto (móvil) solo mostrar ícono o versión corta
        if self.compact_mode:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(
                        self.icon,
                        color=DriveTheme.PRIMARY_BLUE,
                        size=20
                    ),
                    ft.Text(
                        "Facret",  # Versión corta
                        size=18,
                        weight=ft.FontWeight.W_400,
                        color=DriveTheme.GREY_600
                    )
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            )
        
        # Modo desktop completo
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        self.icon,
                        color=DriveTheme.PRIMARY_BLUE,
                        size=22
                    ),
                    padding=8,
                ),
                ft.Text(
                    self.app_name,
                    size=22,
                    weight=ft.FontWeight.W_400,
                    color=DriveTheme.GREY_600
                )
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            # Ancho fijo para desktop, flexible para móvil
            width=None if self.compact_mode else 200,
        )
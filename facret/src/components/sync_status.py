# =============================
# components/sync_status.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme

class SyncStatusComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_synced = True
    
    def build(self):
        if self.is_synced:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.CLOUD_DONE, color=ft.colors.GREEN_600, size=20),
                    ft.Text(
                        "Tus archivos están actualizados",
                        size=14,
                        color=DriveTheme.GREY_600
                    )
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                bgcolor=DriveTheme.GREY_50,
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.SYNC, color=DriveTheme.PRIMARY_BLUE, size=20),
                    ft.Text(
                        "Sincronizando archivos...",
                        size=14,
                        color=DriveTheme.GREY_600
                    )
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                bgcolor=ft.colors.BLUE_50,
            )

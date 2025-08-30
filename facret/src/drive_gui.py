# =============================
# drive_gui.py
# =============================
import flet as ft
from components.drive_header import DriveHeaderComponent
from components.drive_sidebar import DriveSidebarComponent
from components.drive_content import DriveContentComponent
from components.sync_status import SyncStatusComponent
from config.drive_theme import DriveTheme

def run_drive_gui():
    def main(page: ft.Page):
        page.title = "FACRET"
        page.window.icon = "../assets/favicon.ico"
        page.window.width = 1200
        page.window.height = 800
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # Aplicar tema personalizado
        page.theme = DriveTheme.get_theme()
        
        # Componentes principales
        header = DriveHeaderComponent(page)
        sidebar = DriveSidebarComponent(page)
        content = DriveContentComponent(page)
        sync_status = SyncStatusComponent(page)
        
        # Layout principal
        main_layout = ft.Column([
            # Header con búsqueda
            header.build(),
            
            # Contenido principal
            ft.Row([
                # Sidebar izquierdo
                sidebar.build(),
                
                # Área de contenido principal
                ft.Container(
                    content=ft.Column([
                        # Estado de sincronización
                        sync_status.build(),
                        # Contenido principal
                        content.build(),
                    ], spacing=0),
                    expand=True,
                    bgcolor=ft.colors.GREY_50,
                )
            ], spacing=0, expand=True)
            
        ], spacing=0, expand=True)
        
        page.add(main_layout)

    ft.app(target=main, assets_dir="assets")
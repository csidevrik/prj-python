# =============================
# gui.py
# =============================
import flet as ft
from components.sidebar                      import DriveSidebarComponent
from components.toolbar                      import DriveToolbarComponent
from components.content                      import DriveContentComponent
from components.header.responsive_header     import ResponsiveDriveHeader as ResponsiveHeaderComponent
from config.theme                            import DriveTheme

# Mapa de keys del sidebar a componentes
_CONTENT_MAP = {
    "my_drive": "facs_downloader_panel.FacsDownloaderPanel",
}

def run_drive_gui():
    def main(page: ft.Page):
        page.title = "FACRET"
        page.window.icon = "../assets/favicon.ico"
        page.window.width = 1200
        page.window.height = 800
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = DriveTheme.get_theme()

        header  = ResponsiveHeaderComponent(page)
        sidebar = DriveSidebarComponent(page)
        toolbar = DriveToolbarComponent(page, on_toggle_sidebar=sidebar._toggle_sidebar)

        # Área de contenido reactiva
        content_area = ft.Container(
            content=DriveContentComponent(page).build(),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )

        def on_navigate(key: str):
            toolbar.update_breadcrumb(key)
            if key == "my_drive":
                from components.facs_downloader_panel import FacsDownloaderPanel
                content_area.content = FacsDownloaderPanel(page).build()
            else:
                content_area.content = DriveContentComponent(page).build()
            content_area.update()

        sidebar.on_nav_change = on_navigate

        main_layout = ft.Column([
            header.build(),
            toolbar.build(),
            ft.Row([
                sidebar.build(),
                content_area,
            ], spacing=0, expand=True),
        ], spacing=0, expand=True)

        page.add(main_layout)

    ft.app(target=main, assets_dir="assets")
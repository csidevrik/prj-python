import flet as ft
from components.app_bar import AppBarComponent
from components.nav_rail import NavRailComponent
from components.content_router import ContentRouter
from components.file_explorer   import FileExplorerComponent
from components.preview_panel   import PreviewPanel

from config.theme import AppGradients

def run_gui():
    def main(page: ft.Page):
        page.title = "FACRET"
        page.window.icon = "../assets/favicon.ico"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.padding = 0

        router = ContentRouter(page)

        def on_select(key: str):
            router.show(key)

        def toggle_nav_rail(e=None):  # Añadir parámetro e=None
            nav_rail.visible = not nav_rail.visible
            nav_rail.update()
        
        # Inicializar componentes
        app_bar         = AppBarComponent(page, on_menu_click=toggle_nav_rail)
        nav_rail        = NavRailComponent(page)
        # file_explorer   = FileExplorerComponent(page)
        # preview         = PreviewPanel()

        # Layout principal
        layout = ft.Column([
            app_bar.build(),
            ft.Row([
                nav_rail.build(),
                ft.VerticalDivider(width=1),
                # ft.Row([
                #     file_explorer.build(),
                #     ft.VerticalDivider(width=1),
                #     preview.build(),
                # ], expand=True),
                router.build(),
            ], expand=True),
        ], expand=True)

        page.add(layout)

        # Para reemplazar el logo de Flet en la AppBar:
        # 1. Usa un archivo de imagen local (ej: "assets/logo.png") o un SVG.
        # 2. Cambia el parámetro 'leading' de tu AppBar o Container por un ft.Image o ft.Image.asset.

        custom_bar_content = ft.Row(
            [
                # Reemplaza el icono por tu logo personalizado
                ft.Image(
                    src="../assets/favicon.png",  # Cambia la ruta a tu logo
                    width=32,
                    height=32,
                    fit=ft.ImageFit.CONTAIN,
                ),
                # ...existing code...
            ],
            # ...existing code...
        )

    ft.app(target=main)


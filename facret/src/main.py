import ctypes
import flet as ft
from components.nav_rail import NavRailComponent
from config.theme import AppGradients


def main(page: ft.Page):
    # Icono de ventana (ajusta la ruta según tu estructura real)
    page.window.icon = "../assets/favicon.ico"

    # Usar barra de título estándar
    page.window.frameless = False

    # Identificador de ventana (Windows)
    hwnd = ctypes.windll.user32.GetForegroundWindow()

    is_maximized = False

    def minimize_window(e):
        ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

    def maximize_window(e):
        nonlocal is_maximized
        ctypes.windll.user32.ShowWindow(hwnd, 9 if is_maximized else 3)  # RESTORE / MAXIMIZE
        is_maximized = not is_maximized

    def close_window(e):
        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

    # Instanciar el nav rail (pasamos page) y empezar oculto
    nav_rail = NavRailComponent(page, visible=False)

    def toggle_nav_rail(e):
        nav_rail.toggle()  # alterna y se actualiza

    # Barra superior personalizada
    custom_title_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(ft.Icons.MENU, on_click=toggle_nav_rail),
                ft.Text("FACRET", size=16, weight="bold", color="white"),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.MINIMIZE, on_click=minimize_window),
                ft.IconButton(ft.Icons.CROP_SQUARE, on_click=maximize_window),
                ft.IconButton(ft.Icons.CLOSE, on_click=close_window),
            ],
            alignment="spaceBetween",
        ),
        gradient=AppGradients.by_name("Summer"),
        height=40,
        padding=ft.padding.symmetric(horizontal=10),
    )

    # Contenido principal (placeholder)
    content = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("File Explorer", expand=True),
                ft.Text("Preview Panel", expand=True),
            ]
        ),
        expand=True,
        bgcolor="#F5F5F5",
    )

    # Layout principal: ¡usa nav_rail.view!
    page.add(
        ft.Row(
            controls=[
                nav_rail.view,  # <<-- IMPORTANTE
                ft.Column(
                    controls=[custom_title_bar, content],
                    expand=True,
                ),
            ],
            expand=True,
        )
    )


ft.app(target=main)

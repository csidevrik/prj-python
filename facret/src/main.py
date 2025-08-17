import flet as ft
import ctypes
from navrail import NavRail  # Importar el componente del menú lateral
from config.theme import AppGradients  # Importar AppGradients para usar el método by_name

def main(page: ft.Page):
    # Configurar la ventana con barra superior estándar
    page.window.frameless = False  # Activar la barra de título estándar del sistema operativo

    # Obtener el identificador de la ventana (solo para Windows)
    hwnd = ctypes.windll.user32.GetForegroundWindow()

    # Variable para rastrear el estado de maximización
    is_maximized = False

    # Funciones para controlar la ventana
    def minimize_window(e):
        ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

    def maximize_window(e):
        nonlocal is_maximized
        if is_maximized:
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        else:
            ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
        is_maximized = not is_maximized

    def close_window(e):
        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

    # Crear una instancia del menú lateral
    nav_rail = NavRail(visible=False)  # Inicialmente oculto

    # Función para alternar la visibilidad del menú lateral
    def toggle_nav_rail(e):
        nav_rail.visible = not nav_rail.visible
        nav_rail.update()

    # Barra personalizada con el botón de menú
    custom_title_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(ft.Icons.MENU, on_click=toggle_nav_rail),  # Botón de menú
                ft.Text("FACRET", size=16, weight="bold", color="white"),
                ft.Container(expand=True),  # Espaciador
                ft.IconButton(ft.Icons.MINIMIZE, on_click=minimize_window),
                ft.IconButton(ft.Icons.CROP_SQUARE, on_click=maximize_window),
                ft.IconButton(ft.Icons.CLOSE, on_click=close_window),
            ],
            alignment="spaceBetween",
        ),
        gradient=AppGradients.by_name("Summer"),  # Usar el gradiente por nombre
        height=40,
        padding=ft.padding.symmetric(horizontal=10),
    )

    # Contenido principal
    content = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("File Explorer", expand=True),
                ft.Text("Preview Panel", expand=True),
            ],
        ),
        expand=True,
        bgcolor="#F5F5F5",
    )

    # Estructura de la página
    page.add(
        ft.Row(
            controls=[
                nav_rail,  # Agregar el menú lateral
                ft.Column(
                    controls=[
                        custom_title_bar,
                        content,
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )
    )

ft.app(target=main)
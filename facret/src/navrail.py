import flet as ft

class NavRail(ft.Container):
    def __init__(self, visible=True):
        super().__init__(
            visible=visible,
            content=ft.Column(
                controls=[
                    ft.Text("Menú 1"),
                    ft.Text("Menú 2"),
                    ft.Text("Menú 3"),
                ],
            ),
            width=200,
            bgcolor="#E0E0E0",
            padding=10,
        )

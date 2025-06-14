import flet as ft
from config.theme import AppColors

class NavRailComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.visible = False
        self.width = 200
        self._container = None  # Referencia al container
        
    def update(self):
        if self._container:
            self._container.visible = self.visible
            self._container.update()
        
    def build(self):
        self._container = ft.Container(
            content=ft.Column([
                ft.Text("Menú", color=AppColors.ON_BACKGROUND, size=14),
                ft.Divider(),
                # Aquí irán los items del menú
            ], spacing=1),
            bgcolor=AppColors.BACKGROUND,
            visible=self.visible,
            width=self.width
        )
        return self._container

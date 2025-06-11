import flet as ft

class FileExplorerComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        
    def build(self):
        return ft.Container(
            content=ft.Text("File Explorer"),
            expand=True
        )

import flet as ft

class PreviewPanel:
    def build(self):
        return ft.Container(
            content=ft.Text("Preview Panel"),
            expand=True
        )

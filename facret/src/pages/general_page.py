import flet as ft
from flet import UserControl

class GeneralAppearancePage(UserControl):
    def build(self):
        return ft.Column([
            ft.Text("Appearance", size=22, weight=ft.FontWeight.W_600),
            ft.Divider(),
            ft.Switch(label="Dark theme"),
            ft.Dropdown(label="Density", options=[ft.dropdown.Option("Comfortable"), ft.dropdown.Option("Compact")]),
        ], expand=True)

class GeneralFilesPage(UserControl):
    def build(self):
        return ft.Column([
            ft.Text("Files & Folders", size=22, weight=ft.FontWeight.W_600),
            ft.Divider(),
            ft.TextField(label="Downloads location", value="/home/carlos/Downloads", expand=True),
            ft.ElevatedButton("Change...")
        ], expand=True)
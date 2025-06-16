# run_desktop.py
import flet as ft
from gui import run_gui

if __name__ == "__main__":
    ft.app(
        target=run_gui,
        assets_dir="src/assets",
        window_icon="favicon.png"
    )

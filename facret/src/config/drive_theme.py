# =============================
# config/drive_theme.py
# =============================
import flet as ft

class DriveTheme:
    # Colores principales de Google Drive
    PRIMARY_BLUE = "#1a73e8"
    SURFACE_WHITE = "#ffffff"
    GREY_50 = "#f8f9fa"
    GREY_100 = "#f1f3f4"
    GREY_200 = "#e8eaed"
    GREY_400 = "#bdbdbd"
    GREY_600 = "#5f6368"
    GREY_700 = "#202124"
    GREY_800 = "#3c4043"

    
    @staticmethod
    def get_theme():
        return ft.Theme(
            color_scheme_seed=DriveTheme.PRIMARY_BLUE,
            visual_density=ft.VisualDensity.COMPACT,
        )
    
    @staticmethod
    def get_card_style():
        return {
            "bgcolor": DriveTheme.SURFACE_WHITE,
            "border_radius": 12,
            "shadow": ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            )
        }
    
    @staticmethod
    def get_button_style():
        return {
            "style": ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            )
        }
import flet as ft

class AppColors:
    # Colores principales
    BACKGROUND = "#DDD5D0"  # Fondo general
    SURFACE = "#CFC0BD"    # Tarjetas, paneles
    SECONDARY = "#B8B8AA"  # Elementos secundarios
    PRIMARY = "#7F9183"    # AppBar, botones principales
    ACCENT = "#586F6B"     # Botones destacados
    
    # Colores de texto
    ON_PRIMARY = "#FFFFFF"    # Texto sobre primary
    ON_SECONDARY = "#000000"  # Texto sobre secondary (con 87% opacidad)
    ON_BACKGROUND = "#000000" # Texto sobre fondo (con 87% opacidad)
    ON_SURFACE = "#000000"    # Texto sobre surface (con 87% opacidad)

class AppGradients:
    @staticmethod
    def app_bar():
        return ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[AppColors.PRIMARY, AppColors.ACCENT]
        )
    
    @staticmethod
    def content_area():
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[AppColors.BACKGROUND, AppColors.SURFACE]
        )

class AppStyles:
    class Text:
        BODY = {
            "size": 10,
            "color": AppColors.ON_BACKGROUND,
            "weight": "normal"
        }
        
        TITLE = {
            "size": 12,
            "color": AppColors.ON_BACKGROUND,
            "weight": "bold"
        }
    
    class Button:
        PRIMARY = {
            "bgcolor": AppColors.PRIMARY,
            "color": AppColors.ON_PRIMARY,
            "style": ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        }
        
        ACCENT = {
            "bgcolor": AppColors.ACCENT,
            "color": AppColors.ON_PRIMARY,
            "style": ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        }
    
    class Container:
        SURFACE = {
            "bgcolor": AppColors.SURFACE,
            "border_radius": 8,
            "padding": 10
        }
        
        CARD = {
            "bgcolor": AppColors.SURFACE,
            "border_radius": 12,
            "padding": 16,
            "shadow": ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color="#14000000"  # Negro con 8% de opacidad (14 ≈ 0.08 * 255)
            )
        }

# Ejemplo de uso:
# ft.Text("Título", **AppStyles.Text.TITLE)
# ft.ElevatedButton("Botón", **AppStyles.Button.PRIMARY)
# ft.Container(**AppStyles.Container.CARD)

import flet as ft
import math

class AppColors:
    # Colores del sistema usando una paleta coherente
    BACKGROUND      = "#3CA5C5"     # Color de fondo base
    SURFACE         = "#53aecc"     # Color para superficies elevadas (cards, paneles)
    SECONDARY       = "#B8B8AA"     # Color para elementos secundarios
    PRIMARY         = "#7F9183"     # Color principal (acciones importantes)
    ACCENT          = "#586F6B"     # Color de acento (destacar elementos)
    
    # Colores para texto con contraste apropiado
    ON_BACKGROUND   = "#B9DEEC"     # Texto sobre fondo
    ON_SURFACE      = "#000000"     # Texto sobre superficies
    ON_SECONDARY    = "#000000"     # Texto sobre color secundario
    ON_PRIMARY      = "#FFFFFF"     # Texto sobre color principal (blanco)
    ON_ACCENT       = "#FFFFFF"     # Texto sobre color de acento

class AppGradients:
    @staticmethod
    def app_bar():
        return ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[AppColors.PRIMARY, AppColors.ACCENT],
            rotation=math.pi/2
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
            "size": 8,
            "color": AppColors.ON_BACKGROUND,
            "weight": "normal"
        }
        
        TITLE = {
            "size": 14,
            "color": AppColors.ON_PRIMARY,
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

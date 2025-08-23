import flet as ft
import math
import json
import os

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

    # Colorea para el navrail
    NAV_BG = "#3ca5c5"                 # fondo del rail
    NAV_ITEM_BG = "#3ca5c5"            # fondo ítem normal
    NAV_ITEM_SELECTED_BG = "#1f2937"   # fondo ítem seleccionado
    NAV_TEXT = "#cbd5e1"
    NAV_TEXT_SELECTED = "#ffffff"

class GradientLibrary:
    """
    Permite cargar gradientes desde un archivo JSON y acceder a ellos por nombre.
    El JSON debe tener el formato: [{"name": "...", "colors": ["#hex1", "#hex2", ...]}, ...]
    """
    def __init__(self, json_path=None):
        self.gradients = {}
        if json_path and os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for grad in data:
                    self.gradients[grad["name"]] = grad["colors"]

    def get_gradient(self, name, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, rotation=None):
        colors = self.gradients.get(name)
        if not colors:
            raise ValueError(f"Gradient '{name}' not found.")
        return ft.LinearGradient(
            begin=begin,
            end=end,
            colors=colors,
            rotation=rotation
        )

    def list_gradients(self):
        return list(self.gradients.keys())
    
    @staticmethod
    def get_default_gradient():
        return ft.LinearGradient(
            begin=ft.Alignment(-1, 0),  # Inicio del gradiente (izquierda)
            end=ft.Alignment(1, 0),    # Fin del gradiente (derecha)
            colors=["#3CA5C5", "#1E88E5"],  # Colores del gradiente
        )

# Ejemplo de inicialización global (ajusta la ruta según tu estructura)
GRADIENT_JSON_PATH = os.path.join(os.path.dirname(__file__), "gradients.json")
gradient_lib = GradientLibrary(GRADIENT_JSON_PATH)

class AppGradients:
    # Instancia de GradientLibrary para cargar gradientes desde el JSON
    gradient_library = GradientLibrary(GRADIENT_JSON_PATH)

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
    
    @staticmethod
    def by_name(name, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, rotation=None):
        # Utiliza la instancia de GradientLibrary para obtener un gradiente por nombre
        return AppGradients.gradient_library.get_gradient(name, begin, end, rotation)

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
# ft.Container(gradient=AppGradients.by_name("Omolon"))
# ft.Container(**AppStyles.Container.CARD)

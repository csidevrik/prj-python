import flet as ft
from ...config.constants import NAVIGATION_ITEMS

class MenuItem:
    def __init__(self, item_data, navigation_handler, is_active=False):
        self.data = item_data
        self.navigation_handler = navigation_handler
        self.is_active = is_active
        
    def build(self, is_collapsed=False):
        """Construir el elemento de menú"""
        if is_collapsed:
            return self._build_collapsed()
        else:
            return self._build_expanded()
    
    def _build_expanded(self):
        """Menú expandido con ícono y texto"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    name=self._get_icon(),
                    color=self._get_color(),
                    size=20
                ),
                ft.Text(
                    self.data["title"],
                    color=self._get_color(),
                    size=14,
                    weight=ft.FontWeight.W500 if self.is_active else ft.FontWeight.NORMAL
                )
            ], spacing=12),
            padding=ft.padding.all(12),
            bgcolor=self._get_bg_color(),
            border_radius=8,
            on_click=self._on_click,
            on_hover=self._on_hover,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
    
    def _build_collapsed(self):
        """Menú colapsado solo con ícono"""
        return ft.Container(
            content=ft.Icon(
                name=self._get_icon(),
                color=self._get_color(),
                size=24
            ),
            padding=ft.padding.all(12),
            bgcolor=self._get_bg_color(),
            border_radius=8,
            on_click=self._on_click,
            on_hover=self._on_hover,
            tooltip=self.data["title"],
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            alignment=ft.alignment.center
        )
    
    def _get_icon(self):
        """Obtener ícono según el tipo de menú"""
        icon_map = {
            "description": ft.icons.DESCRIPTION,
            "delete": ft.icons.DELETE_OUTLINE,
            "edit": ft.icons.EDIT,
            "remove_circle": ft.icons.REMOVE_CIRCLE_OUTLINE,
            "receipt": ft.icons.RECEIPT,
            "assessment": ft.icons.ASSESSMENT,
            "code": ft.icons.CODE,
            "visibility": ft.icons.VISIBILITY
        }
        return icon_map.get(self.data["icon"], ft.icons.HELP_OUTLINE)
    
    def _get_color(self):
        """Obtener color según estado activo"""
        return "#00BCD4" if self.is_active else "#666666"
    
    def _get_bg_color(self):
        """Obtener color de fondo según estado activo"""
        return "#E0F7FA" if self.is_active else "transparent"
    
    def _on_click(self, e):
        """Manejar click en elemento de menú"""
        self.navigation_handler.navigate_to(self.data["view"])
    
    def _on_hover(self, e):
        """Manejar hover en elemento de menú"""
        if e.data == "true" and not self.is_active:
            e.control.bgcolor = "#F5F5F5"
        elif e.data == "false" and not self.is_active:
            e.control.bgcolor = "transparent"
        e.control.update()
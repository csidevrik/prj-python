import flet as ft
from ...config.theme import AppTheme

class Breadcrumb:
    def __init__(self, page: ft.Page, navigation_handler):
        self.page = page
        self.navigation_handler = navigation_handler
        self.breadcrumb_items = []
        
    def build(self):
        self.breadcrumb_container = ft.Container(
            content=ft.Row(
                controls=self._build_breadcrumb_items(),
                spacing=5
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            bgcolor="#ECEFF1",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0"))
        )
        
        return self.breadcrumb_container
    
    def _build_breadcrumb_items(self):
        items = []
        current_section = self._get_current_section()
        
        if current_section:
            items.append(
                ft.TextButton(
                    text=current_section["title"],
                    on_click=lambda e: self.navigation_handler.navigate_to(current_section["view"])
                )
            )
            
            # Si hay subsección, agregar separador y subsección
            current_subsection = self._get_current_subsection()
            if current_subsection:
                items.extend([
                    ft.Icon(ft.icons.CHEVRON_RIGHT, size=16),
                    ft.Text(current_subsection, color=AppTheme.TEXT_SECONDARY)
                ])
        
        return items
    
    def _get_current_section(self):
        from ...config.constants import NAVIGATION_ITEMS
        for item in NAVIGATION_ITEMS:
            if item["view"] == self.navigation_handler.current_view:
                return item
        return None
    
    def _get_current_subsection(self):
        # TODO: Implementar lógica para subsecciones
        # Por ejemplo, si estamos en "facturas > eliminar duplicados"
        return None
    
    def update_breadcrumb(self):
        """Actualizar breadcrumb cuando cambie la navegación"""
        self.breadcrumb_container.content.controls = self._build_breadcrumb_items()
        self.page.update()
    
    def update_responsive(self, is_mobile, is_tablet):
        if is_mobile:
            # En móvil, breadcrumb más compacto
            self.breadcrumb_container.padding = ft.padding.symmetric(horizontal=10, vertical=5)
            # TODO: Truncar texto largo
        else:
            self.breadcrumb_container.padding = ft.padding.symmetric(horizontal=20, vertical=8)
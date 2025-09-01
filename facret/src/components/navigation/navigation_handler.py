import flet as ft

class NavigationHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_view = "facturas_view"  # Vista por defecto
        self.view_cache = {}  # Cache de vistas para mejor rendimiento
        
    def navigate_to(self, view_name):
        """Navegar a una vista específica"""
        if view_name != self.current_view:
            self.current_view = view_name
            self._update_main_content()
    
    def get_current_view(self):
        """Obtener la vista actual"""
        if self.current_view not in self.view_cache:
            self.view_cache[self.current_view] = self._create_view(self.current_view)
        
        return self.view_cache[self.current_view]
    
    def _create_view(self, view_name):
        """Factory para crear vistas"""
        from ...views import (
            facturas_view, duplicates_view, rename_xml_view
            # del_prefix_view, retenciones_view, informes_view,
            # xml_view, pdf_viewer_view
        )
        
        view_map = {
            "facturas_view": facturas_view.FacturasView,
            "duplicates_view": duplicates_view.DuplicatesView,
            "rename_xml_view": rename_xml_view.RenameXMLView,
            # "del_prefix_view": del_prefix_view.DelPrefixView,
            # "retenciones_view": retenciones_view.RetencionesView,
            # "informes_view": informes_view.InformesView,
            # "xml_view": xml_view.XMLView,
            # "pdf_viewer_view": pdf_viewer_view.PDFViewerView
        }
        
        view_class = view_map.get(view_name)
        if view_class:
            return view_class(self.page).build()
        else:
            return self._create_placeholder_view(view_name)
    
    def _create_placeholder_view(self, view_name):
        """Crear vista placeholder mientras se desarrolla"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Vista: {view_name}",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text("En desarrollo..."),
                ft.ElevatedButton(
                    text="Botón de ejemplo",
                    on_click=lambda _: print(f"Acción en {view_name}")
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _update_main_content(self):
        """Actualizar el contenido principal"""
        # Esta función será llamada por el layout principal
        # para refrescar el contenido cuando cambie la vista
        pass
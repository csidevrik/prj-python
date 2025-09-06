import flet as ft

class NavigationHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_view           = "facturas_view"  # Vista por defecto
        self.view_cache             = {}  # Cache de vistas para mejor rendimiento
        self.main_content_container = None
        self.sidebar                = None

    def set_main_content_container(self, container):
        self.main_content_container = container 
    
    def set_sidebar_reference(self, sidebar):
        self.sidebar = sidebar

    def navigate_to(self, view_name):
        """Navegar a una vista específica"""
        if view_name != self.current_view:
            print(f"Navegando a {view_name}")
            self.current_view = view_name
            self._update_main_content()
            if self.sidebar:
                self.sidebar.update_active_state()

    def get_current_view(self):
        """Obtener la vista actual"""
        if self.current_view not in self.view_cache:
            self.view_cache[self.current_view] = self._create_view(self.current_view)
        
        return self.view_cache[self.current_view]
    
    def _create_view(self, view_name):
        """Factory para crear vistas"""
        print(f"Creando vista: {view_name}")
        
        try:
            from ...views import (
                facturas_view, duplicates_view, rename_xml_view
                # del_prefix_view, retenciones_view, informes_view,
                # xml_view, pdf_viewer_view
            )
        
            view_map = {
                "facturas_view":    facturas_view.FacturasView,
                "duplicates_view":  duplicates_view.DuplicatesView,
                "rename_xml_view":  rename_xml_view.RenameXMLView,
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
        except ImportError as e:
            print(f"Error al importar vista: {view_name}. Detalles: {e}")
            return self._create_placeholder_view(view_name) 
        except Exception as e:
            print(f"Error inesperado al crear vista: {view_name}. Detalles: {e}")
            return self._create_placeholder_view(view_name)

    def _create_placeholder_view(self, view_name):
        """Crear vista placeholder mientras se desarrolla"""
        title  = view_name.replace("_view", "").replace("_", " ").title()
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.CONSTRUCTION,
                    size=64,
                    color="#FF9800"
                ),
                ft.Text(
                    title,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#333333"
                ),
                ft.Text(
                    "Esta vista está en desarrollo",
                    size=16,
                    color="#666666"
                ),
                ft.ElevatedButton(
                    text=f"Función de ejemplo - {title}",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=lambda _: print(f"Acción ejecutada en vista: {title}")
                ),
                ft.Text(
                    f"Vista técnica: {view_name}",
                    size=12,
                    color="#999999"
                )
            ], 
            alignment=ft.MainAxisAlignment.CENTER),
            # horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.alignment.center,
            expand=True,
            padding=40
        )
    
    def _update_main_content(self):
        """Actualizar el contenido principal"""
        if self.main_content_container:
            print(f"Actualizando contenido principal con {self.current_view}")
            new_view = self.get_current_view()
            self.main_content_container.content = new_view
            self.page.update()
        else:
            print("❌ No hay referencia al container principal")
        # Esta función será llamada por el layout principal
        # para refrescar el contenido cuando cambie la vista
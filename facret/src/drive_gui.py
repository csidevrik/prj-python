# =============================
# drive_gui.py
# =============================
import flet as ft
from components.drive_header                import DriveHeaderComponent
from components.drive_sidebar               import DriveSidebarComponent
from components.drive_content               import DriveContentComponent
from components.sync_status                 import SyncStatusComponent
from components.header.responsive_header    import ResponsiveDriveHeader as ResponsiveHeaderComponent
from config.drive_theme                     import DriveTheme

class DriveApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sidebar_state = "expanded"  # "hidden", "collapsed", "expanded"
        self.setup_page()
        self.init_components()
        self.build_layout()
        
        # Configurar listener para cambios de tamaño de ventana
        self.page.on_resize = self.on_window_resize
    
    def setup_page(self):
        self.page.title = "FACRET"
        self.page.window.icon = "../assets/favicon.ico"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = DriveTheme.get_theme()
    
    def init_components(self):
        # Componentes principales
        self.header = ResponsiveHeaderComponent(self.page)
        self.sidebar = DriveSidebarComponent(self.page)
        self.content = DriveContentComponent(self.page)
        self.sync_status = SyncStatusComponent(self.page)
        
        # Configurar callback del botón de menú en el header
        self.header.on_menu_click = self.toggle_sidebar
    
    def on_window_resize(self, e):
        """Maneja el redimensionamiento de la ventana"""
        if self.sidebar_state == "expanded":
            # Solo actualizar si el sidebar está expandido
            self.update_layout()
    
    def toggle_sidebar(self):
        """Alterna entre los estados del sidebar"""
        if self.sidebar_state == "expanded":
            self.sidebar_state = "collapsed"
        elif self.sidebar_state == "collapsed":
            self.sidebar_state = "hidden"
        else:  # hidden
            self.sidebar_state = "expanded"
        
        self.update_layout()
    
    def get_sidebar_widget(self):
        """Retorna el widget del sidebar según el estado actual"""
        if self.sidebar_state == "hidden":
            return None
        elif self.sidebar_state == "collapsed":
            return self.sidebar.build_collapsed()
        else:  # expanded
            # Usar build_responsive para ancho adaptativo
            available_width = self.page.window.width if self.page.window.width else 1200
            return self.sidebar.build_responsive(available_width)
    
    def build_layout(self):
        """Construye el layout principal"""
        self.main_row = ft.Row(spacing=0, expand=True)
        
        # Contenido principal (siempre presente)
        self.content_container = ft.Container(
            content=ft.Column([
                self.sync_status.build(),
                self.content.build(),
            ], spacing=0),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )
        
        self.main_layout = ft.Column([
            # Header con búsqueda
            self.header.build(),
            # Contenido principal
            self.main_row
        ], spacing=0, expand=True)
        
        self.update_layout()
        self.page.add(self.main_layout)
    
    def update_layout(self):
        """Actualiza el layout según el estado del sidebar"""
        self.main_row.controls.clear()
        
        # Agregar sidebar si no está oculto
        sidebar_widget = self.get_sidebar_widget()
        if sidebar_widget:
            self.main_row.controls.append(sidebar_widget)
        
        # Agregar contenido principal
        self.main_row.controls.append(self.content_container)
        
        self.page.update()
    
    def get_layout_info(self):
        """Información del layout para debugging"""
        return {
            "sidebar_state": self.sidebar_state,
            "window_width": self.page.window.width,
            "window_height": self.page.window.height,
            "sidebar_width": self.sidebar.get_optimal_width() if self.sidebar_state == "expanded" else None
        }

def run_drive_gui():
    def main(page: ft.Page):
        app = DriveApp(page)
    
    ft.app(target=main, assets_dir="assets")
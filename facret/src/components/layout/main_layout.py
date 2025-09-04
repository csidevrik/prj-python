import flet as ft
from .appbar        import AppBar
from .sidebar       import Sidebar
from .breadcrumb    import Breadcrumb
from ..navigation.navigation_handler import NavigationHandler
from ...config.settings import AppSettings

class MainLayout:
    def __init__(self, page: ft.Page):
        self.page                = page
        self.settings            = AppSettings()
        self.navigation_handler  = NavigationHandler(page)

        # Crear componentes
        self.appbar              = AppBar(page, self.navigation_handler)
        self.sidebar             = Sidebar(page, self.navigation_handler)
        self.breadcrumb          = Breadcrumb(page, self.navigation_handler)

        # Estado responsive
        self.is_mobile           = True
        self.is_tablet           = False

    def build(self):
        # Layout principal usando Row y Column
        main_content = ft.Column([
            # AppBar
            self.appbar.build(),
            
            # Breadcrumb
            self.breadcrumb.build(),
            
            # Contenido principal (Sidebar + Main Area)
            ft.Row([
                # Sidebar
                self.sidebar.build(),
                
                # Main content area
                ft.Container(
                    content=self.navigation_handler.get_current_view(),
                    expand=True,
                    padding=20,
                    bgcolor="#54DBBA"
                )
            ], expand=True, spacing=0)
        ], spacing=0, expand=True)
        
        return main_content
    
    def handle_resize(self, width, height):
        # Determinar tipo de dispositivo
        self.is_mobile = width < self.settings.MOBILE_BREAKPOINT
        self.is_tablet = width < self.settings.TABLET_BREAKPOINT and not self.is_mobile
        
        # Actualizar componentes responsive
        self.appbar.update_responsive(self.is_mobile, self.is_tablet)
        self.sidebar.update_responsive(self.is_mobile, self.is_tablet)
        self.breadcrumb.update_responsive(self.is_mobile, self.is_tablet)
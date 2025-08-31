# =============================
# components/header/responsive_header.py (NUEVO)
# =============================
import flet as ft
from config.drive_theme import DriveTheme
from components.header.app_brand import AppBrandComponent
from components.header.search_component import SearchComponent
from .tools_component import ToolsComponent, ToolButton
from components.header.user_session import UserSessionComponent

class ResponsiveDriveHeader:
    def __init__(self, page: ft.Page):
        self.page = page
        self.mobile_breakpoint = 768
        self.is_mobile = self._check_if_mobile()
        self.drawer_open = False
        
        # Configurar herramientas con prioridades móviles
        self.tools_config = [
            ToolButton(
                icon=ft.Icons.HELP_OUTLINE,
                tooltip="Ayuda",
                on_click=self._handle_help_click,
                mobile_priority=2  # Solo en hamburger menu
            ),
            ToolButton(
                icon=ft.Icons.SETTINGS_OUTLINED,
                tooltip="Configuración",
                on_click=self._handle_settings_click,
                mobile_priority=2  # Solo en hamburger menu
            ),
            ToolButton(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                tooltip="Notificaciones",
                on_click=self._handle_notifications_click,
                badge_count=3,
                mobile_priority=1  # Mostrar siempre
            )
        ]
        
        # Configurar sugerencias de búsqueda
        self.search_suggestions = [
            "Documentos recientes", "Mis archivos", "Compartidos conmigo",
            "Favoritos", "Papelera", "Presentaciones", "Hojas de cálculo"
        ]
        
        # Inicializar componentes
        self._init_components()
        
        # Escuchar cambios de tamaño de ventana
        self.page.on_resize = self._on_page_resize
    
    def _check_if_mobile(self):
        return self.page.width < self.mobile_breakpoint
    
    def _init_components(self):
        # Brand component
        self.app_brand = AppBrandComponent(compact_mode=self.is_mobile)
        
        # Search component
        self.search_component = SearchComponent(
            page=self.page,
            suggestions=self.search_suggestions,
            on_search=self._handle_search,
            mobile_mode=self.is_mobile
        )
        
        # Tools component
        self.tools_component = ToolsComponent(
            tools=self.tools_config,
            mobile_mode=self.is_mobile
        )
        
        # User session component
        self.user_session = UserSessionComponent(
            user_name="Usuario",
            user_email="usuario@facret.com",
            on_profile_click=self._handle_profile_click,
            on_logout_click=self._handle_logout_click
        )
        
        # Drawer para móvil
        if self.is_mobile:
            self._create_mobile_drawer()
    
    def build(self):
        if self.is_mobile:
            return self._build_mobile_header()
        else:
            return self._build_desktop_header()
    
    def _build_desktop_header(self):
        """Header para desktop con 4 containers en Row"""
        return ft.Container(
            content=ft.Row([
                # Container 1: Brand
                ft.Container(
                    content=self.app_brand.build(),
                    width=200,
                    padding=ft.padding.symmetric(horizontal=8),
                ),
                
                # Container 2: Search (expandible)
                ft.Container(
                    content=self.search_component.build(),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=8),
                ),
                
                # Container 3: Tools
                ft.Container(
                    content=self.tools_component.build(),
                    padding=ft.padding.symmetric(horizontal=8),
                ),
                
                # Container 4: User Session
                ft.Container(
                    content=self.user_session.build(),
                    padding=ft.padding.symmetric(horizontal=8),
                ),
            ], 
            alignment=ft.MainAxisAlignment.START,
            spacing=0),
            
            # Container principal con estilo
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, DriveTheme.GREY_200)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=2,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 1)
            ),
        )
    
    def _build_mobile_header(self):
        """Header para móvil con hamburger menu"""
        return ft.Container(
            content=ft.Row([
                # Container 1: Hamburger Menu
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.MENU,
                        tooltip="Menú",
                        on_click=self._toggle_drawer,
                        icon_color=DriveTheme.GREY_600,
                    ),
                    padding=ft.padding.all(4),
                ),
                
                # Container 2: Brand (compacto)
                ft.Container(
                    content=self.app_brand.build(),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=8),
                ),
                
                # Container 3: Search Button + Visible Tools
                ft.Container(
                    content=ft.Row([
                        self.search_component.build(),
                        self.tools_component.build(),
                    ], spacing=4),
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                
                # Container 4: User Session
                ft.Container(
                    content=self.user_session.build(),
                    padding=ft.padding.symmetric(horizontal=8),
                ),
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=0),
            
            # Container principal móvil
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, DriveTheme.GREY_200)),
        )
    
    def _create_mobile_drawer(self):
        """Crear drawer/sidebar para móvil con herramientas ocultas"""
        drawer_tools = [tool for tool in self.tools_config if tool.mobile_priority == 2]
        
        drawer_items = [
            # Sección de búsqueda en drawer
            ft.Container(
                content=ft.Column([
                    ft.Text("Búsqueda", weight=ft.FontWeight.BOLD, size=16),
                    ft.TextField(
                        hint_text=self.placeholder,
                        prefix_icon=ft.Icons.SEARCH,
                        on_submit=self._drawer_search_submit,
                        border_radius=8,
                    )
                ], spacing=8),
                padding=ft.padding.all(16),
                margin=ft.margin.only(bottom=16),
            ),
            
            ft.Divider(height=1),
            
            # Sección de herramientas
            ft.Container(
                content=ft.Text("Herramientas", weight=ft.FontWeight.BOLD, size=16),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            )
        ]
        
        # Agregar herramientas al drawer
        for tool in drawer_tools:
            drawer_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(tool.icon, size=20),
                        ft.Text(tool.tooltip, size=14),
                        # Badge si existe
                        ft.Container(
                            content=ft.Text(str(tool.badge_count), size=10, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED,
                            border_radius=8,
                            padding=ft.padding.all(4),
                            visible=bool(tool.badge_count),
                        ) if tool.badge_count else ft.Container()
                    ], spacing=12),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    on_click=tool.on_click,
                    ink=True,
                )
            )
        
        self.drawer = ft.NavigationDrawer(
            controls=drawer_items,
            bgcolor=DriveTheme.SURFACE_WHITE,
        )
    
    def _toggle_drawer(self, e):
        """Toggle del drawer móvil"""
        if hasattr(self, 'drawer'):
            self.page.drawer = self.drawer
            self.page.drawer.open = not getattr(self.page.drawer, 'open', False)
            self.page.update()
    
    def _drawer_search_submit(self, e):
        """Manejar búsqueda desde drawer"""
        if self.on_search:
            self.on_search(e.control.value)
        # Cerrar drawer después de búsqueda
        self.page.drawer.open = False
        self.page.update()
    
    def _on_page_resize(self, e):
        """Manejar cambio de tamaño de ventana"""
        old_mobile_state = self.is_mobile
        self.is_mobile = self._check_if_mobile()
        
        # Si cambió el estado móvil, reinicializar componentes
        if old_mobile_state != self.is_mobile:
            self._init_components()
            # Aquí necesitarías rebuilder la UI
            self._rebuild_header()
    
    def _rebuild_header(self):
        """Reconstruir header cuando cambie el modo"""
        # Esta función debería ser llamada desde el componente padre
        # para actualizar completamente la UI
        pass
    
    # Event handlers
    def _handle_search(self, query: str):
        print(f"Buscando: {query}")
        # Implementar lógica de búsqueda
    
    def _handle_help_click(self, e):
        print("Ayuda clickeada")
    
    def _handle_settings_click(self, e):
        print("Configuración clickeada")
    
    def _handle_notifications_click(self, e):
        print("Notificaciones clickeadas")
    
    def _handle_profile_click(self):
        print("Perfil clickeado")
    
    def _handle_logout_click(self):
        print("Logout clickeado")

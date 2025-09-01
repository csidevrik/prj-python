import flet as ft
from ...config.constants import NAVIGATION_ITEMS
from ...config.theme import AppTheme
from ...config.settings import AppSettings

class Sidebar:
    def __init__(self, page: ft.Page, navigation_handler):
        self.page = page
        self.navigation_handler = navigation_handler
        self.settings = AppSettings()
        self.is_collapsed = False
        self.is_mobile_mode = False
        
        # Crear elementos de menú
        self.menu_items = []
        self._create_menu_items()
        
    def build(self):
        self.sidebar_container = ft.Container(
            content=ft.Column([
                # Toggle button y search
                self._build_header(),
                
                # Menu items
                ft.Column(
                    controls=self.menu_items,
                    spacing=2,
                    expand=True
                )
            ], spacing=10),
            width=self.settings.SIDEBAR_EXPANDED_WIDTH,
            bgcolor="white",
            padding=10,
            border=ft.border.only(right=ft.border.BorderSide(1, "#E0E0E0"))
        )
        
        return self.sidebar_container
    
    def _build_header(self):
        self.toggle_button = ft.IconButton(
            icon=ft.icons.MENU,
            tooltip="Colapsar/Expandir menú",
            on_click=self._toggle_sidebar
        )
        
        self.search_input = ft.TextField(
            hint_text="Buscar menús...",
            height=35,
            on_change=self._filter_menu_items,
            prefix_icon=ft.icons.SEARCH
        )
        
        return ft.Column([
            self.toggle_button,
            self.search_input
        ], spacing=10)
    
    def _create_menu_items(self):
        self.menu_items = []
        for item in NAVIGATION_ITEMS:
            menu_item = self._create_menu_item(item)
            self.menu_items.append(menu_item)
    
    def _create_menu_item(self, item):
        is_active = self.navigation_handler.current_view == item["view"]
        
        button = ft.Container(
            content=ft.Row([
                ft.Icon(
                    name=getattr(ft.icons, item["icon"].upper(), ft.icons.HELP),
                    color=AppTheme.TEXT_PRIMARY if not is_active else AppTheme.PRIMARY_COLOR
                ),
                ft.Text(
                    item["title"],
                    color=AppTheme.TEXT_PRIMARY if not is_active else AppTheme.PRIMARY_COLOR,
                    size=14
                )
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            bgcolor=AppTheme.SIDEBAR_ACTIVE_COLOR if is_active else "transparent",
            border_radius=8,
            on_click=lambda e, view=item["view"]: self._navigate_to(view),
            data=item
        )
        
        # Agregar hover effect
        button.on_hover = self._on_item_hover
        
        return button
    
    def _navigate_to(self, view_name):
        self.navigation_handler.navigate_to(view_name)
        self._update_active_state()
    
    def _update_active_state(self):
        for menu_item in self.menu_items:
            item_data = menu_item.data
            is_active = self.navigation_handler.current_view == item_data["view"]
            menu_item.bgcolor = AppTheme.SIDEBAR_ACTIVE_COLOR if is_active else "transparent"
        
        self.page.update()
    
    def _on_item_hover(self, e):
        if e.data == "true":  # Mouse enter
            if e.control.bgcolor != AppTheme.SIDEBAR_ACTIVE_COLOR:
                e.control.bgcolor = AppTheme.SIDEBAR_HOVER_COLOR
        else:  # Mouse leave
            if e.control.bgcolor != AppTheme.SIDEBAR_ACTIVE_COLOR:
                e.control.bgcolor = "transparent"
        self.page.update()
    
    def _toggle_sidebar(self, e):
        self.is_collapsed = not self.is_collapsed
        self._animate_sidebar_toggle()
    
    def _animate_sidebar_toggle(self):
        new_width = self.settings.SIDEBAR_COLLAPSED_WIDTH if self.is_collapsed else self.settings.SIDEBAR_EXPANDED_WIDTH
        
        # Animar el cambio de ancho
        self.sidebar_container.width = new_width
        
        # Mostrar/ocultar texto y search
        self.search_input.visible = not self.is_collapsed
        
        # Actualizar tooltips en estado colapsado
        for menu_item in self.menu_items:
            if self.is_collapsed:
                menu_item.tooltip = menu_item.data["title"]
                # Ocultar texto, mostrar solo ícono
                menu_item.content = ft.Row([
                    ft.Icon(
                        name=getattr(ft.icons, menu_item.data["icon"].upper(), ft.icons.HELP),
                        color=AppTheme.TEXT_PRIMARY
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            else:
                menu_item.tooltip = None
                # Mostrar ícono y texto
                menu_item.content = ft.Row([
                    ft.Icon(
                        name=getattr(ft.icons, menu_item.data["icon"].upper(), ft.icons.HELP),
                        color=AppTheme.TEXT_PRIMARY
                    ),
                    ft.Text(
                        menu_item.data["title"],
                        color=AppTheme.TEXT_PRIMARY,
                        size=14
                    )
                ], spacing=10)
        
        self.page.update()
    
    def _filter_menu_items(self, e):
        search_term = e.control.value.lower()
        
        for menu_item in self.menu_items:
            item_title = menu_item.data["title"].lower()
            menu_item.visible = search_term in item_title
        
        self.page.update()
    
    def update_responsive(self, is_mobile, is_tablet):
        self.is_mobile_mode = is_mobile
        
        if is_mobile:
            # En móvil, sidebar como overlay
            self.sidebar_container.width = 250
            # TODO: Implementar lógica de overlay
        elif is_tablet:
            # En tablet, sidebar colapsable
            self.sidebar_container.width = self.settings.SIDEBAR_COLLAPSED_WIDTH if self.is_collapsed else 200
        else:
            # En desktop, comportamiento normal
            self.sidebar_container.width = self.settings.SIDEBAR_COLLAPSED_WIDTH if self.is_collapsed else self.settings.SIDEBAR_EXPANDED_WIDTH
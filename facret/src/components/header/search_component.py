# =============================
# components/header/search_component.py (MEJORADO)
# =============================
import flet as ft
from typing import Callable, List, Optional
from config.drive_theme import DriveTheme

class SearchComponent:
    def __init__(
        self, 
        page: ft.Page,
        placeholder: str = "Search on Folder",
        on_search: Optional[Callable] = None,
        suggestions: Optional[List[str]] = None,
        mobile_mode: bool = False
    ):
        self.page = page
        self.placeholder = placeholder
        self.on_search = on_search
        self.suggestions = suggestions or []
        self.mobile_mode = mobile_mode
        self.search_query = ""
        self.is_dropdown_open = False
        self.filtered_suggestions = []
        
        # En móvil, el search puede estar oculto inicialmente
        if mobile_mode:
            self._build_mobile_search()
        else:
            self._build_desktop_search()
    
    def _build_desktop_search(self):
        self.search_field = ft.TextField(
            hint_text=self.placeholder,
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            fill_color=DriveTheme.GREY_100,
            border_radius=24,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_change=self._on_search_change,
            height=40,
        )
    
    def _build_mobile_search(self):
        # En móvil, solo un botón de búsqueda que abre overlay
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip="Buscar",
            on_click=self._open_mobile_search,
        )
    
    def build(self):
        if self.mobile_mode:
            return ft.Container(
                content=self.search_button,
                padding=ft.padding.all(4),
            )
        
        return ft.Container(
            content=self.search_field,
            # Se expandirá para ocupar el espacio disponible
            expand=True,
            padding=ft.padding.symmetric(horizontal=20),
            margin=ft.margin.symmetric(horizontal=16),
        )
    
    def _on_search_change(self, e):
        self.search_query = e.control.value
        if self.on_search:
            self.on_search(self.search_query)
    
    def _open_mobile_search(self, e):
        # Implementar overlay de búsqueda para móvil
        search_overlay = ft.AlertDialog(
            title=ft.Text("Buscar"),
            content=ft.TextField(
                hint_text=self.placeholder,
                autofocus=True,
                on_submit=self._mobile_search_submit,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._close_mobile_search),
            ]
        )
        self.page.dialog = search_overlay
        search_overlay.open = True
        self.page.update()
    
    def _mobile_search_submit(self, e):
        if self.on_search:
            self.on_search(e.control.value)
        self._close_mobile_search(e)
    
    def _close_mobile_search(self, e):
        self.page.dialog.open = False
        self.page.update()
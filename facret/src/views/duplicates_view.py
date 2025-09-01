import flet as ft
from ..core.services.duplicate_service import DuplicateService

class DuplicatesView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.duplicate_service = DuplicateService()
        self.duplicates_found = []
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Text(
                    "Eliminar Archivos Duplicados",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#333333"
                ),
                
                ft.Divider(),
                
                # Scan options
                ft.Row([
                    ft.Checkbox(
                        label="Comparar por nombre",
                        value=True
                    ),
                    ft.Checkbox(
                        label="Comparar por contenido",
                        value=False
                    ),
                    ft.Checkbox(
                        label="Comparar por tamaño",
                        value=True
                    )
                ], spacing=20),
                
                # Scan button
                ft.ElevatedButton(
                    text="Buscar Duplicados",
                    icon=ft.icons.SEARCH,
                    on_click=self._scan_duplicates,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE
                ),
                
                # Results area
                ft.Container(
                    content=self._build_results_area(),
                    expand=True,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=8,
                    padding=10
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _build_results_area(self):
        return ft.Column([
            ft.Text(
                "Haz clic en 'Buscar Duplicados' para comenzar el análisis",
                size=16,
                color=ft.colors.GREY_600
            )
        ], expand=True)
    
    def _scan_duplicates(self, e):
        # TODO: Implementar búsqueda de duplicados
        self._show_alert("Escaneando archivos duplicados...")
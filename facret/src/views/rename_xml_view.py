import flet as ft
from ..core.services.rename_service import RenameService

class RenameXMLView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.rename_service = RenameService()
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Text(
                    "Renombrar Archivos XML",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#333333"
                ),
                
                ft.Divider(),
                
                # Rename options
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Opciones de Renombrado", size=18, weight=ft.FontWeight.BOLD),
                            
                            ft.Row([
                                ft.Text("Patrón:", width=100),
                                ft.TextField(
                                    hint_text="ej: FACTURA_{numero}_{fecha}",
                                    expand=True
                                )
                            ], spacing=10),
                            
                            ft.Row([
                                ft.Text("Prefijo:", width=100),
                                ft.TextField(
                                    hint_text="ej: FAC_",
                                    width=200
                                )
                            ], spacing=10),
                            
                            ft.Row([
                                ft.Text("Sufijo:", width=100),
                                ft.TextField(
                                    hint_text="ej: _procesado",
                                    width=200
                                )
                            ], spacing=10),
                            
                            ft.Row([
                                ft.Checkbox(label="Incluir fecha"),
                                ft.Checkbox(label="Incluir hora"),
                                ft.Checkbox(label="Convertir a mayúsculas")
                            ], spacing=20)
                        ], spacing=15),
                        padding=20
                    )
                ),
                
                # Preview area
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Vista Previa", size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("Selecciona archivos para ver la vista previa"),
                                height=200,
                                border=ft.border.all(1, ft.colors.GREY_300),
                                border_radius=5,
                                padding=10
                            )
                        ], spacing=15),
                        padding=20
                    ),
                    expand=True
                ),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        text="Vista Previa",
                        icon=ft.icons.PREVIEW,
                        on_click=self._show_preview
                    ),
                    ft.ElevatedButton(
                        text="Aplicar Cambios",
                        icon=ft.icons.CHECK,
                        on_click=self._apply_rename,
                        bgcolor=ft.colors.GREEN,
                        color=ft.colors.WHITE
                    )
                ], spacing=10)
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _show_preview(self, e):
        # TODO: Mostrar vista previa del renombrado
        pass
    
    def _apply_rename(self, e):
        # TODO: Aplicar renombrado de archivos
        pass
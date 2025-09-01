import flet as ft
from ..core.services.file_service import FileService
from ..core.services.xml_service import XMLService

class FacturasView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.file_service = FileService()
        self.xml_service = XMLService()
        self.selected_files = []
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Text(
                        "Gestión de Facturas",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#333333"
                    ),
                    ft.ElevatedButton(
                        text="Actualizar",
                        icon=ft.icons.REFRESH,
                        on_click=self._refresh_files
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # File actions toolbar
                ft.Row([
                    ft.ElevatedButton(
                        text="Seleccionar Todo",
                        icon=ft.icons.SELECT_ALL,
                        on_click=self._select_all_files
                    ),
                    ft.ElevatedButton(
                        text="Deseleccionar Todo",
                        icon=ft.icons.DESELECT,
                        on_click=self._deselect_all_files
                    ),
                    ft.ElevatedButton(
                        text="Procesar Seleccionados",
                        icon=ft.icons.PLAY_ARROW,
                        on_click=self._process_selected_files,
                        bgcolor=ft.colors.GREEN,
                        color=ft.colors.WHITE
                    )
                ], spacing=10),
                
                # File list
                ft.Container(
                    content=self._build_file_list(),
                    expand=True,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=8,
                    padding=10
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _build_file_list(self):
        # Placeholder para lista de archivos
        self.file_list = ft.Column([
            ft.Text("No hay archivos cargados", size=16, color=ft.colors.GREY_600)
        ], expand=True)
        
        return self.file_list
    
    def _refresh_files(self, e):
        # TODO: Implementar carga de archivos desde directorio
        files = self.file_service.get_xml_files()
        # self._update_file_list(files)
    
    # def _update_file_list(self, files):
    #     controls = []
    #     for file in files:
    #         controls.append(
    #             ft.CheckboxListTile(
    #                 value=False,
    #                 title=ft.Text(file.name),
    #                 subtitle=ft.Text(f"Tamaño: {file.size} bytes"),
    #                 on_change=lambda e, f=file: self._on_file_selected(e, f)
    #             )
    #         )
        
    #     self.file_list.controls = controls if controls else [
    #         ft.Text("No se encontraron archivos XML", color=ft.colors.GREY_600)
    #     ]
    #     self.page.update()
    
    def _select_all_files(self, e):
        for control in self.file_list.controls:
            if hasattr(control, 'value'):
                control.value = True
        self.page.update()
    
    def _deselect_all_files(self, e):
        for control in self.file_list.controls:
            if hasattr(control, 'value'):
                control.value = False
        self.page.update()
    
    def _on_file_selected(self, e, file):
        if e.control.value:
            if file not in self.selected_files:
                self.selected_files.append(file)
        else:
            if file in self.selected_files:
                self.selected_files.remove(file)
    
    def _process_selected_files(self, e):
        if not self.selected_files:
            self._show_alert("Por favor selecciona al menos un archivo")
            return
        
        # TODO: Implementar procesamiento de archivos
        self._show_alert(f"Procesando {len(self.selected_files)} archivos...")
    
    def _show_alert(self, message):

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Información"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
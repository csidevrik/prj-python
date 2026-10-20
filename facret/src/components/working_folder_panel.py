# =============================
# components/working_folder_panel.py
# =============================
import flet as ft
from config.theme import DriveTheme
from logic.config_manager import load_config, save_config
from logic.folder_stats import get_folder_stats


class WorkingFolderPanel:
    """Panel global para seleccionar y mostrar la carpeta de trabajo."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._config = load_config()
        self._current_folder = self._config.get("carpeta_trabajo", "")

        # File Picker para seleccionar carpeta
        self._picker = ft.FilePicker(on_result=self._on_picker_result)
        page.overlay.append(self._picker)

        # Referencias a callbacks
        self.on_folder_changed = None

    def _on_browse_click(self, e):
        """Abre el diálogo de selección de carpeta."""
        self._picker.get_directory_path()

    def _on_picker_result(self, e: ft.FilePickerResultEvent):
        """Maneja la selección de carpeta desde el File Picker."""
        if e.path:
            self._current_folder = e.path
            self._save_folder_and_notify()

    def _save_folder_and_notify(self):
        """Guarda la carpeta en config y notifica a los observadores."""
        data = load_config()
        data["carpeta_trabajo"] = self._current_folder
        save_config(data)

        # Notificar a gui.py para actualizar sidebar
        if "on_config_change" in self.page.data:
            self.page.data["on_config_change"]()

        # Actualizar el panel
        self.update()

    def update(self):
        """Recarga la carpeta actual desde config."""
        self._config = load_config()
        self._current_folder = self._config.get("carpeta_trabajo", "")
        if hasattr(self, '_folder_text'):
            self._folder_text.value = self._current_folder or "No seleccionada"
            self._folder_text.update()

    def build(self) -> ft.Control:
        """Construye el panel de carpeta de trabajo."""
        self._folder_text = ft.Text(
            value=self._current_folder or "No seleccionada",
            size=12,
            color=DriveTheme.ON_SURFACE,
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.FOLDER_OPEN_OUTLINED,
                    size=18,
                    color=DriveTheme.PRIMARY_BLUE,
                ),
                ft.Column([
                    ft.Text(
                        "Carpeta de Trabajo",
                        size=11,
                        color=DriveTheme.GREY_600,
                        weight=ft.FontWeight.W_500,
                    ),
                    self._folder_text,
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_size=16,
                    icon_color=DriveTheme.PRIMARY_BLUE,
                    tooltip="Actualizar",
                    on_click=lambda e: self.update(),
                ),
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    icon_size=16,
                    icon_color=DriveTheme.PRIMARY_BLUE,
                    tooltip="Cambiar carpeta",
                    on_click=self._on_browse_click,
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.with_opacity(0.05, DriveTheme.PRIMARY_BLUE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, DriveTheme.PRIMARY_BLUE)),
            border_radius=8,
            margin=ft.margin.symmetric(horizontal=16, vertical=8),
        )

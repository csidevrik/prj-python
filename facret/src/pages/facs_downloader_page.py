# =============================
# pages/facs_downloader_page.py
# =============================
import flet as ft
import threading
from config.theme import DriveTheme
from logic.config_manager import load_config, save_config


class FacsDownloaderPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self._config = load_config()

        self._tf_outlook = ft.TextField(
            value=self._config.get("carpeta_outlook", ""),
            border_color=DriveTheme.GREY_200,
            focused_border_color=DriveTheme.PRIMARY_BLUE,
            text_size=13,
            expand=True,
        )
        self._tf_remitente = ft.TextField(
            value=self._config.get("correo_remitente", ""),
            border_color=DriveTheme.GREY_200,
            focused_border_color=DriveTheme.PRIMARY_BLUE,
            text_size=13,
            expand=True,
        )
        self._tf_destinatario = ft.TextField(
            value=self._config.get("correo_destinatario", ""),
            border_color=DriveTheme.GREY_200,
            focused_border_color=DriveTheme.PRIMARY_BLUE,
            text_size=13,
            expand=True,
        )
        self._tf_guardar = ft.TextField(
            value=self._config.get("carpeta_guardar", ""),
            border_color=DriveTheme.GREY_200,
            focused_border_color=DriveTheme.PRIMARY_BLUE,
            text_size=13,
            expand=True,
        )

        # ── File Picker para seleccionar carpeta de descarga ──────────────
        self._picker = ft.FilePicker(on_result=self._on_picker_result)
        page.overlay.append(self._picker)

        self._log_column = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=2,
            expand=True,
        )
        self._run_btn = None  # asignado en build()

    # ── Build ────────────────────────────────────────────────────────────────

    def build(self):
        self._run_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=18, color=ft.Colors.WHITE),
                ft.Text("Ejecutar descarga", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=8, tight=True),
            style=ft.ButtonStyle(
                bgcolor=DriveTheme.PRIMARY_BLUE,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            on_click=self._run_download,
        )

        return ft.Container(
            content=ft.Column([
                self._build_header(),
                ft.Divider(height=1, color=DriveTheme.GREY_200),
                ft.Container(
                    content=ft.Column([
                        self._build_form(),
                        ft.Container(height=16),
                        self._build_actions(),
                        ft.Container(height=16),
                        self._build_log_panel(),
                    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                ),
            ], spacing=0, expand=True),
            expand=True,
            bgcolor=DriveTheme.GREY_50,
        )

    def _build_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=24, color=DriveTheme.PRIMARY_BLUE),
                    bgcolor=ft.Colors.with_opacity(0.1, DriveTheme.PRIMARY_BLUE),
                    border_radius=10,
                    padding=10,
                ),
                ft.Column([
                    ft.Text("Download FACS", size=18, weight=ft.FontWeight.W_600, color=DriveTheme.GREY_800),
                    ft.Text(
                        "Descarga facturas ETAPA desde Outlook local · sin cuenta Microsoft paga",
                        size=12,
                        color=DriveTheme.GREY_600,
                    ),
                ], spacing=2, tight=True),
            ], spacing=14),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=DriveTheme.SURFACE_WHITE,
        )

    def _build_form(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Configuracion de la accion", size=13, weight=ft.FontWeight.W_600, color=DriveTheme.GREY_800),
                ft.Container(height=12),
                self._build_field("Carpeta de Outlook",              "Ej: Inbox\\CONTRACT\\ETAPA\\FACS", ft.Icons.FOLDER_OUTLINED,  self._tf_outlook),
                self._build_field("Correo del remitente (From)",     "Ej: info@comunicados-etapa.com",   ft.Icons.ALTERNATE_EMAIL,   self._tf_remitente),
                self._build_field("Correo del destinatario (To)",    "Ej: csigua@emov.gob.ec",           ft.Icons.PERSON_OUTLINE,    self._tf_destinatario),
                self._build_field_with_picker("Carpeta de descarga local", "Ej: D:\\Facturas_ETAPA", ft.Icons.SAVE_ALT, self._tf_guardar),
            ], spacing=0),
            **DriveTheme.get_card_style(),
            padding=20,
        )

    def _build_field(self, label: str, hint: str, icon, field: ft.TextField):
        field.hint_text = hint
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, size=18, color=DriveTheme.GREY_600), width=36),
                ft.Column([
                    ft.Text(label, size=11, color=DriveTheme.GREY_600, weight=ft.FontWeight.W_500),
                    field,
                ], spacing=2, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.padding.only(bottom=16),
        )

    def _build_field_with_picker(self, label: str, hint: str, icon, field: ft.TextField):
        """Campo con botón Explorar para seleccionar carpeta."""
        field.hint_text = hint
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, size=18, color=DriveTheme.GREY_600), width=36),
                ft.Column([
                    ft.Text(label, size=11, color=DriveTheme.GREY_600, weight=ft.FontWeight.W_500),
                    ft.Row([
                        field,
                        ft.IconButton(
                            icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                            icon_size=18,
                            icon_color=DriveTheme.PRIMARY_BLUE,
                            tooltip="Explorar carpeta",
                            on_click=self._on_browse_click,
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=2, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.padding.only(bottom=16),
        )

    def _build_actions(self):
        return ft.Row([
            ft.OutlinedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.SAVE_OUTLINED, size=16, color=DriveTheme.PRIMARY_BLUE),
                    ft.Text("Guardar configuracion", size=13, color=DriveTheme.PRIMARY_BLUE),
                ], spacing=8, tight=True),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    side=ft.BorderSide(1, DriveTheme.PRIMARY_BLUE),
                ),
                on_click=self._save_config,
            ),
            self._run_btn,
        ], spacing=12)

    def _build_log_panel(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TERMINAL, size=16, color=DriveTheme.GREY_600),
                    ft.Text("Registro de actividad", size=13, weight=ft.FontWeight.W_600, color=DriveTheme.GREY_800),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=DriveTheme.GREY_600,
                        tooltip="Limpiar registro",
                        on_click=self._clear_log,
                    ),
                ], spacing=8),
                ft.Divider(height=1, color=DriveTheme.GREY_200),
                ft.Container(content=self._log_column, height=200, padding=ft.padding.all(8)),
            ], spacing=8),
            **DriveTheme.get_card_style(),
            padding=16,
        )

    # ── Logic ────────────────────────────────────────────────────────────────

    def _on_browse_click(self, e):
        """Abre el dialogo de selección de carpeta."""
        self._picker.get_directory_path()

    def _on_picker_result(self, e: ft.FilePickerResultEvent):
        """Maneja la selección de carpeta desde el File Picker."""
        if e.path:
            self._tf_guardar.value = e.path
            self._tf_guardar.update()

    def _save_config(self, e):
        data = {
            "carpeta_outlook":     self._tf_outlook.value,
            "correo_remitente":    self._tf_remitente.value,
            "correo_destinatario": self._tf_destinatario.value,
            "carpeta_guardar":     self._tf_guardar.value,
            "carpeta_trabajo":     self._tf_guardar.value,  # Sincronizar con Gestión FACS
        }
        save_config(data)
        self._log("Configuracion guardada correctamente.")

        # Notificar a gui.py para reconstruir sidebar con nuevas estadísticas
        if "on_config_change" in self.page.data:
            self.page.data["on_config_change"]()

    def _run_download(self, e):
        self._run_btn.disabled = True
        self._run_btn.update()
        threading.Thread(target=self._do_download, daemon=True).start()

    def _do_download(self):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            from logic.facs_downloader import DescargadorFacturas
            descargador = DescargadorFacturas(log_callback=self._log)
            descargador.descargar_facturas_etapa(
                carpeta_outlook=self._tf_outlook.value,
                carpeta_guardar=self._tf_guardar.value,
                correo_remitente=self._tf_remitente.value,
            )
        except Exception as ex:
            self._log(f"Error: {ex}")
        finally:
            pythoncom.CoUninitialize()
            self._run_btn.disabled = False
            self._run_btn.update()

    def _log(self, msg: str):
        self._log_column.controls.append(
            ft.Text(msg, size=12, color=DriveTheme.GREY_800, selectable=True)
        )
        try:
            self._log_column.update()
        except Exception:
            pass

    def _clear_log(self, e):
        self._log_column.controls.clear()
        self._log_column.update()

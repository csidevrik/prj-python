# =============================
# pages/facs_manager_page.py
# =============================
import flet as ft
import threading
from config.theme import AppTheme as T
from logic import facs_manager as fm


# ── Definición de acciones ─────────────────────────────────────────────────────
# Para agregar una acción nueva: añade un dict aquí.
ACTIONS = [
    {
        "key":   "firefox",
        "label": "Ver PDFs en Firefox",
        "desc":  "Abre todos los PDFs de la carpeta en Firefox, ordenados por fecha de modificación.",
        "icon":  ft.Icons.OPEN_IN_BROWSER,
        "fn":    lambda folder, log: fm.open_pdf_with_firefox(folder, log),
    },
    {
        "key":   "chrome",
        "label": "Ver PDFs en Chrome",
        "desc":  "Abre todos los PDFs de la carpeta en Chrome, ordenados por fecha de modificación.",
        "icon":  ft.Icons.OPEN_IN_BROWSER,
        "fn":    lambda folder, log: fm.open_pdf_with_chrome(folder, log),
    },
    {
        "key":   "dupes",
        "label": "Eliminar duplicados",
        "desc":  "Detecta y elimina archivos duplicados por hash SHA-256. Conserva el más antiguo.",
        "icon":  ft.Icons.FILTER_NONE_OUTLINED,
        "fn":    lambda folder, log: fm.remove_duplicate_files(folder, log),
    },
    {
        "key":   "prefix",
        "label": 'Eliminar prefijo "RIDE_"',
        "desc":  'Renombra todos los PDFs quitando el prefijo "RIDE_" del nombre.',
        "icon":  ft.Icons.TEXT_FIELDS_OUTLINED,
        "fn":    lambda folder, log: fm.remove_prefix_files_pdf(folder, "RIDE_", log),
    },
    {
        "key":   "rename",
        "label": "Renombrar con XML",
        "desc":  "Renombra pares XML+PDF usando los atributos del XML (estab, ptoEmi, secuencial, instalación).",
        "icon":  ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
        "fn":    lambda folder, log: fm.rename_files_with_attributes(folder, log),
    },
    {
        "key":   "proc_fac",
        "label": "Procesar facturas XML",
        "desc":  "Lee todos los XMLs de facturas y genera facturas.json + facturas.csv ordenados por código.",
        "icon":  ft.Icons.RECEIPT_LONG_OUTLINED,
        "fn":    lambda folder, log: fm.process_all_xml_facs(folder, log),
    },
    {
        "key":   "proc_ret",
        "label": "Procesar retenciones XML",
        "desc":  "Limpia y procesa XMLs de retenciones. Genera retenciones.json + retenciones.csv.",
        "icon":  ft.Icons.DESCRIPTION_OUTLINED,
        "fn":    lambda folder, log: fm.process_all_xml_rets(folder, log),
    },
]


class FacsManagerPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self._running = False

        # ── Folder picker ──────────────────────────────────────────────────
        self._folder_field = ft.TextField(
            value=page.session.get("gfacs_folder") or "",
            hint_text="Selecciona o escribe la ruta de la carpeta...",
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            text_size=13,
            expand=True,
            on_change=self._on_folder_change,
        )
        self._picker = ft.FilePicker(on_result=self._on_picker_result)
        page.overlay.append(self._picker)

        # ── Log ────────────────────────────────────────────────────────────
        self._log_col = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=3,
            expand=True,
        )
        self._log_visible = ft.Ref[ft.Container]()

    # ── Build ──────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Container(
                        content=ft.Column(
                            [
                                self._build_folder_row(),
                                ft.Container(height=20),
                                self._build_cards_grid(),
                                ft.Container(height=20),
                                self._build_log_panel(),
                            ],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=28, vertical=20),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            bgcolor=T.SURFACE_VARIANT,
        )

    # ── Header ─────────────────────────────────────────────────────────────

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.FOLDER_SPECIAL_OUTLINED, size=24, color=T.PRIMARY),
                        bgcolor=ft.Colors.with_opacity(0.1, T.PRIMARY),
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Gestión FACS", size=18, weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
                            ft.Text(
                                "Procesamiento de facturas y retenciones XML del SRI Ecuador",
                                size=12,
                                color=T.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                    ),
                ],
                spacing=14,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=T.SURFACE,
        )

    # ── Folder row ─────────────────────────────────────────────────────────

    def _build_folder_row(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Carpeta de trabajo",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=T.ON_SURFACE,
                    ),
                    ft.Text(
                        "Todas las acciones operan sobre esta carpeta.",
                        size=12,
                        color=T.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        [
                            self._folder_field,
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=16, color=T.ON_PRIMARY),
                                        ft.Text("Explorar", size=13, color=T.ON_PRIMARY),
                                    ],
                                    spacing=6,
                                    tight=True,
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=T.PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                                ),
                                on_click=lambda e: self._picker.get_directory_path(),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=4,
            ),
            **T.get_card_style(),
            padding=20,
        )

    # ── Cards grid ─────────────────────────────────────────────────────────

    def _build_cards_grid(self):
        return ft.GridView(
            runs_count=3,
            max_extent=340,
            child_aspect_ratio=1.6,
            spacing=14,
            run_spacing=14,
            controls=[self._build_action_card(action) for action in ACTIONS],
            height=320,
        )

    def _build_action_card(self, action: dict) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(action["icon"], size=20, color=T.PRIMARY),
                                bgcolor=ft.Colors.with_opacity(0.1, T.PRIMARY),
                                border_radius=8,
                                padding=8,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                icon_color=T.PRIMARY,
                                icon_size=20,
                                tooltip="Ejecutar",
                                on_click=lambda e, a=action: self._run_action(a),
                            ),
                        ],
                    ),
                    ft.Text(
                        action["label"],
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=T.ON_SURFACE,
                    ),
                    ft.Text(
                        action["desc"],
                        size=11,
                        color=T.ON_SURFACE_VARIANT,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=6,
            ),
            **T.get_card_style(),
            padding=16,
            on_click=lambda e, a=action: self._run_action(a),
            ink=True,
        )

    # ── Log panel ──────────────────────────────────────────────────────────

    def _build_log_panel(self):
        return ft.Container(
            ref=self._log_visible,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.TERMINAL, size=16, color=T.ON_SURFACE_VARIANT),
                            ft.Text(
                                "Registro de actividad",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=16,
                                icon_color=T.ON_SURFACE_VARIANT,
                                tooltip="Limpiar registro",
                                on_click=self._clear_log,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Container(
                        content=self._log_col,
                        height=180,
                        padding=ft.padding.all(8),
                        bgcolor=T.SURFACE_VARIANT,
                        border_radius=8,
                    ),
                ],
                spacing=8,
            ),
            **T.get_card_style(),
            padding=16,
        )

    # ── Action execution ───────────────────────────────────────────────────

    def _run_action(self, action: dict):
        folder = self._folder_field.value.strip()
        if not folder:
            self._log("Selecciona una carpeta de trabajo antes de ejecutar.")
            return
        if self._running:
            self._log("Hay una accion en curso. Espera a que termine.")
            return

        self._log(f"[{action['label']}] Iniciando en: {folder}")
        self._running = True
        threading.Thread(
            target=self._execute_in_thread,
            args=(action, folder),
            daemon=True,
        ).start()

    def _execute_in_thread(self, action: dict, folder: str):
        try:
            action["fn"](folder, self._log)
        except Exception as ex:
            self._log(f"Error: {ex}")
        finally:
            self._running = False

    # ── Log helpers ────────────────────────────────────────────────────────

    def _log(self, msg: str):
        color = T.ERROR if msg.startswith("Error") else T.ON_SURFACE
        self._log_col.controls.append(
            ft.Text(msg, size=12, color=color, selectable=True)
        )
        try:
            self._log_col.update()
        except Exception:
            pass

    def _clear_log(self, e):
        self._log_col.controls.clear()
        self._log_col.update()

    # ── Folder picker callbacks ─────────────────────────────────────────────

    def _on_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self._folder_field.value = e.path
            self.page.session["gfacs_folder"] = e.path
            self._folder_field.update()

    def _on_folder_change(self, e):
        self.page.session["gfacs_folder"] = e.control.value

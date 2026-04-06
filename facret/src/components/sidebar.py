# =============================
# components/sidebar.py
# =============================
import flet as ft
from typing import Callable, Optional
from config.theme import AppTheme as T
from config.menu_config import MENU_ITEMS, flat_menu


# Datos del usuario — en el futuro vendrán de un modelo/sesión real
_USER_NAME    = "Carlos Sigua"
_USER_EMAIL   = "csigua@emov.gob.ec"
_USER_INITIALS = "CS"


class DriveSidebarComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_item = "home"
        self._expanded = True
        self._sidebar_width = 280
        self.on_nav_change: Optional[Callable[[str], None]] = None

        # ── Search widgets ────────────────────────────────────────────────
        self._search_field = ft.TextField(
            hint_text="Buscar en menús...",
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            border_radius=20,
            text_size=13,
            height=36,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=0),
            expand=True,
            on_change=self._on_search_change,
        )
        self._results_list = ft.Column(controls=[], spacing=2)
        self._results_card = ft.Container(
            content=self._results_list,
            **T.get_card_style(),
            padding=8,
            visible=False,
        )
        self._nav_column = ft.Column([], spacing=4)

    # ── Build ─────────────────────────────────────────────────────────────

    def build(self):
        self._nav_column.controls = self._build_nav_items()

        self._container = ft.Container(
            width=self._sidebar_width,
            # SIN expand=True aquí: dentro de un Row, expand afecta el ANCHO.
            # La altura la hereda del Row padre que sí tiene expand=True.
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                [
                    # ── Buscador + botón compacto ────────────────────────
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.CREATE_NEW_FOLDER_OUTLINED,
                                    icon_color=T.ON_SURFACE_VARIANT,
                                    tooltip="Nueva acción",
                                    icon_size=20,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        bgcolor=T.SURFACE,
                                        shadow_color=ft.Colors.with_opacity(
                                            0.15, ft.Colors.BLACK
                                        ),
                                        elevation=2,
                                    ),
                                    on_click=self._on_new_click,
                                ),
                                self._search_field,
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    ),
                    # ── Resultados de búsqueda ───────────────────────────
                    ft.Container(
                        content=self._results_card,
                        padding=ft.padding.only(left=8, right=8, bottom=4),
                    ),
                    # ── Menú de navegación ───────────────────────────────
                    self._nav_column,
                    # ── Spacer: empuja el footer al fondo ────────────────
                    ft.Container(expand=True),
                    ft.Divider(height=1, color=T.OUTLINE),
                    # ── Almacenamiento ───────────────────────────────────
                    self._build_storage_section(),
                    ft.Divider(height=1, color=T.OUTLINE),
                    # ── Footer de usuario (estilo ChatGPT) ───────────────
                    self._build_user_footer(),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=T.SURFACE,
        )
        return self._container

    # ── Nav items ─────────────────────────────────────────────────────────

    def _build_nav_items(self):
        return [
            self._create_nav_item(item.key, item.icon, item.label)
            for item in MENU_ITEMS
        ]

    def _create_nav_item(self, key: str, icon: str, text: str):
        is_selected = self.selected_item == key
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    icon,
                    color=T.PRIMARY if is_selected else T.ON_SURFACE_VARIANT,
                    size=20,
                ),
                title=ft.Text(
                    text,
                    color=T.PRIMARY if is_selected else T.ON_SURFACE,
                    size=14,
                    weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.W_400,
                ),
                on_click=lambda e, k=key: self._on_nav_click(k),
            ),
            bgcolor=(
                ft.Colors.with_opacity(0.1, T.PRIMARY) if is_selected else None
            ),
            margin=ft.margin.symmetric(horizontal=8),
            border_radius=8,
        )

    # ── Storage section ───────────────────────────────────────────────────

    def _build_storage_section(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Almacenamiento", size=13, color=T.ON_SURFACE_VARIANT),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.CLOUD_OUTLINED,
                                            size=14,
                                            color=T.ON_SURFACE_VARIANT,
                                        ),
                                        ft.Text(
                                            "15 GB de 15 GB",
                                            size=11,
                                            color=T.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    spacing=6,
                                ),
                                ft.Container(
                                    content=ft.ProgressBar(
                                        value=0.8,
                                        height=3,
                                        bgcolor=T.OUTLINE,
                                        color=T.PRIMARY,
                                    ),
                                    margin=ft.margin.symmetric(vertical=6),
                                ),
                            ]
                        ),
                        padding=ft.padding.symmetric(horizontal=0, vertical=4),
                    ),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

    # ── User footer ───────────────────────────────────────────────────────

    def _build_user_footer(self):
        """
        Footer fijo al fondo del sidebar.
        Muestra nombre/email del usuario y un PopupMenu con opciones.
        Inspirado en el pie de página de ChatGPT.
        """
        popup = ft.PopupMenuButton(
            icon=ft.Icons.MORE_HORIZ,
            icon_color=T.ON_SURFACE_VARIANT,
            tooltip="Opciones",
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=T.ON_SURFACE_VARIANT),
                            ft.Text("Perfil", size=13, color=T.ON_SURFACE),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e: self._on_system_nav("profile"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=16, color=T.ON_SURFACE_VARIANT),
                            ft.Text("Configuración", size=13, color=T.ON_SURFACE),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e: self._on_system_nav("settings"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HELP_OUTLINE, size=16, color=T.ON_SURFACE_VARIANT),
                            ft.Text("Ayuda", size=13, color=T.ON_SURFACE),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e: self._on_system_nav("help"),
                ),
                ft.PopupMenuItem(),  # divider
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT, size=16, color=T.ERROR),
                            ft.Text("Cerrar sesión", size=13, color=T.ERROR),
                        ],
                        spacing=10,
                    ),
                    on_click=self._on_logout,
                ),
            ],
        )

        return ft.Container(
            content=ft.Row(
                [
                    # Avatar con iniciales
                    T.avatar_style(_USER_INITIALS, size=34),
                    # Nombre y email
                    ft.Column(
                        [
                            ft.Text(
                                _USER_NAME,
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color=T.ON_SURFACE,
                            ),
                            ft.Text(
                                _USER_EMAIL,
                                size=11,
                                color=T.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=1,
                        tight=True,
                        expand=True,
                    ),
                    # Menú de opciones
                    popup,
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            bgcolor=T.SURFACE,
        )

    # ── Search logic ──────────────────────────────────────────────────────

    def _on_search_change(self, e):
        query = e.control.value.strip().lower()
        if not query:
            self._results_card.visible = False
            self._nav_column.visible = True
            self._results_list.controls = []
        else:
            matches = [
                (item, parent)
                for item, parent in flat_menu()
                if query in item.label.lower()
            ]
            self._build_results(matches)
            self._results_card.visible = bool(matches)
            self._nav_column.visible = False
        self.page.update()

    def _build_results(self, matches: list):
        self._results_list.controls = [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(item.icon, size=18, color=T.PRIMARY),
                    title=ft.Text(item.label, size=13, color=T.ON_SURFACE),
                    subtitle=(
                        ft.Text(f"en {parent.label}", size=11, color=T.ON_SURFACE_VARIANT)
                        if parent
                        else None
                    ),
                    dense=True,
                    on_click=lambda e, k=item.key: self._on_result_click(k),
                ),
                border_radius=6,
            )
            for item, parent in matches
        ]

    def _on_result_click(self, key: str):
        self.selected_item = key
        self._search_field.value = ""
        self._results_card.visible = False
        self._results_list.controls = []
        self._nav_column.visible = True
        self._nav_column.controls = self._build_nav_items()
        if self.on_nav_change:
            self.on_nav_change(key)
        self.page.update()

    # ── Nav click ─────────────────────────────────────────────────────────

    def _on_nav_click(self, key: str):
        self.selected_item = key
        self._nav_column.controls = self._build_nav_items()
        if self.on_nav_change:
            self.on_nav_change(key)
        self.page.update()

    def _on_system_nav(self, key: str):
        """Navega a secciones del sistema (settings, profile, help)."""
        if self.on_nav_change:
            self.on_nav_change(key)

    def _on_logout(self, e):
        print("Logout")

    # ── Misc ──────────────────────────────────────────────────────────────

    def _on_new_click(self, e):
        pass

    def _toggle_sidebar(self, e):
        self._expanded = not self._expanded
        self._container.width = self._sidebar_width if self._expanded else 0
        self._container.update()

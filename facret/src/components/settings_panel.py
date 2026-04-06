# =============================
# components/settings_panel.py
# =============================
"""
Panel de configuración de FACRET.
Sección principal: selector visual de paleta de colores.

Cómo funciona el cambio de tema:
  - Se actualizan los atributos de clase en AppTheme (PRIMARY, SEED, etc.)
  - Se llama page.theme = AppTheme.get_theme() → Flet refresca su color scheme
  - Los widgets ya construidos (sidebar, header) mantienen sus colores hasta
    que se recargan. La forma más limpia de aplicar el tema completo es
    reiniciando la vista o navegando a otra pantalla y volviendo.
"""
import flet as ft
from config.theme import AppTheme as T


# ── Paletas predefinidas ───────────────────────────────────────────────────────
# Para agregar un tema nuevo: añade un dict con los 4 campos obligatorios.
PRESET_THEMES = [
    {
        "name": "Google Blue",
        "desc": "Clásico y familiar",
        "seed":               "#1a73e8",
        "primary":            "#1a73e8",
        "primary_container":  "#d3e3fd",
        "on_surface":         "#3c4043",
    },
    {
        "name": "Teal Verde",
        "desc": "Fresco y profesional",
        "seed":               "#0d9488",
        "primary":            "#0d9488",
        "primary_container":  "#ccfbf1",
        "on_surface":         "#134e4a",
    },
    {
        "name": "Índigo",
        "desc": "Moderno y creativo",
        "seed":               "#4f46e5",
        "primary":            "#4f46e5",
        "primary_container":  "#e0e7ff",
        "on_surface":         "#1e1b4b",
    },
    {
        "name": "Navy Slate",
        "desc": "Serio e institucional",
        "seed":               "#1e40af",
        "primary":            "#1e40af",
        "primary_container":  "#dbeafe",
        "on_surface":         "#1e3a5f",
    },
    {
        "name": "Emerald",
        "desc": "Natural y calmado",
        "seed":               "#059669",
        "primary":            "#059669",
        "primary_container":  "#d1fae5",
        "on_surface":         "#064e3b",
    },
    {
        "name": "Rose",
        "desc": "Cálido y cercano",
        "seed":               "#e11d48",
        "primary":            "#e11d48",
        "primary_container":  "#ffe4e6",
        "on_surface":         "#4c0519",
    },
]


class SettingsPanel:
    def __init__(self, page: ft.Page):
        self.page = page
        self._active_seed = T.SEED
        self._status_text = ft.Text("", size=12, color=T.SUCCESS)

    # ── Build ─────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Container(
                        content=ft.Column(
                            [
                                self._build_theme_section(),
                                ft.Container(height=24),
                                self._build_about_section(),
                            ],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=32, vertical=20),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            bgcolor=T.SURFACE_VARIANT,
        )

    # ── Header ────────────────────────────────────────────────────────────

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.SETTINGS_OUTLINED,
                            size=24,
                            color=T.PRIMARY,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.1, T.PRIMARY),
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Configuración",
                                size=18,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                            ft.Text(
                                "Personaliza la apariencia de FACRET",
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

    # ── Theme section ──────────────────────────────────────────────────────

    def _build_theme_section(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PALETTE_OUTLINED,
                                size=16,
                                color=T.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                "Paleta de colores",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        "Elige el tema visual de la aplicación. "
                        "El color primario afecta botones, íconos activos y selecciones.",
                        size=12,
                        color=T.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=12),
                    # Grid de tarjetas de paleta
                    ft.GridView(
                        runs_count=3,
                        max_extent=220,
                        child_aspect_ratio=1.4,
                        spacing=12,
                        run_spacing=12,
                        controls=[
                            self._build_theme_card(theme)
                            for theme in PRESET_THEMES
                        ],
                        height=300,
                    ),
                    ft.Container(height=8),
                    self._status_text,
                ],
                spacing=6,
            ),
            **T.get_card_style(),
            padding=20,
        )

    def _build_theme_card(self, theme: dict) -> ft.Container:
        is_active = theme["seed"] == self._active_seed
        primary   = theme["primary"]
        container = theme["primary_container"]

        swatches = ft.Row(
            [
                # Swatch PRIMARY (grande)
                ft.Container(
                    bgcolor=primary,
                    border_radius=ft.border_radius.only(top_left=8, bottom_left=8),
                    expand=2,
                ),
                # Swatch PRIMARY_CONTAINER
                ft.Container(bgcolor=container, expand=1),
                # Swatch SURFACE
                ft.Container(bgcolor="#ffffff", expand=1),
                # Swatch ON_SURFACE
                ft.Container(
                    bgcolor=theme["on_surface"],
                    border_radius=ft.border_radius.only(top_right=8, bottom_right=8),
                    expand=1,
                ),
            ],
            spacing=0,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    # Franja de colores
                    ft.Container(
                        content=swatches,
                        height=52,
                        border_radius=8,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        border=ft.border.all(
                            2,
                            primary if is_active else T.OUTLINE,
                        ),
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        theme["name"],
                                        size=13,
                                        weight=ft.FontWeight.W_500,
                                        color=T.ON_SURFACE,
                                    ),
                                    ft.Text(
                                        theme["desc"],
                                        size=11,
                                        color=T.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=1,
                                tight=True,
                                expand=True,
                            ),
                            # Indicador de activo
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=16,
                                    color=primary,
                                ),
                                visible=is_active,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=0,
            ),
            **T.get_card_style(),
            padding=12,
            on_click=lambda e, th=theme: self._apply_theme(th),
            # Borde resaltado si está activo
            border=ft.border.all(2, primary if is_active else "transparent"),
        )

    # ── About section ─────────────────────────────────────────────────────

    def _build_about_section(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=16,
                                color=T.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                "Acerca de FACRET",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        [
                            ft.Text("Versión", size=13, color=T.ON_SURFACE_VARIANT, expand=True),
                            ft.Text("1.0.0", size=13, color=T.ON_SURFACE),
                        ]
                    ),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Row(
                        [
                            ft.Text("Motor UI", size=13, color=T.ON_SURFACE_VARIANT, expand=True),
                            ft.Text("Flet (Flutter)", size=13, color=T.ON_SURFACE),
                        ]
                    ),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Row(
                        [
                            ft.Text("Fuente de facturas", size=13, color=T.ON_SURFACE_VARIANT, expand=True),
                            ft.Text("Outlook local (COM)", size=13, color=T.ON_SURFACE),
                        ]
                    ),
                ],
                spacing=6,
            ),
            **T.get_card_style(),
            padding=20,
        )

    # ── Apply theme ───────────────────────────────────────────────────────

    def _apply_theme(self, theme: dict):
        """
        Aplica el tema seleccionado:
          1. Actualiza los atributos de clase en AppTheme.
          2. Cambia page.theme para que Flet refresque su esquema de Material.
          3. Recarga el panel para que los bordes activos se actualicen.
        """
        # Actualizar la clase AppTheme
        T.SEED               = theme["seed"]
        T.PRIMARY            = theme["primary"]
        T.PRIMARY_CONTAINER  = theme["primary_container"]
        T.ON_SURFACE         = theme["on_surface"]
        # Mantener alias de compat sincronizados
        T.PRIMARY_BLUE       = T.PRIMARY

        # Actualizar el tema de Flet
        self.page.theme = T.get_theme()

        # Actualizar estado interno y refrescar las tarjetas
        self._active_seed = theme["seed"]
        self._status_text.value = f"✅ Tema «{theme['name']}» aplicado. Navega a otra sección para verlo completo."

        self.page.update()

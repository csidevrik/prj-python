# =============================
# config/theme.py
# =============================
"""
Paleta de colores semántica de FACRET.

Para cambiar el tema completo de la app:
  1. Cambia SEED al nuevo color principal.
  2. Actualiza PRIMARY y PRIMARY_CONTAINER con los valores que genera
     el Material Theme Builder: https://m3.material.io/theme-builder

Regla de uso:
  - Usa nombres SEMÁNTICOS en código nuevo (PRIMARY, ON_SURFACE, OUTLINE…)
  - Los alias legacy (PRIMARY_BLUE, GREY_*) siguen funcionando para no
    romper código existente, pero evita usarlos en código nuevo.
"""
import flet as ft


class AppTheme:
    # ── Color semilla ──────────────────────────────────────────────────────
    # Paleta teal — evoca agua, va con la identidad de ETAPA (empresa agua Cuenca)
    # Para cambiar: edita SEED y los valores PRIMARY/PRIMARY_CONTAINER
    SEED = "#007a8c"

    # ── Primary ───────────────────────────────────────────────────────────
    # Acciones principales: botones, íconos activos, links, selección en sidebar
    PRIMARY           = "#0b5f78"   # teal oscuro
    ON_PRIMARY        = "#ffffff"   # texto/ícono SOBRE PRIMARY
    PRIMARY_CONTAINER = "#b8dde6"   # teal suave — hover, ítem seleccionado en sidebar

    # ── Secondary ─────────────────────────────────────────────────────────
    # Acentos, badges, estado activo secundario
    SECONDARY         = "#0097a7"   # teal medio
    ON_SECONDARY      = "#ffffff"
    SECONDARY_CONTAINER = "#ccedf1" # teal muy suave

    # ── Surface ───────────────────────────────────────────────────────────
    # Fondos de componentes (cards, sidebar, header)
    SURFACE           = "#ffffff"
    SURFACE_VARIANT   = "#f0f7f8"   # fondo de la página — blanco con tinte teal
    ON_SURFACE        = "#1a2b2e"   # texto principal
    ON_SURFACE_VARIANT = "#3d5a5e"  # texto secundario, placeholders, subtítulos

    # ── Outline ───────────────────────────────────────────────────────────
    # Bordes, separadores, dividers
    OUTLINE           = "#c2d8db"   # borde teal suave
    OUTLINE_VARIANT   = "#dce9eb"

    # ── Error / Success ───────────────────────────────────────────────────
    ERROR             = "#ba1a1a"
    ON_ERROR          = "#ffffff"
    SUCCESS           = "#1a7a4a"   # verde confirmación (logs de descarga exitosa)

    # ── Backward compat ───────────────────────────────────────────────────
    # Alias para código existente — en código NUEVO usa los nombres semánticos.
    PRIMARY_BLUE  = PRIMARY
    SURFACE_WHITE = SURFACE
    GREY_50       = SURFACE_VARIANT
    GREY_100      = "#e4eef0"
    GREY_200      = OUTLINE
    GREY_600      = ON_SURFACE_VARIANT
    GREY_800      = ON_SURFACE

    # ── Theme de Flet ─────────────────────────────────────────────────────

    @staticmethod
    def get_theme() -> ft.Theme:
        return ft.Theme(
            color_scheme_seed=AppTheme.SEED,  # "#007a8c" teal
            visual_density=ft.VisualDensity.COMPACT,
        )

    # ── Estilos reutilizables ─────────────────────────────────────────────

    @staticmethod
    def get_card_style() -> dict:
        """Estilo estándar para tarjetas/panels."""
        return {
            "bgcolor": AppTheme.SURFACE,
            "border_radius": 12,
            "shadow": ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        }

    @staticmethod
    def get_button_style() -> dict:
        """Estilo estándar para botones."""
        return {
            "style": ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            )
        }

    @staticmethod
    def avatar_style(initials: str, size: int = 32) -> ft.Container:
        """Genera un avatar circular con iniciales."""
        return ft.Container(
            content=ft.Text(
                initials.upper()[:2],
                size=size * 0.4,
                weight=ft.FontWeight.W_600,
                color=AppTheme.ON_PRIMARY,
            ),
            width=size,
            height=size,
            border_radius=size,
            bgcolor=AppTheme.PRIMARY,
            alignment=ft.alignment.center,
        )


# Alias para que el código existente que importa DriveTheme siga funcionando
DriveTheme = AppTheme

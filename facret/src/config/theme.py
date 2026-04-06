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
    # Cambia este valor y regenera la paleta en m3.material.io/theme-builder
    SEED = "#1a73e8"

    # ── Primary ───────────────────────────────────────────────────────────
    # Acciones principales: botones, íconos activos, links
    PRIMARY           = "#1a73e8"
    ON_PRIMARY        = "#ffffff"   # texto/ícono SOBRE el color PRIMARY
    PRIMARY_CONTAINER = "#d3e3fd"   # fondo suave: hover, ítem seleccionado

    # ── Surface ───────────────────────────────────────────────────────────
    # Fondos de componentes (cards, sidebar, header)
    SURFACE           = "#ffffff"
    SURFACE_VARIANT   = "#f8f9fa"   # fondo de la página / áreas secundarias
    ON_SURFACE        = "#3c4043"   # texto principal sobre surface
    ON_SURFACE_VARIANT = "#5f6368"  # texto secundario, placeholders, subtítulos

    # ── Outline ───────────────────────────────────────────────────────────
    # Bordes, separadores, dividers
    OUTLINE           = "#e8eaed"
    OUTLINE_VARIANT   = "#dadce0"

    # ── Error / Success ───────────────────────────────────────────────────
    ERROR             = "#d93025"
    ON_ERROR          = "#ffffff"
    SUCCESS           = "#1e8e3e"   # logs positivos, confirmaciones

    # ── Backward compat ───────────────────────────────────────────────────
    # Estos alias permiten que el código existente siga funcionando.
    # En código NUEVO usa los nombres semánticos de arriba.
    PRIMARY_BLUE  = PRIMARY
    SURFACE_WHITE = SURFACE
    GREY_50       = SURFACE_VARIANT
    GREY_100      = "#f1f3f4"
    GREY_200      = OUTLINE
    GREY_600      = ON_SURFACE_VARIANT
    GREY_800      = ON_SURFACE

    # ── Theme de Flet ─────────────────────────────────────────────────────

    @staticmethod
    def get_theme() -> ft.Theme:
        return ft.Theme(
            color_scheme_seed=AppTheme.SEED,
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

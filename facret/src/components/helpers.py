# =============================
# components/helpers.py
# =============================
"""
Helpers visuales reutilizables para pages.
Reduce duplicación de código de componentes comunes.
"""
import flet as ft
from config.theme import AppTheme as T


def build_stat_chip(label: str, value: str, icon: str | None = None) -> ft.Container:
    """
    Chip genérico para mostrar etiqueta + valor (ej: "Estado: ACTIVO").

    Args:
        label: Texto de la etiqueta ("Estado", "Tamaño", etc.)
        value: Valor a mostrar ("ACTIVO", "234 MB", etc.)
        icon: Ícono opcional (ft.Icons.XXXX)

    Returns:
        Container con el chip diseñado
    """
    children = [
        ft.Text(label, size=9, color=T.ON_SURFACE_VARIANT),
        ft.Text(value, size=11, weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
    ]

    if icon:
        children.insert(0, ft.Icon(icon, size=14, color=T.PRIMARY))

    return ft.Container(
        content=ft.Column(
            children,
            spacing=1,
            tight=True,
        ),
        bgcolor=T.SURFACE,
        border=ft.border.all(1, T.OUTLINE),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
    )


def build_status_text(text: str, status: str, size: int = 13) -> ft.Text:
    """
    Texto con color mapeado según estado.

    Args:
        text: Texto a mostrar
        status: Estado ("ACTIVE", "CANCELED", "UP", "DOWN", etc.)
        size: Tamaño de fuente

    Returns:
        Text widget con color apropiado
    """
    color_map = {
        "ACTIVE": T.SUCCESS,
        "UP": T.SUCCESS,
        "CANCELED": T.ERROR,
        "DOWN": T.ERROR,
    }
    color = color_map.get(status, T.ON_SURFACE_VARIANT)

    return ft.Text(text, size=size, color=color, weight=ft.FontWeight.W_500)


def build_info_row(label: str, value: str, icon: str | None = None) -> ft.Row:
    """
    Fila de información: ícono + etiqueta + valor.

    Args:
        label: Etiqueta descriptiva
        value: Valor a mostrar
        icon: Ícono opcional (ft.Icons.XXXX)

    Returns:
        Row con la información formateada
    """
    children = []

    if icon:
        children.append(ft.Icon(icon, size=14, color=T.ON_SURFACE_VARIANT))

    children.extend([
        ft.Text(label, size=11, color=T.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
        ft.Text(value, size=11, color=T.ON_SURFACE, weight=ft.FontWeight.W_600),
    ])

    return ft.Row(children, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def build_divider_section(title: str) -> list[ft.Control]:
    """
    Sección con divider: título + línea divisoria.

    Args:
        title: Título de la sección

    Returns:
        Lista de widgets [título, divider]
    """
    return [
        ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
        ft.Divider(height=1, color=T.OUTLINE),
    ]


def build_action_card(
    icon: str,
    label: str,
    description: str,
    on_click=None,
    color: str | None = None,
) -> ft.Container:
    """
    Tarjeta de acción: ícono + label + descripción.

    Args:
        icon: Ícono (ft.Icons.XXXX)
        label: Título de la acción
        description: Descripción corta
        on_click: Callback al hacer clic
        color: Color del ícono (default PRIMARY)

    Returns:
        Container con la tarjeta de acción
    """
    if color is None:
        color = T.PRIMARY

    return ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=24, color=color),
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        border_radius=8,
                        padding=8,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW,
                        icon_color=color,
                        icon_size=20,
                    ),
                ]),
                ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
                ft.Text(
                    description,
                    size=11,
                    color=T.ON_SURFACE_VARIANT,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=8,
        ),
        **T.get_card_style(),
        padding=12,
        on_click=on_click,
        ink=True,
    )


def build_labeled_field(
    label: str,
    field: ft.Control,
    icon: str | None = None,
    helper_text: str = "",
) -> ft.Container:
    """
    Campo de entrada con etiqueta e ícono opcional.

    Args:
        label: Etiqueta descriptiva
        field: Control de entrada (TextField, etc.)
        icon: Ícono opcional
        helper_text: Texto de ayuda debajo del campo

    Returns:
        Container con el campo formateado
    """
    children = [
        ft.Text(label, size=11, color=T.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
        field,
    ]

    if helper_text:
        children.append(
            ft.Text(helper_text, size=9, color=T.ON_SURFACE_VARIANT, italic=True)
        )

    row_children = []
    if icon:
        row_children.append(
            ft.Container(
                content=ft.Icon(icon, size=18, color=T.ON_SURFACE_VARIANT),
                width=36,
            )
        )

    row_children.append(ft.Column(children, spacing=2, expand=True))

    return ft.Container(
        content=ft.Row(row_children, spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
        padding=ft.padding.only(bottom=16),
    )

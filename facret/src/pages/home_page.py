# =============================
# pages/home_page.py
# =============================
import flet as ft
from config.theme import AppTheme as T


# ── Datos del dashboard ────────────────────────────────────────────────────────
# Cuando los modelos Factura/Retencion estén conectados, reemplaza estos valores
# con llamadas a la capa logic/ o a una función de resumen del modelo.
def _get_stats() -> dict:
    return {
        "facturas":        0,
        "retenciones":     0,
        "ultima_descarga": "—",
        "carpeta":         "—",
    }

def _get_recent() -> list:
    # Retornará lista de dicts con keys: nombre, tipo, fecha
    return []


class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self._on_navigate = None   # se asigna desde gui.py si se necesita navegar

    def build(self) -> ft.Control:
        stats  = _get_stats()
        recent = _get_recent()

        return ft.Container(
            content=ft.Column(
                [
                    self._build_welcome(),
                    ft.Container(
                        content=ft.Column(
                            [
                                self._build_stats_row(stats),
                                ft.Container(height=24),
                                self._build_recent_section(recent),
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

    # ── Welcome ───────────────────────────────────────────────────────────────

    def _build_welcome(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "Bienvenido a FACRET",
                                size=20,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                            ft.Text(
                                "Resumen de actividad de descarga de facturas ETAPA",
                                size=13,
                                color=T.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=4,
                        tight=True,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=16, color=T.ON_PRIMARY),
                                ft.Text("Ir a Download FACS", size=13, color=T.ON_PRIMARY),
                            ],
                            spacing=8,
                            tight=True,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=T.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        ),
                        on_click=self._go_to_download,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=28, vertical=18),
            bgcolor=T.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(1, T.OUTLINE)),
        )

    # ── Stats ─────────────────────────────────────────────────────────────────

    def _build_stats_row(self, stats: dict):
        return ft.Row(
            [
                self._stat_card(
                    icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                    label="Facturas descargadas",
                    value=str(stats["facturas"]),
                    color=T.PRIMARY,
                ),
                self._stat_card(
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    label="Retenciones",
                    value=str(stats["retenciones"]),
                    color=T.SECONDARY,
                ),
                self._stat_card(
                    icon=ft.Icons.HISTORY,
                    label="Ultima descarga",
                    value=stats["ultima_descarga"],
                    color=T.ON_SURFACE_VARIANT,
                    value_size=16,
                ),
                self._stat_card(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    label="Carpeta destino",
                    value=stats["carpeta"],
                    color=T.ON_SURFACE_VARIANT,
                    value_size=13,
                ),
            ],
            spacing=16,
        )

    def _stat_card(
        self,
        icon: str,
        label: str,
        value: str,
        color: str,
        value_size: int = 28,
    ) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=20, color=color),
                                bgcolor=ft.Colors.with_opacity(0.1, color),
                                border_radius=8,
                                padding=8,
                            ),
                        ],
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        value,
                        size=value_size,
                        weight=ft.FontWeight.W_700,
                        color=T.ON_SURFACE,
                    ),
                    ft.Text(
                        label,
                        size=12,
                        color=T.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=2,
            ),
            **T.get_card_style(),
            padding=20,
            expand=True,
        )

    # ── Recent activity ───────────────────────────────────────────────────────

    def _build_recent_section(self, recent: list):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=16, color=T.ON_SURFACE_VARIANT),
                            ft.Text(
                                "Actividad reciente",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=T.ON_SURFACE,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=T.OUTLINE),
                    ft.Container(height=8),
                    self._build_recent_list(recent),
                ],
                spacing=8,
            ),
            **T.get_card_style(),
            padding=20,
        )

    def _build_recent_list(self, recent: list) -> ft.Control:
        if not recent:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.INBOX_OUTLINED,
                            size=48,
                            color=T.OUTLINE,
                        ),
                        ft.Text(
                            "Sin actividad reciente",
                            size=14,
                            color=T.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            "Las facturas descargadas aparecerán aquí",
                            size=12,
                            color=T.OUTLINE,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.symmetric(vertical=32),
            )

        # Cuando haya datos reales: una fila por cada factura reciente
        return ft.Column(
            [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT, color=T.PRIMARY, size=20),
                    title=ft.Text(item["nombre"], size=13),
                    subtitle=ft.Text(item["tipo"], size=11, color=T.ON_SURFACE_VARIANT),
                    trailing=ft.Text(item["fecha"], size=11, color=T.ON_SURFACE_VARIANT),
                )
                for item in recent
            ],
            spacing=4,
        )

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_to_download(self, e):
        # Usa page.data para llegar al router de gui.py si está disponible
        on_nav = (self.page.data or {}).get("on_navigate")
        if on_nav:
            on_nav("my_drive")

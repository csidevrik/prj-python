import flet as ft
from config.theme import AppTheme as T
from logic.contracts_loader import load_servicios_flat
from logic.contracts_writer import update_servicio, add_evento
from models.models import EnlaceInternet, EnlaceDatos


# ── Helpers ────────────────────────────────────────────────────────────────────

def _estado_color(estado: str) -> str:
    return {
        "ACTIVE":   T.SUCCESS,
        "CANCELED": T.ERROR,
    }.get(estado, T.ON_SURFACE_VARIANT)


def _op_color(estado_op: str) -> str:
    return T.SUCCESS if estado_op == "UP" else T.ERROR


def _display_agencia(s) -> str:
    if isinstance(s, EnlaceInternet):
        ag = s.agencia
        return ag.nombre if ag else s.agencia_id
    ag_a = s.agencia_extremo_a
    ag_b = s.agencia_extremo_b
    nombre_a = ag_a.nombre if ag_a else s.extremo_a
    nombre_b = ag_b.nombre if ag_b else s.extremo_b
    return f"{nombre_a}  ↔  {nombre_b}"


def _matches(s, q: str) -> bool:
    q = q.lower()
    return (
        q in s.cod_serv.lower()
        or q in _display_agencia(s).lower()
        or q in s.grupo.lower()
        or q in s.estado.lower()
        or q in s.bandwidth.lower()
        or q in s.isp.lower()
    )


def _ref_chip(label: str, value: str) -> ft.Container:
    """Chip de solo lectura para mostrar datos del contrato en el diálogo."""
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=9, color=T.ON_SURFACE_VARIANT),
                ft.Text(value, size=11, weight=ft.FontWeight.W_600,
                        color=T.ON_SURFACE),
            ],
            spacing=1, tight=True,
        ),
        bgcolor=T.SURFACE,
        border=ft.border.all(1, T.OUTLINE),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
    )


# ── Page ───────────────────────────────────────────────────────────────────────

class ContractsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self._servicios = load_servicios_flat()
        self._selected: EnlaceInternet | EnlaceDatos | None = None
        self._search_query = ""

        # ── controles que se actualizan en lugar de reconstruirse ──────────
        self._search_tf = ft.TextField(
            hint_text="Buscar por agencia, código, grupo, estado...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            text_size=13,
            height=42,
            expand=True,
            on_change=self._on_search,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        )
        self._edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED,
            icon_color=T.PRIMARY,
            tooltip="Editar servicio",
            disabled=True,
            on_click=self._on_edit,
        )
        self._del_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=T.ERROR,
            tooltip="Eliminar servicio",
            disabled=True,
            on_click=self._on_delete,
        )

        # refs para actualizar partes de la UI sin reconstruir todo
        self._table_ref  = ft.Ref[ft.DataTable]()
        self._detail_ref = ft.Ref[ft.Container]()

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
                                self._build_toolbar(),
                                ft.Container(height=12),
                                ft.Row(
                                    [
                                        # tabla: siempre visible, se expande
                                        ft.Container(
                                            content=self._build_table_card(),
                                            expand=True,
                                        ),
                                        # detalle: a la derecha, aparece al seleccionar
                                        self._build_detail_panel(),
                                    ],
                                    spacing=16,
                                    expand=True,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                ),
                            ],
                            spacing=0,
                            expand=True,
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
        total = sum(s.valor_mensual for s in self._servicios)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=24, color=T.PRIMARY),
                        bgcolor=ft.Colors.with_opacity(0.1, T.PRIMARY),
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Contratos ETAPA", size=18,
                                    weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
                            ft.Text(
                                f"Servicios: {len(self._servicios)}  ·  "
                                f"Total mensual: ${total:,.2f}",
                                size=12, color=T.ON_SURFACE_VARIANT,
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

    # ── Toolbar (search + CRUD) ────────────────────────────────────────────

    def _build_toolbar(self):
        return ft.Container(
            content=ft.Row(
                [
                    self._search_tf,
                    ft.Container(width=8),
                    # ── botones CRUD ───────────────────────────
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=16, color=T.ON_PRIMARY),
                                ft.Text("Agregar", size=13, color=T.ON_PRIMARY),
                            ],
                            spacing=4,
                            tight=True,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=T.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        ),
                        on_click=self._on_add,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [self._edit_btn, self._del_btn],
                            spacing=0,
                        ),
                        bgcolor=T.SURFACE,
                        border_radius=8,
                        border=ft.border.all(1, T.OUTLINE),
                        padding=ft.padding.symmetric(horizontal=4),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **T.get_card_style(),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

    # ── Tabla ──────────────────────────────────────────────────────────────

    def _build_table_card(self):
        cols = [
            ft.DataColumn(ft.Text("#",          size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Estado",     size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Grupo",      size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("SDWAN",      size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("COD_SERV",   size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Bandwidth",  size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Agencia / Enlace", size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("$/mes",      size=12, weight=ft.FontWeight.W_600), numeric=True),
            ft.DataColumn(ft.Text("Op.",        size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Vigencia",   size=12, weight=ft.FontWeight.W_600), numeric=True),
            ft.DataColumn(ft.Text("Inicio",     size=12, weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Fin",        size=12, weight=ft.FontWeight.W_600)),
        ]

        table = ft.DataTable(
            ref=self._table_ref,
            columns=cols,
            rows=self._build_rows(),
            border=ft.border.all(1, T.OUTLINE),
            border_radius=8,
            heading_row_color=ft.Colors.with_opacity(0.04, T.PRIMARY),
            heading_row_height=40,
            data_row_min_height=36,
            data_row_max_height=40,
            divider_thickness=0.5,
            column_spacing=16,
        )

        total_visible = sum(
            s.valor_mensual for s in self._servicios
            if not self._search_query or _matches(s, self._search_query)
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [table],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(expand=True),
                                ft.Text("TOTAL MENSUAL", size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=T.ON_SURFACE_VARIANT),
                                ft.Container(width=16),
                                ft.Text(f"${total_visible:,.2f}", size=14,
                                        weight=ft.FontWeight.W_700, color=T.PRIMARY),
                            ],
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        bgcolor=ft.Colors.with_opacity(0.04, T.PRIMARY),
                        border_radius=ft.border_radius.only(
                            bottom_left=8, bottom_right=8),
                    ),
                ],
                spacing=0,
            ),
            **T.get_card_style(),
            padding=0,
        )

    def _build_rows(self) -> list[ft.DataRow]:
        rows = []
        filtered = [
            s for s in self._servicios
            if not self._search_query or _matches(s, self._search_query)
        ]
        for i, s in enumerate(filtered, 1):
            is_sel = self._selected is s
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i), size=12,
                                            color=T.ON_SURFACE_VARIANT)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                s.estado, size=11,
                                color=_estado_color(s.estado),
                                weight=ft.FontWeight.W_600,
                            ),
                            bgcolor=ft.Colors.with_opacity(
                                0.08, _estado_color(s.estado)),
                            border_radius=4,
                            padding=ft.padding.symmetric(
                                horizontal=6, vertical=2),
                        )),
                        ft.DataCell(ft.Text(s.grupo, size=12)),
                        ft.DataCell(ft.Text(
                            "SI" if s.sdwan else "NO", size=12,
                            color=T.PRIMARY if s.sdwan else T.ON_SURFACE_VARIANT,
                        )),
                        ft.DataCell(ft.Text(
                            s.cod_serv, size=12,
                            weight=ft.FontWeight.W_600, color=T.PRIMARY,
                        )),
                        ft.DataCell(ft.Text(s.bandwidth, size=12)),
                        ft.DataCell(ft.Text(_display_agencia(s), size=12)),
                        ft.DataCell(ft.Text(
                            f"{s.valor_mensual:,.2f}", size=12)),
                        ft.DataCell(ft.Text(
                            s.estado_operativo, size=12,
                            color=_op_color(s.estado_operativo),
                            weight=ft.FontWeight.W_600,
                        )),
                        ft.DataCell(ft.Text(str(s.vigencia_meses), size=12)),
                        ft.DataCell(ft.Text(
                            s.fecha_inicio, size=11,
                            color=T.ON_SURFACE_VARIANT)),
                        ft.DataCell(ft.Text(
                            s.fecha_fin, size=11,
                            color=T.ON_SURFACE_VARIANT)),
                    ],
                    selected=is_sel,
                    color=ft.Colors.with_opacity(
                        0.08, T.PRIMARY) if is_sel else None,
                    on_select_changed=lambda e, svc=s: self._on_row_select(svc),
                )
            )
        return rows

    # ── Detail panel (derecha) ─────────────────────────────────────────────

    def _build_detail_panel(self) -> ft.Container:
        return ft.Container(
            ref=self._detail_ref,
            content=self._detail_content(),
            visible=self._selected is not None,
            width=320,
            **T.get_card_style(),
            padding=16,
        )

    def _detail_content(self) -> ft.Control:
        s = self._selected
        if s is None:
            return ft.Container()

        if isinstance(s, EnlaceInternet):
            ag = s.agencia
            cards = [
                self._info_card(
                    "Agencia", ft.Icons.LOCATION_ON_OUTLINED,
                    [
                        ("ID",        s.agencia_id),
                        ("Nombre",    ag.nombre if ag else "—"),
                        ("Dirección", ag.direccion if ag and ag.direccion else "—"),
                        ("Tipo",      ag.tipo if ag else "—"),
                    ],
                ),
                self._info_card(
                    "Servicio", ft.Icons.WIFI_OUTLINED,
                    [
                        ("Código",     s.cod_serv),
                        ("Bandwidth",  s.bandwidth),
                        ("SDWAN",      "Sí" if s.sdwan else "No"),
                        ("ISP",        s.isp),
                        ("$/mes",      f"${s.valor_mensual:,.2f}"),
                        ("Estado op.", s.estado_operativo),
                        ("Vigencia",   f"{s.vigencia_meses} meses"),
                        ("Inicio",     s.fecha_inicio),
                        ("Fin",        s.fecha_fin),
                        ("Notas",      s.notas or "—"),
                    ],
                ),
            ]
        else:
            ag_a = s.agencia_extremo_a
            ag_b = s.agencia_extremo_b
            cards = [
                self._info_card(
                    f"Extremo A", ft.Icons.ADJUST_OUTLINED,
                    [
                        ("ID",        s.extremo_a),
                        ("Nombre",    ag_a.nombre if ag_a else "—"),
                        ("Tipo",      ag_a.tipo if ag_a else "—"),
                    ],
                ),
                self._info_card(
                    f"Extremo B", ft.Icons.ADJUST_OUTLINED,
                    [
                        ("ID",        s.extremo_b),
                        ("Nombre",    ag_b.nombre if ag_b else "—"),
                        ("Tipo",      ag_b.tipo if ag_b else "—"),
                    ],
                ),
                self._info_card(
                    "Enlace de Datos", ft.Icons.CABLE_OUTLINED,
                    [
                        ("Código",     s.cod_serv),
                        ("Bandwidth",  s.bandwidth),
                        ("ISP",        s.isp),
                        ("$/mes",      f"${s.valor_mensual:,.2f}"),
                        ("Estado op.", s.estado_operativo),
                        ("Vigencia",   f"{s.vigencia_meses} meses"),
                        ("Inicio",     s.fecha_inicio),
                        ("Fin",        s.fecha_fin),
                        ("Notas",      s.notas or "—"),
                    ],
                ),
            ]

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINED, size=15, color=T.PRIMARY),
                        ft.Text("Detalle", size=13,
                                weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=T.ON_SURFACE_VARIANT,
                            tooltip="Cerrar",
                            on_click=lambda e: self._clear_selection(),
                        ),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=1, color=T.OUTLINE),
                *cards,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )

    def _info_card(self, title: str, icon: str,
                   fields: list[tuple[str, str]]) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, size=14, color=T.PRIMARY),
                            ft.Text(title, size=12,
                                    weight=ft.FontWeight.W_600, color=T.ON_SURFACE),
                        ],
                        spacing=6,
                    ),
                    ft.Divider(height=1, color=T.OUTLINE),
                    *[
                        ft.Row(
                            [
                                ft.Text(label, size=11,
                                        color=T.ON_SURFACE_VARIANT, width=80),
                                ft.Text(value, size=11, color=T.ON_SURFACE,
                                        expand=True, selectable=True),
                            ],
                            spacing=8,
                        )
                        for label, value in fields
                    ],
                ],
                spacing=5,
                tight=True,
            ),
            bgcolor=T.SURFACE_VARIANT,
            border_radius=8,
            padding=12,
        )

    # ── Callbacks ──────────────────────────────────────────────────────────

    def _on_row_select(self, svc):
        self._selected = svc
        self._edit_btn.disabled = False
        self._del_btn.disabled = False
        self._edit_btn.update()
        self._del_btn.update()
        self._table_ref.current.rows = self._build_rows()
        self._table_ref.current.update()
        self._detail_ref.current.content = self._detail_content()
        self._detail_ref.current.visible = True
        self._detail_ref.current.update()

    def _clear_selection(self):
        self._selected = None
        self._edit_btn.disabled = True
        self._del_btn.disabled = True
        self._edit_btn.update()
        self._del_btn.update()
        self._table_ref.current.rows = self._build_rows()
        self._table_ref.current.update()
        self._detail_ref.current.visible = False
        self._detail_ref.current.update()

    def _on_search(self, e):
        self._search_query = e.control.value or ""
        self._table_ref.current.rows = self._build_rows()
        self._table_ref.current.update()

    # ── CRUD ───────────────────────────────────────────────────────────────

    def _on_add(self, e):
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Agregar servicio — próximamente"),
            bgcolor=T.PRIMARY,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _on_edit(self, e):
        if not self._selected:
            return
        self._open_edit_dialog(self._selected)

    def _on_delete(self, e):
        if not self._selected:
            return
        self._open_delete_dialog(self._selected)

    # ── Diálogo de edición ─────────────────────────────────────────────────

    def _open_edit_dialog(self, svc):
        # ── campos editables ──────────────────────────────────────────
        op_dropdown = ft.Dropdown(
            label="Estado operativo",
            value=svc.estado_operativo,
            options=[
                ft.dropdown.Option("UP",   "UP — Enlace activo"),
                ft.dropdown.Option("DOWN", "DOWN — Enlace caído"),
            ],
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
        )
        ip_field = ft.TextField(
            label="IP pública",
            value=svc.ip_publica or "",
            hint_text="ej: 190.123.45.67",
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
        )
        notas_field = ft.TextField(
            label="Notas",
            value=svc.notas or "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
        )

        # ── sección agregar evento ────────────────────────────────────
        evento_fecha = ft.TextField(
            label="Fecha del evento",
            hint_text="YYYY-MM-DD",
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
            expand=True,
        )
        evento_tipo = ft.Dropdown(
            label="Tipo",
            value="nota",
            options=[
                ft.dropdown.Option("nota",       "Nota"),
                ft.dropdown.Option("caida",      "Caída"),
                ft.dropdown.Option("restablecimiento", "Restablecimiento"),
                ft.dropdown.Option("mantenimiento",    "Mantenimiento"),
            ],
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
            expand=True,
        )
        evento_desc = ft.TextField(
            label="Descripción del evento",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=T.OUTLINE,
            focused_border_color=T.PRIMARY,
            label_style=ft.TextStyle(color=T.ON_SURFACE_VARIANT, size=12),
        )
        evento_status = ft.Text("", size=11, color=T.SUCCESS)

        def _guardar_evento(e):
            desc = evento_desc.value.strip()
            if not desc:
                evento_status.value = "Escribe una descripción para el evento."
                evento_status.color = T.ERROR
                evento_status.update()
                return
            ok = add_evento(
                cod_serv=svc.cod_serv,
                tipo=evento_tipo.value,
                descripcion=desc,
                fecha=evento_fecha.value.strip() or None,
            )
            if ok:
                evento_fecha.value = ""
                evento_desc.value = ""
                evento_status.value = "Evento registrado."
                evento_status.color = T.SUCCESS
            else:
                evento_status.value = "Error al guardar el evento."
                evento_status.color = T.ERROR
            evento_fecha.update()
            evento_desc.update()
            evento_status.update()

        def _guardar_servicio(e):
            ok = update_servicio(
                cod_serv=svc.cod_serv,
                estado_operativo=op_dropdown.value,
                ip_publica=ip_field.value.strip(),
                notas=notas_field.value.strip(),
            )
            if ok:
                # actualiza el objeto en memoria para reflejar en UI sin recargar
                svc.estado_operativo = op_dropdown.value
                svc.ip_publica = ip_field.value.strip()
                svc.notas = notas_field.value.strip()
                self._table_ref.current.rows = self._build_rows()
                self._table_ref.current.update()
                self._detail_ref.current.content = self._detail_content()
                self._detail_ref.current.update()
            self.page.close(dlg)

        agencia_label = _display_agencia(svc)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.EDIT_OUTLINED, color=T.PRIMARY, size=18),
                    ft.Text(f"Editar  {svc.cod_serv}", size=15,
                            weight=ft.FontWeight.W_600),
                ],
                spacing=8,
            ),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    [
                        # ── referencia (solo lectura) ──────────────
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Datos del contrato  (solo lectura)",
                                            size=11, color=T.ON_SURFACE_VARIANT,
                                            weight=ft.FontWeight.W_600),
                                    ft.Row(
                                        [
                                            _ref_chip("Agencia", agencia_label),
                                            _ref_chip("Bandwidth", svc.bandwidth),
                                            _ref_chip("$/mes", f"${svc.valor_mensual:,.2f}"),
                                            _ref_chip("Grupo", svc.grupo),
                                        ],
                                        wrap=True, spacing=6,
                                    ),
                                ],
                                spacing=8, tight=True,
                            ),
                            bgcolor=T.SURFACE_VARIANT,
                            border_radius=8,
                            padding=12,
                        ),
                        ft.Divider(height=1, color=T.OUTLINE),
                        # ── campos editables ───────────────────────
                        ft.Text("Campos editables", size=11,
                                color=T.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_600),
                        op_dropdown,
                        ip_field,
                        notas_field,
                        ft.Divider(height=1, color=T.OUTLINE),
                        # ── agregar evento ─────────────────────────
                        ft.Text("Registrar evento", size=11,
                                color=T.ON_SURFACE_VARIANT,
                                weight=ft.FontWeight.W_600),
                        ft.Row([evento_fecha, evento_tipo], spacing=10),
                        evento_desc,
                        ft.Row(
                            [
                                evento_status,
                                ft.Container(expand=True),
                                ft.OutlinedButton(
                                    "Agregar evento",
                                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                    on_click=_guardar_evento,
                                ),
                            ],
                        ),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("Cancelar",
                              on_click=lambda e: self.page.close(dlg)),
                ft.ElevatedButton(
                    "Guardar cambios",
                    icon=ft.Icons.SAVE_OUTLINED,
                    style=ft.ButtonStyle(
                        bgcolor=T.PRIMARY,
                        color=T.ON_PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=_guardar_servicio,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    # ── Diálogo de confirmación para eliminar ──────────────────────────────

    def _open_delete_dialog(self, svc):
        def _confirmar(e):
            self.page.close(dlg)
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Eliminar servicio — próximamente (requiere lógica de escritura compleja)"),
                bgcolor=T.ON_SURFACE_VARIANT,
            )
            self.page.snack_bar.open = True
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=T.ERROR, size=18),
                    ft.Text("Eliminar servicio", size=15,
                            weight=ft.FontWeight.W_600, color=T.ERROR),
                ],
                spacing=8,
            ),
            content=ft.Text(
                f"¿Eliminar el servicio {svc.cod_serv} — {_display_agencia(svc)}?\n"
                "Esta acción no se puede deshacer.",
                size=13,
            ),
            actions=[
                ft.TextButton("Cancelar",
                              on_click=lambda e: self.page.close(dlg)),
                ft.ElevatedButton(
                    "Eliminar",
                    icon=ft.Icons.DELETE_OUTLINE,
                    style=ft.ButtonStyle(
                        bgcolor=T.ERROR,
                        color=T.ON_PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=_confirmar,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

import flet as ft
from config.theme import AppColors, AppStyles
from config.menu_structure import MenuStructure


class NavRailComponent:
    """
    Componente de navegación lateral para Flet 0.28+ (sin UserControl).
    Expone:
      - .view  -> el Control (Container) que debes añadir al layout
      - .toggle() / .update() / .on_menu_click() / .on_submenu_click()
    """
    def __init__(self, page: ft.Page, visible: bool = False, width: int = 200):
        self.page = page
        self.visible = visible
        self.width = width

        self.selected_menu = None
        self.selected_submenu = None

        # Controles internos que reusamos al refrescar
        self._container: ft.Container | None = None
        self._column: ft.Column | None = None

        # Construimos la vista inicial
        self.view = self._build()

    def build(self):
        return self.view
    
    # API pública
    def toggle(self):
        self.visible = not self.visible
        self.update()

    def update(self):
        """Refresca contenido y visibilidad."""
        self._build(update_only=True)

    def on_menu_click(self, key: str):
        self.selected_menu = key
        self.selected_submenu = None
        self.update()

    def on_submenu_click(self, key: str):
        self.selected_submenu = key 
        self.update()

    # ---- Implementación interna ----
    def _build(self, update_only: bool = False) -> ft.Container:
        menu_items = MenuStructure().items or []

        # Seleccionar el primer menú por defecto
        if self.selected_menu is None and menu_items:
            self.selected_menu = menu_items[0]["key"]

        # Handlers
        def make_menu_onclick(menu_key: str):
            def handler(e):
                self.selected_menu = menu_key
                self.selected_submenu = None
                self._refresh_controls()
            return handler

        def make_submenu_onclick(submenu_key: str):
            def handler(e):
                self.selected_submenu = submenu_key
                self._refresh_controls()
            return handler

        # Construir tiles del menú
        tiles: list[ft.Control] = []
        for item in menu_items:
            is_selected = self.selected_menu == item["key"]
            tiles.append(
                ft.ListTile(
                    title=ft.Text(
                        item["label"], 
                        color=AppColors.NAV_TEXT_SELECTED if is_selected else AppColors.NAV_TEXT,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                    ),
                    leading=ft.Icon(
                        item["icon"],
                        color=AppColors.NAV_TEXT_SELECTED if is_selected else AppColors.NAV_TEXT
                    ),
                    dense=True,
                    selected=is_selected,
                    selected_tile_color=AppColors.NAV_ITEM_SELECTED_BG,
                    bgcolor=AppColors.NAV_ITEM_SELECTED_BG if is_selected else AppColors.NAV_ITEM_BG,
                    on_click=make_menu_onclick(item["key"]),
                )
            )

            # Submenús visibles sólo si el menú está seleccionado
            if is_selected and item.get("submenus"):
                for submenu in item["submenus"]:
                    is_sub_selected = self.selected_submenu == submenu["key"]
                    tiles.append(
                        ft.ListTile(
                            title=ft.Text("    " + submenu["label"], color=AppColors.ON_BACKGROUND),
                            leading=ft.Icon(ft.Icons.ARROW_RIGHT),
                            selected=is_sub_selected,
                            bgcolor=AppColors.BACKGROUND if is_sub_selected else AppColors.PRIMARY,
                            on_click=make_submenu_onclick(submenu["key"]),
                        )
                    )

        # Primera creación
        if not update_only or self._container is None:
            self._column = ft.Column(controls=tiles, spacing=1)
            self._container = ft.Container(
                content=self._column,
                bgcolor=AppColors.BACKGROUND,
                visible=self.visible,
                width=self.width,
            )
            return self._container

        # Modo actualización (reusar controles y sólo cambiar props)
        if self._column is not None:
            self._column.controls = tiles
        if self._container is not None:
            self._container.visible = self.visible
            self._container.width = self.width
            self._container.update()
        return self._container

    def _refresh_controls(self):
        """Reconstruye el contenido y actualiza la página."""
        self._build(update_only=True)
        # Si prefieres actualizar sólo el contenedor:
        # self._container.update()
        # Si necesitas refrescar toda la página:
        # self.page.update()

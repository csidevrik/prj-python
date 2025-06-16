import flet as ft
from config.theme import AppColors
from config.menu_structure import MenuStructure
from config.theme import AppStyles

class NavRailComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.visible = False
        self.width = 200
        self._container = None  # Referencia al container
        self.selected_menu = None
        self.selected_submenu = None
        
    def update(self):
        if self._container:
            self._container.visible = self.visible
            self._container.update()
        
    def build(self):
        menu_items = MenuStructure().items
        # Inicializa el primer menú como seleccionado si ninguno está seleccionado
        if self.selected_menu is None and menu_items:
            self.selected_menu = menu_items[0]["key"]

        menu_tiles = []

        def make_menu_onclick(menu_key):
            def handler(e):
                self.selected_menu = menu_key
                self.selected_submenu = None
                self.page.update()
            return handler

        def make_submenu_onclick(submenu_key):
            def handler(e):
                self.selected_submenu = submenu_key
                self.page.update()
            return handler

        for item in menu_items:
            is_selected = self.selected_menu == item["key"]
            menu_tiles.append(
                ft.ListTile(
                    title=ft.Text(item['label'], color=AppColors.ON_BACKGROUND),
                    leading=ft.Icon(item['icon']),
                    selected=is_selected,
                    bgcolor="blue100" if is_selected else None,
                    on_click=make_menu_onclick(item["key"])
                )
            )
            # Mostrar submenús solo si este menú está seleccionado y tiene submenús
            if is_selected and item.get("submenus"):
                for submenu in item["submenus"]:
                    is_sub_selected = self.selected_submenu == submenu["key"]
                    menu_tiles.append(
                        ft.ListTile(
                            title=ft.Text("    " + submenu['label'], color=AppColors.ON_BACKGROUND),
                            leading=ft.Icon(ft.Icons.ARROW_RIGHT),
                            selected=is_sub_selected,
                            bgcolor="blue200" if is_sub_selected else "blue50",
                            on_click=make_submenu_onclick(submenu["key"])
                        )
                    )

        self._container = ft.Container(
            content=ft.Column([
                ft.Text("TOOLS",**AppStyles.Text.TITLE),
                ft.Divider(),
                # Aquí irán los items del menú
                *menu_tiles
            ], spacing=1),
            bgcolor=AppColors.BACKGROUND,
            visible=self.visible,
            width=self.width
        )
        return self._container

    def on_menu_click(self, key):
        self.selected_menu = key
        self.selected_submenu = None
        self.page.update()

    def on_submenu_click(self, key):
        self.selected_submenu = key
        self.page.update()

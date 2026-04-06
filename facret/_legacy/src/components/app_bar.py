import flet as ft
from config.theme import AppColors, AppGradients, AppStyles

class AppBarComponent:
    def __init__(self, page: ft.Page, on_menu_click=None):
        self.page = page
        self.on_menu_click = on_menu_click
        self.search_expanded = False
        self.search_history = [
            {"text": "Factura 001", "action": lambda: print("Ir a Factura 001")},
            {"text": "Retención 2024", "action": lambda: print("Ir a Retención 2024")},
            {"text": "Configuración", "action": lambda: print("Ir a Configuración")},
        ]
        self.search_field = ft.TextField(
            visible=False,
            width=0,
            height=36,
            hint_text="Buscar...",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=10),
            autofocus=True,
            on_change=lambda e: self.update_suggestions(e.control.value),
            text_size=14,
            color=AppColors.ON_PRIMARY,
        )
        self.dropdown_column = ft.Column(  # Crear referencia separada para el Column
            controls=[],
            spacing=0,
        )
        self.suggestions_dropdown = ft.Container(
            content=self.dropdown_column,  # Usar la referencia
            bgcolor=AppColors.SURFACE,
            border_radius=8,
            padding=8,
            visible=False
        )
        
    def build_search(self):
        # Solo retornamos las referencias ya inicializadas
        return self.search_field, self.suggestions_dropdown

    def update_suggestions(self, query):
        filtered = [s for s in self.search_history if query.lower() in s["text"].lower()]
        self.dropdown_column.controls.clear()  # Usar dropdown_column en lugar de content.controls
        for s in filtered:
            self.dropdown_column.controls.append(
                ft.ListTile(
                    title=ft.Text(
                        s["text"],
                        color=AppColors.ON_SURFACE,
                        size=14
                    ),
                    on_click=lambda e, action=s["action"]: (action(), self.collapse_search()),
                )
            )
        self.suggestions_dropdown.visible = bool(filtered)
        self.dropdown_column.update()  # Actualizar el Column
        self.suggestions_dropdown.update()  # Actualizar el Container

    def expand_search(self, e):
        self.search_expanded = True
        self.search_field.visible = True
        self.search_field.width = 250
        self.search_field.focus()
        self.suggestions_dropdown.visible = True
        self.search_field.update()
        self.suggestions_dropdown.update()

    def collapse_search(self):
        self.search_expanded = False
        self.search_field.visible = False
        self.search_field.width = 0
        self.suggestions_dropdown.visible = False
        self.search_field.value = ""
        self.search_field.update()
        self.suggestions_dropdown.update()

    def build_action_buttons(self):
        return ft.Row([
            ft.IconButton(
                ft.Icons.SEARCH,
                icon_color=AppColors.ON_PRIMARY,
                tooltip="Buscar",
                on_click=self.expand_search
            ),
            ft.IconButton(
                ft.Icons.MENU,
                icon_color=AppColors.ON_PRIMARY,
                tooltip="Menú",
                on_click=self.on_menu_click
            ),
            # ...resto de botones...
        ])

    def build(self):
        search_field, suggestions_dropdown = self.build_search()
        return ft.Container(
            content=ft.Row([
                ft.Text("FACRET", **AppStyles.Text.TITLE),
                ft.Container(expand=True),
                ft.Stack([search_field, suggestions_dropdown]),
                self.build_action_buttons(),
            ]),
            # gradient=AppGradients.app_bar(),
            gradient=AppGradients.by_name("Omolon"),
            padding=1
        )

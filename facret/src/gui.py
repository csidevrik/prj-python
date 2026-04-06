# =============================
# gui.py
# =============================
import importlib
import flet as ft
from components.sidebar                      import DriveSidebarComponent
from components.toolbar                      import DriveToolbarComponent
from components.header.responsive_header     import ResponsiveDriveHeader as ResponsiveHeaderComponent
from config.theme                            import DriveTheme
from config.menu_config                      import ALL_ITEMS, MENU_ITEMS, LABEL_MAP


def _load_page(page_class_path: str, flet_page: ft.Page) -> ft.Control:
    """
    Importa dinámicamente 'module.path.ClassName' y devuelve .build().
    Para registrar una nueva página solo hay que actualizar menu_config.py.
    """
    module_path, class_name = page_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(flet_page).build()


def _placeholder_page(key: str) -> ft.Control:
    """Vista por defecto para secciones aún no implementadas."""
    label = LABEL_MAP.get(key, key)
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CONSTRUCTION, size=64, color=DriveTheme.GREY_200),
                ft.Text(
                    f"«{label}»",
                    size=18,
                    weight=ft.FontWeight.W_500,
                    color=DriveTheme.GREY_600,
                ),
                ft.Text("Sección en construcción", size=13, color=DriveTheme.GREY_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=DriveTheme.GREY_50,
    )


def run_drive_gui():
    def main(page: ft.Page):
        page.title = "FACRET"
        page.window.icon = "../assets/favicon.ico"
        page.window.width = 1200
        page.window.height = 800
        page.padding = 0
        page.spacing = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = DriveTheme.get_theme()

        header  = ResponsiveHeaderComponent(page)
        sidebar = DriveSidebarComponent(page)
        toolbar = DriveToolbarComponent(page, on_toggle_sidebar=sidebar._toggle_sidebar)

        content_area = ft.Container(
            content=_load_page("pages.home_page.HomePage", page),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )

        def on_navigate(key: str):
            toolbar.update_breadcrumb(key)
            item = next((m for m in ALL_ITEMS if m.key == key), None)
            if item and item.page_class:
                content_area.content = _load_page(item.page_class, page)
            else:
                content_area.content = _placeholder_page(key)
            content_area.update()

        sidebar.on_nav_change   = on_navigate
        header.on_navigate      = on_navigate   # engranaje del header → settings

        main_layout = ft.Column(
            [
                header.build(),
                toolbar.build(),
                ft.Row(
                    [sidebar.build(), content_area],
                    spacing=0,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

        page.add(main_layout)

    ft.app(target=main, assets_dir="assets")

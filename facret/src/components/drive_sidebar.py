# =============================
# components/drive_sidebar.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme

class DriveSidebarComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_item = "home"
    
    def build(self):
        return ft.Container(
            width=280,
            content=ft.Column([
                # Botón Nuevo
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.ADD, size=20),
                            ft.Text("Nuevo", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=8, tight=True),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=16),
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            bgcolor=DriveTheme.SURFACE_WHITE,
                            color=DriveTheme.GREY_800,
                            shadow_color=ft.colors.with_opacity(0.15, ft.colors.BLACK),
                            elevation=2,
                        ),
                        on_click=self._on_new_click,
                    ),
                    padding=ft.padding.all(16),
                ),
                
                # Menú de navegación
                ft.Column([
                    self._create_nav_item("home", ft.icons.HOME_OUTLINED, "Página principal", True),
                    self._create_nav_item("my_drive", ft.icons.FOLDER_OUTLINED, "Mi unidad"),
                    self._create_nav_item("computers", ft.icons.COMPUTER_OUTLINED, "Ordenadores"),
                    self._create_nav_item("shared", ft.icons.PEOPLE_OUTLINED, "Compartido conmigo"),
                    self._create_nav_item("recent", ft.icons.ACCESS_TIME, "Reciente"),
                    self._create_nav_item("starred", ft.icons.STAR_OUTLINE, "Destacados"),
                    self._create_nav_item("trash", ft.icons.DELETE_OUTLINE, "Papelera"),
                ], spacing=4),
                
                ft.Divider(height=1, color=DriveTheme.GREY_200),
                
                # Almacenamiento
                ft.Container(
                    content=ft.Column([
                        ft.Text("Almacenamiento", size=14, color=DriveTheme.GREY_600),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.CLOUD_OUTLINED, size=16, color=DriveTheme.GREY_600),
                                    ft.Text("15 GB utilizados de 15 GB", size=12, color=DriveTheme.GREY_600),
                                ], spacing=8),
                                ft.Container(
                                    content=ft.ProgressBar(value=0.8, height=4, bgcolor=DriveTheme.GREY_200),
                                    margin=ft.margin.symmetric(vertical=8),
                                ),
                            ]),
                            **DriveTheme.get_card_style(),
                            padding=12,
                            margin=ft.margin.only(top=8),
                        )
                    ]),
                    padding=16,
                )
                
            ], spacing=0),
            bgcolor=DriveTheme.SURFACE_WHITE,
        )
    
    def _create_nav_item(self, key: str, icon: str, text: str, selected: bool = False):
        is_selected = self.selected_item == key
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    icon,
                    color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_600,
                    size=20
                ),
                title=ft.Text(
                    text,
                    color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_800,
                    size=14,
                    weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.W_400
                ),
                on_click=lambda e, k=key: self._on_nav_click(k),
            ),
            bgcolor=ft.colors.with_opacity(0.1, DriveTheme.PRIMARY_BLUE) if is_selected else None,
            # border_radius=0,
            margin=ft.margin.symmetric(horizontal=8),
            border_radius=8,
        )
    
    def _on_nav_click(self, key: str):
        self.selected_item = key
        self.page.update()
    
    def _on_new_click(self, e):
        # Implementar menú de nuevo archivo/carpeta
        pass
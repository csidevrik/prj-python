# =============================
# components/drive_content.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme

class DriveContentComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view_mode = "grid"  # grid o list
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                # Barra de herramientas
                self._build_toolbar(),
                
                # Contenido principal
                ft.Container(
                    content=self._build_file_grid(),
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                )
            ], spacing=0),
            expand=True,
        )
    
    def _build_toolbar(self):
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    "Enlaces rápidos",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=DriveTheme.GREY_800
                ),
                ft.Container(expand=True),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.VIEW_MODULE if self.view_mode == "grid" else ft.Icons.VIEW_MODULE_OUTLINED,
                        tooltip="Vista en cuadrícula",
                        on_click=lambda e: self._change_view("grid"),
                        icon_color=DriveTheme.PRIMARY_BLUE if self.view_mode == "grid" else DriveTheme.GREY_600,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.VIEW_LIST if self.view_mode == "list" else ft.Icons.VIEW_LIST_OUTLINED,
                        tooltip="Vista de lista",
                        on_click=lambda e: self._change_view("list"),
                        icon_color=DriveTheme.PRIMARY_BLUE if self.view_mode == "list" else DriveTheme.GREY_600,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        tooltip="Información",
                        icon_color=DriveTheme.GREY_600,
                    ),
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
        )
    
    def _build_file_grid(self):
        # Datos de ejemplo
        files = [
            {"name": "Documentos importantes", "type": "folder", "shared": True},
            {"name": "Proyecto FACRET", "type": "folder", "shared": False},
            {"name": "Informe_2024.pdf", "type": "pdf", "shared": False},
            {"name": "Presentación.pptx", "type": "presentation", "shared": True},
            {"name": "Datos_analysis.xlsx", "type": "spreadsheet", "shared": False},
            {"name": "Codigo_fuente.zip", "type": "archive", "shared": False},
        ]
        
        if self.view_mode == "grid":
            return ft.GridView(
                runs_count=4,
                max_extent=250,
                child_aspect_ratio=1.2,
                spacing=16,
                run_spacing=16,
                controls=[self._create_file_card(file) for file in files],
            )
        else:
            return ft.Column([
                self._create_file_row(file) for file in files
            ], spacing=4)
    
    def _create_file_card(self, file_data):
        icon = self._get_file_icon(file_data["type"])
        
        # Construir elementos de la columna dinámicamente
        column_items = [
            ft.Container(
                content=ft.Icon(
                    icon,
                    size=48,
                    color=self._get_file_color(file_data["type"])
                ),
                alignment=ft.alignment.center,
                height=80,
            ),
            ft.Text(
                file_data["name"],
                size=14,
                text_align=ft.TextAlign.CENTER,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
                color=DriveTheme.GREY_800,
            ),
        ]
        
        # Agregar ícono de compartido si es necesario
        if file_data["shared"]:
            column_items.append(
                ft.Container(
                    content=ft.Icon(ft.Icons.PEOPLE, size=16, color=DriveTheme.GREY_600),
                    alignment=ft.alignment.center_right,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                column_items,
                spacing=8, 
                alignment=ft.MainAxisAlignment.CENTER
            ),
            **DriveTheme.get_card_style(),
            padding=16,
            on_click=lambda e, f=file_data: self._on_file_click(f),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            # animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )
    
    def _create_file_row(self, file_data):
        icon = self._get_file_icon(file_data["type"])
        
        # Construir elementos trailing dinámicamente
        trailing_items = []
        if file_data["shared"]:
            trailing_items.append(ft.Icon(ft.Icons.PEOPLE, size=16, color=DriveTheme.GREY_600))
        trailing_items.append(ft.IconButton(
            icon=ft.Icons.MORE_VERT,
            icon_size=16,
            icon_color=DriveTheme.GREY_600,
        ))
        
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    icon,
                    color=self._get_file_color(file_data["type"]),
                    size=24
                ),
                title=ft.Text(file_data["name"], size=14),
                trailing=ft.Row(trailing_items, spacing=4, tight=True),
                on_click=lambda e, f=file_data: self._on_file_click(f),
            ),
            bgcolor=DriveTheme.SURFACE_WHITE,
            border_radius=8,
            margin=ft.margin.symmetric(vertical=2),
        )
    
    def _get_file_icon(self, file_type):
        Icons = {
            "folder": ft.Icons.FOLDER,
            "pdf": ft.Icons.PICTURE_AS_PDF,
            "presentation": ft.Icons.SLIDESHOW,
            "spreadsheet": ft.Icons.TABLE_CHART,
            "archive": ft.Icons.ARCHIVE,
        }
        return Icons.get(file_type, ft.Icons.INSERT_DRIVE_FILE)
    
    def _get_file_color(self, file_type):
        Colors = {
            "folder": ft.Colors.BLUE_600,
            "pdf": ft.Colors.RED_600,
            "presentation": ft.Colors.ORANGE_600,
            "spreadsheet": ft.Colors.GREEN_600,
            "archive": ft.Colors.PURPLE_600,
        }
        return Colors.get(file_type, DriveTheme.GREY_600)
    
    def _change_view(self, mode):
        self.view_mode = mode
        self.page.update()
    
    def _on_file_click(self, file_data):
        print(f"Clicked on: {file_data['name']}")
        # Implementar lógica de apertura de archivos
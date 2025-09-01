import flet as ft
from ...config.theme import AppTheme

class AppBar:
    def __init__(self, page: ft.Page, navigation_handler):
        self.page = page
        self.navigation_handler = navigation_handler
        self.work_directory = ""
        
    def build(self):
        return ft.Container(
            content=ft.Row([
                # Brand Container
                self._build_brand_container(),
                
                # Directory Search Container
                self._build_directory_search_container(),
                
                # Utility Container
                self._build_utility_container(),
                
                # Window Controls Container (solo para desktop)
                self._build_window_controls_container()
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=AppTheme.PRIMARY_COLOR,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            height=60
        )
    
    def _build_brand_container(self):
        return ft.Row([
            ft.Container(
                content=ft.Text("A", color="black", size=20, weight=ft.FontWeight.BOLD),
                width=40,
                height=40,
                bgcolor="#FFC107",
                border_radius=20,
                alignment=ft.alignment.center
            ),
            ft.Text("FACRET", color="white", size=18, weight=ft.FontWeight.BOLD)
        ], spacing=10)
    
    def _build_directory_search_container(self):
        self.search_field = ft.TextField(
            hint_text="Buscar en directorio...",
            width=300,
            height=40,
            bgcolor="white",
            on_change=self._on_search_change
        )
        
        self.open_dir_button = ft.ElevatedButton(
            text="Abrir Directorio",
            on_click=self._open_directory_dialog,
            bgcolor="white",
            color=AppTheme.PRIMARY_COLOR
        )
        
        return ft.Row([
            self.search_field,
            self.open_dir_button
        ], spacing=10)
    
    def _build_utility_container(self):
        return ft.Row([
            ft.IconButton(
                icon=ft.icons.HELP_OUTLINE,
                icon_color="white",
                tooltip="Ayuda",
                on_click=self._show_help
            ),
            ft.IconButton(
                icon=ft.icons.SETTINGS,
                icon_color="white",
                tooltip="Configuración",
                on_click=self._show_settings
            ),
            # Badge corregido con Stack
            ft.Container(
                content=ft.Stack([
                    ft.IconButton(
                        icon=ft.icons.NOTIFICATIONS,
                        icon_color="white",
                        tooltip="Notificaciones",
                        on_click=self._show_notifications
                    ),
                    ft.Container(
                        content=ft.Text("3", color="white", size=12, weight=ft.FontWeight.BOLD),
                        bgcolor="red",
                        width=20,
                        height=20,
                        border_radius=10,
                        alignment=ft.alignment.center,
                        right=5,
                        top=5
                    )
                ]),
                width=50,
                height=50
            ),
            ft.PopupMenuButton(
                icon=ft.icons.ACCOUNT_CIRCLE,
                icon_color="white",
                tooltip="Perfil de usuario",
                items=[
                    ft.PopupMenuItem(text="Perfil"),
                    ft.PopupMenuItem(text="Cerrar Sesión"),
                ]
            )
        ], spacing=5)
    
    def _build_window_controls_container(self):
        # Controles de ventana simplificados
        return ft.Row([
            ft.IconButton(
                icon=ft.icons.MINIMIZE,
                icon_color="white",
                tooltip="Minimizar",
                on_click=self._minimize_window
            ),
            ft.IconButton(
                icon=ft.icons.CROP_SQUARE,
                icon_color="white",
                tooltip="Maximizar",
                on_click=self._toggle_maximize
            ),
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_color="white",
                tooltip="Cerrar",
                on_click=self._close_window
            )
        ], spacing=0)
    
    # Métodos que estaban faltando
    def _on_search_change(self, e):
        search_term = e.control.value
        print(f"Buscando: {search_term}")
        # TODO: Implementar búsqueda
    
    def _open_directory_dialog(self, e):
        def get_directory_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.work_directory = e.path
                self.search_field.hint_text = f"Directorio: {e.path}"
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=get_directory_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.get_directory_path()
    
    def _show_help(self, e):
        self._show_dialog("Ayuda", "Manual de usuario próximamente...")
    
    def _show_settings(self, e):
        self._show_dialog("Configuración", "Panel de configuración en desarrollo...")
    
    def _show_notifications(self, e):
        self._show_dialog("Notificaciones", "No hay notificaciones nuevas")
    
    def _show_dialog(self, title, content):
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("Cerrar", on_click=close_dialog)
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _minimize_window(self, e):
        # En Flet, estas funciones pueden no estar disponibles en todas las plataformas
        print("Minimizar ventana")
        try:
            self.page.window_minimized = True
            self.page.update()
        except:
            print("Función minimizar no disponible en esta plataforma")
        
    def _toggle_maximize(self, e):
        print("Maximizar/Restaurar ventana")
        try:
            self.page.window_maximized = not getattr(self.page, 'window_maximized', False)
            self.page.update()
        except:
            print("Función maximizar no disponible en esta plataforma")
    
    def _close_window(self, e):
        print("Cerrando aplicación")
        try:
            self.page.window_destroy()
        except:
            print("Función cerrar no disponible, cerrando página...")
            self.page.go("/")
    
    def update_responsive(self, is_mobile, is_tablet):
        if is_mobile:
            self.search_field.width = 150
            self.search_field.visible = False  # Ocultar en móvil
        elif is_tablet:
            self.search_field.width = 200
            self.search_field.visible = True
        else:
            self.search_field.width = 300
            self.search_field.visible = True
        
        self.page.update()
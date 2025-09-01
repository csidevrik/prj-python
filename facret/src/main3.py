import flet as ft
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Callable
from enum import Enum

# Configuración de temas y colores
class AppTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

@dataclass
class AppColors:
    # Colores principales
    primary: str
    primary_variant: str
    secondary: str
    background: str
    surface: str
    error: str
    
    # Colores de texto
    on_primary: str
    on_secondary: str
    on_background: str
    on_surface: str
    on_error: str
    
    # Colores del sidebar
    sidebar_bg: str
    sidebar_hover: str
    sidebar_selected: str
    
    # Bordes y divisores
    border_color: str
    divider_color: str

# Definir paletas de colores para cada tema
THEME_COLORS = {
    AppTheme.LIGHT: AppColors(
        primary="#0066CC",
        primary_variant="#004499",
        secondary="#6C757D",
        background="#FFFFFF",
        surface="#F8F9FA",
        error="#DC3545",
        
        on_primary="#FFFFFF",
        on_secondary="#FFFFFF",
        on_background="#212529",
        on_surface="#212529",
        on_error="#FFFFFF",
        
        sidebar_bg="#F8F9FA",
        sidebar_hover="#E9ECEF",
        sidebar_selected="#E3F2FD",
        
        border_color="#DEE2E6",
        divider_color="#E9ECEF"
    ),
    
    AppTheme.DARK: AppColors(
        primary="#4A9EFF",
        primary_variant="#2B7DE9",
        secondary="#8E9297",
        background="#1A1A1A",
        surface="#2D2D30",
        error="#F87171",
        
        on_primary="#000000",
        on_secondary="#FFFFFF",
        on_background="#FFFFFF",
        on_surface="#FFFFFF",
        on_error="#000000",
        
        sidebar_bg="#252526",
        sidebar_hover="#37373D",
        sidebar_selected="#094771",
        
        border_color="#3E3E42",
        divider_color="#37373D"
    )
}

@dataclass
class AppSettings:
    app_title: str = "Helper Tools"
    window_width: int = 1200
    window_height: int = 800
    theme: AppTheme = AppTheme.DARK
    sidebar_width: int = 280
    sidebar_collapsed_width: int = 60
    sidebar_visible: bool = True
    last_selected_tool: str = "home"

class SettingsManager:
    def __init__(self, settings_file: str = "app_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> AppSettings:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convertir el string del theme de vuelta a enum
                    if 'theme' in data:
                        if isinstance(data['theme'], str):
                            # Si es un string como "AppTheme.DARK", extraer solo "DARK"
                            theme_value = data['theme'].split('.')[-1] if '.' in data['theme'] else data['theme']
                            try:
                                data['theme'] = AppTheme(theme_value.lower())
                            except ValueError:
                                data['theme'] = AppTheme.DARK
                    return AppSettings(**data)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
                return AppSettings()
        return AppSettings()
    
    def save_settings(self):
        try:
            data = asdict(self.settings)
            # Convertir el enum a string para guardarlo
            if 'theme' in data:
                data['theme'] = data['theme'].value
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

class SidebarItem:
    def __init__(self, 
                 key: str, 
                 title: str, 
                 icon: str, 
                 on_click: Callable = None,
                 shortcut: str = None):
        self.key = key
        self.title = title
        self.icon = icon
        self.on_click = on_click
        self.shortcut = shortcut

class MainApp:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Asegurar que el tema sea válido
        if not isinstance(self.settings.theme, AppTheme):
            self.settings.theme = AppTheme.DARK
        
        self.colors = THEME_COLORS[self.settings.theme]
        
        # Estado de la aplicación
        self.sidebar_collapsed = not self.settings.sidebar_visible
        self.selected_tool = self.settings.last_selected_tool
        
        # Controles principales
        self.page = None
        self.sidebar_container = None
        self.main_content = None
        self.sidebar_items = []
        
        self.setup_sidebar_items()
    
    def setup_sidebar_items(self):
        """Configurar los elementos del sidebar"""
        self.sidebar_items = [
            SidebarItem("home", "Inicio", ft.Icons.HOME, shortcut="Ctrl+H"),
            SidebarItem("text_tools", "Herramientas de Texto", ft.Icons.TEXT_FIELDS, shortcut="Ctrl+T"),
            SidebarItem("file_tools", "Archivos", ft.Icons.FOLDER, shortcut="Ctrl+F"),
            SidebarItem("system_tools", "Sistema", ft.Icons.COMPUTER, shortcut="Ctrl+S"),
            SidebarItem("network_tools", "Red", ft.Icons.WIFI, shortcut="Ctrl+N"),
            SidebarItem("calculator", "Calculadora", ft.Icons.CALCULATE, shortcut="Ctrl+C"),
            SidebarItem("settings", "Configuración", ft.Icons.SETTINGS, shortcut="Ctrl+,"),
        ]
    
    def create_sidebar_item(self, item: SidebarItem) -> ft.Container:
        """Crear un elemento del sidebar"""
        is_selected = item.key == self.selected_tool
        
        # Definir el contenido según si está colapsado o no
        if self.sidebar_collapsed:
            content = ft.Row([
                ft.Icon(
                    item.icon, 
                    size=20, 
                    color=self.colors.primary if is_selected else self.colors.on_surface
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        else:
            content = ft.Row([
                ft.Icon(
                    item.icon, 
                    size=20, 
                    color=self.colors.primary if is_selected else self.colors.on_surface
                ),
                ft.Text(
                    item.title,
                    size=14,
                    color=self.colors.primary if is_selected else self.colors.on_surface,
                    weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
                )
            ], spacing=12)
        
        container = ft.Container(
            content=content,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            margin=ft.margin.symmetric(horizontal=8, vertical=2),
            bgcolor=self.colors.sidebar_selected if is_selected else None,
            border_radius=8,
            on_click=lambda e, key=item.key: self.select_tool(key),
            on_hover=lambda e, key=item.key: self.on_sidebar_item_hover(e, key),
            tooltip=item.title if self.sidebar_collapsed else None,
            data=item.key  # Guardar la key en el container
        )
        
        return container
    
    def on_sidebar_item_hover(self, e, item_key: str):
        """Manejar hover en elementos del sidebar"""
        is_selected = item_key == self.selected_tool
        
        if e.data == "true":  # Mouse entra
            if not is_selected:  # Solo aplicar hover si NO está seleccionado
                e.control.bgcolor = self.colors.sidebar_hover
        else:  # Mouse sale
            if is_selected:
                # Restaurar color de seleccionado
                e.control.bgcolor = self.colors.sidebar_selected
            else:
                # Restaurar color normal (transparente)
                e.control.bgcolor = None
        e.control.update()
    
    def toggle_sidebar(self, e=None):
        """Alternar visibilidad del sidebar"""
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.settings.sidebar_visible = not self.sidebar_collapsed
        self.settings_manager.save_settings()
        self.update_sidebar()
    
    def update_sidebar(self):
        """Actualizar el sidebar"""
        if not self.sidebar_container:
            return
            
        # Limpiar contenido actual
        self.sidebar_container.content.controls.clear()
        
        # Header del sidebar
        if self.sidebar_collapsed:
            header = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_size=20,
                    on_click=self.toggle_sidebar,
                    tooltip="Expandir sidebar"
                ),
                padding=ft.padding.symmetric(vertical=8),
                alignment=ft.alignment.center
            )
        else:
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        self.settings.app_title,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors.on_surface
                    ),
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_size=20,
                        on_click=self.toggle_sidebar,
                        tooltip="Colapsar sidebar"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.all(12)
            )
        
        # Agregar header
        self.sidebar_container.content.controls.append(header)
        
        # Divisor
        self.sidebar_container.content.controls.append(
            ft.Divider(color=self.colors.divider_color, height=1)
        )
        
        # Agregar elementos del sidebar
        for item in self.sidebar_items:
            self.sidebar_container.content.controls.append(
                self.create_sidebar_item(item)
            )
        
        # Actualizar ancho del sidebar
        self.sidebar_container.width = (
            self.settings.sidebar_collapsed_width if self.sidebar_collapsed 
            else self.settings.sidebar_width
        )
        
        self.sidebar_container.update()
    
    def select_tool(self, tool_key: str):
        """Seleccionar una herramienta"""
        self.selected_tool = tool_key
        self.settings.last_selected_tool = tool_key
        self.settings_manager.save_settings()
        
        # Actualizar sidebar
        self.update_sidebar()
        
        # Actualizar contenido principal
        self.update_main_content()
    
    def update_main_content(self):
        """Actualizar el contenido principal"""
        if not self.main_content:
            return
            
        # Contenido según la herramienta seleccionada
        content_map = {
            "home": self.create_home_content(),
            "text_tools": self.create_text_tools_content(),
            "file_tools": self.create_file_tools_content(),
            "system_tools": self.create_system_tools_content(),
            "network_tools": self.create_network_tools_content(),
            "calculator": self.create_calculator_content(),
            "settings": self.create_settings_content(),
        }
        
        self.main_content.content = content_map.get(
            self.selected_tool, 
            self.create_home_content()
        )
        self.main_content.update()
    
    def create_home_content(self):
        """Crear contenido de inicio"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Bienvenido a Helper Tools",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors.on_background
                ),
                ft.Text(
                    "Selecciona una herramienta del sidebar para comenzar",
                    size=16,
                    color=self.colors.secondary
                ),
                ft.Container(height=20),
                ft.GridView(
                    expand=True,
                    runs_count=3,
                    max_extent=200,
                    child_aspect_ratio=1.5,
                    spacing=16,
                    run_spacing=16,
                    controls=[
                        self.create_tool_card(item) for item in self.sidebar_items[1:-1]
                    ]
                )
            ]),
            padding=ft.padding.all(24)
        )
    
    def create_tool_card(self, item: SidebarItem):
        """Crear tarjeta de herramienta"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(item.icon, size=32, color=self.colors.primary),
                ft.Text(
                    item.title,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=self.colors.on_surface,
                    text_align=ft.TextAlign.CENTER
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=self.colors.surface,
            border=ft.border.all(1, self.colors.border_color),
            border_radius=12,
            padding=ft.padding.all(16),
            on_click=lambda e, key=item.key: self.select_tool(key)
        )
    
    def create_text_tools_content(self):
        return ft.Container(
            content=ft.Text("Herramientas de Texto - En desarrollo", size=24),
            padding=ft.padding.all(24)
        )
    
    def create_file_tools_content(self):
        return ft.Container(
            content=ft.Text("Herramientas de Archivos - En desarrollo", size=24),
            padding=ft.padding.all(24)
        )
    
    def create_system_tools_content(self):
        return ft.Container(
            content=ft.Text("Herramientas de Sistema - En desarrollo", size=24),
            padding=ft.padding.all(24)
        )
    
    def create_network_tools_content(self):
        return ft.Container(
            content=ft.Text("Herramientas de Red - En desarrollo", size=24),
            padding=ft.padding.all(24)
        )
    
    def create_calculator_content(self):
        return ft.Container(
            content=ft.Text("Calculadora - En desarrollo", size=24),
            padding=ft.padding.all(24)
        )
    
    def create_settings_content(self):
        """Crear contenido de configuraciones"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Configuración",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors.on_background
                ),
                ft.Container(height=20),
                
                # Configuración de tema
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Apariencia", size=18, weight=ft.FontWeight.W_500),
                            ft.Container(height=10),
                            ft.Row([
                                ft.Text("Tema:", size=14),
                                ft.Dropdown(
                                    value=self.settings.theme.value,
                                    options=[
                                        ft.dropdown.Option("light", "Claro"),
                                        ft.dropdown.Option("dark", "Oscuro"),
                                        ft.dropdown.Option("auto", "Automático")
                                    ],
                                    on_change=self.change_theme
                                )
                            ])
                        ]),
                        padding=ft.padding.all(16)
                    )
                ),
                
                # Configuración general
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("General", size=18, weight=ft.FontWeight.W_500),
                            ft.Container(height=10),
                            ft.TextField(
                                label="Título de la aplicación",
                                value=self.settings.app_title,
                                on_change=self.change_app_title
                            )
                        ]),
                        padding=ft.padding.all(16)
                    )
                )
            ]),
            padding=ft.padding.all(24)
        )
    
    def change_theme(self, e):
        """Cambiar tema de la aplicación"""
        new_theme = AppTheme(e.control.value)
        self.settings.theme = new_theme
        self.colors = THEME_COLORS[new_theme]
        self.settings_manager.save_settings()
        
        # Actualizar tema de la página
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT if new_theme == AppTheme.LIGHT
            else ft.ThemeMode.DARK if new_theme == AppTheme.DARK
            else ft.ThemeMode.SYSTEM
        )
        
        # Actualizar interfaz
        self.update_sidebar()
        self.update_main_content()
        self.page.update()
    
    def change_app_title(self, e):
        """Cambiar título de la aplicación"""
        self.settings.app_title = e.control.value
        self.settings_manager.save_settings()
        self.page.title = self.settings.app_title
        self.update_sidebar()
        self.page.update()
    
    def on_keyboard_event(self, e):
        """Manejar eventos de teclado"""
        # Toggle sidebar con Ctrl+B
        if e.key == "B" and e.ctrl:
            self.toggle_sidebar()
        
        # Shortcuts para herramientas
        shortcuts = {
            "H": "home",
            "T": "text_tools", 
            "F": "file_tools",
            "S": "system_tools",
            "N": "network_tools",
            "C": "calculator",
            ",": "settings"
        }
        
        if e.ctrl and e.key in shortcuts:
            self.select_tool(shortcuts[e.key])
    
    def main(self, page: ft.Page):
        """Función principal de la aplicación"""
        self.page = page
        
        # Configuración de la página
        page.title = self.settings.app_title
        page.theme_mode = (
            ft.ThemeMode.LIGHT if self.settings.theme == AppTheme.LIGHT
            else ft.ThemeMode.DARK if self.settings.theme == AppTheme.DARK
            else ft.ThemeMode.SYSTEM
        )
        page.window_width = self.settings.window_width
        page.window_height = self.settings.window_height
        page.window_min_width = 800
        page.window_min_height = 600
        page.padding = 0
        page.spacing = 0
        
        # Manejar eventos de teclado
        page.on_keyboard_event = self.on_keyboard_event
        
        # Crear sidebar
        self.sidebar_container = ft.Container(
            content=ft.Column(scroll=ft.ScrollMode.AUTO),
            width=self.settings.sidebar_width if not self.sidebar_collapsed else self.settings.sidebar_collapsed_width,
            bgcolor=self.colors.sidebar_bg,
            border=ft.border.only(right=ft.border.BorderSide(1, self.colors.border_color))
        )
        
        # Crear contenido principal
        self.main_content = ft.Container(
            content=self.create_home_content(),
            expand=True,
            bgcolor=self.colors.background
        )
        
        # Layout principal
        main_layout = ft.Row([
            self.sidebar_container,
            self.main_content
        ], expand=True, spacing=0)
        
        page.add(main_layout)
        
        # Inicializar sidebar y contenido
        self.update_sidebar()
        self.update_main_content()

def main(page: ft.Page):
    app = MainApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)
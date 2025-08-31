# =============================
# components/drive_sidebar.py
# =============================
import flet as ft
from config.drive_theme import DriveTheme
from config.menu_structure import MenuStructure, TOOL_BUTTONS

class DriveSidebarComponent:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_item = "home"
        self.expanded_submenus = set()  # Para controlar qué submenús están expandidos
        self.menu_structure = MenuStructure()
        self.selected_files = []  # Para almacenar archivos seleccionados
        self.total_size = 0  # Tamaño total de archivos seleccionados
        
        # Configuración de ancho adaptativo
        self.min_width = 160  # Ancho mínimo absoluto
        self.max_width = 280  # Ancho máximo
        self.current_width = self._calculate_optimal_width()
        
    def _calculate_optimal_width(self):
        """Calcula el ancho óptimo basado en el texto más largo del menú"""
        max_text_length = 0
        
        # Verificar elementos principales
        for item in self.menu_structure.get_items():
            text_length = len(item["label"])
            max_text_length = max(max_text_length, text_length)
            
            # Verificar submenús
            for submenu in item.get("submenus", []):
                # Los submenús necesitan espacio adicional por la indentación
                submenu_length = len(submenu["label"]) + 4  # +4 para indentación
                max_text_length = max(max_text_length, submenu_length)
        
        # Verificar herramientas
        for tool in TOOL_BUTTONS:
            text_length = len(tool["label"])
            max_text_length = max(max_text_length, text_length)
        
        # Calcular ancho basado en longitud de texto
        # Aproximadamente 8px por carácter + 60px para iconos y padding
        calculated_width = (max_text_length * 8) + 60
        
        # Aplicar límites mínimo y máximo
        return max(self.min_width, min(calculated_width, self.max_width))
        
    def build(self):
        return ft.Container(
            width=self.current_width,  # Usar ancho calculado dinámicamente
            expand=True,  # Permitir que el sidebar se expanda verticalmente
            content=ft.Column([
                # Botón Open Directory (fijo en la parte superior)
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=18),
                            ft.Text("Open Directory", size=12, weight=ft.FontWeight.W_500),
                        ], spacing=6, tight=True),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            bgcolor=DriveTheme.SURFACE_WHITE,
                            color=DriveTheme.GREY_800,
                            shadow_color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                            elevation=2,
                        ),
                        on_click=self._on_new_click,
                    ),
                    padding=ft.padding.all(10),
                ),
                
                # Área scrollable con ListView que se expande
                ft.Container(
                    content=ft.ListView(
                        controls=self._build_all_menu_content(),
                        spacing=1,
                        padding=ft.padding.symmetric(horizontal=4, vertical=6),
                        auto_scroll=False,
                    ),
                    expand=True,
                ),
                
                # Sección de información de selección
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=1, color=DriveTheme.GREY_200, thickness=1),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Selección", size=12, color=DriveTheme.GREY_600, weight=ft.FontWeight.W_500),
                                ft.Container(
                                    content=self._build_selection_info(),
                                    **DriveTheme.get_card_style(),
                                    padding=8,
                                    margin=ft.margin.only(top=4),
                                )
                            ]),
                            padding=10,
                        )
                    ], spacing=0),
                )
                
            ], spacing=0, expand=True),
            bgcolor=DriveTheme.SURFACE_WHITE,
        )
    
    def build_responsive(self, available_width=None):
        """Versión responsiva que ajusta el ancho según el espacio disponible"""
        if available_width:
            # Calcular qué porcentaje del ancho total debería ocupar el sidebar
            max_sidebar_percentage = 0.25  # Máximo 25% del ancho total
            max_allowed_width = available_width * max_sidebar_percentage
            
            # Usar el menor entre el ancho óptimo y el máximo permitido
            responsive_width = min(self.current_width, max_allowed_width)
            responsive_width = max(responsive_width, self.min_width)  # Respetar mínimo
            
            return ft.Container(
                width=responsive_width,
                expand=True,
                content=self._build_sidebar_content(),
                bgcolor=DriveTheme.SURFACE_WHITE,
            )
        else:
            return self.build()
    
    def _build_sidebar_content(self):
        """Construye el contenido interno del sidebar (reutilizable)"""
        return ft.Column([
            # Botón Open Directory
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=18),
                        ft.Text("Open Directory", size=12, weight=ft.FontWeight.W_500),
                    ], spacing=6, tight=True),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        bgcolor=DriveTheme.SURFACE_WHITE,
                        color=DriveTheme.GREY_800,
                        shadow_color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                        elevation=2,
                    ),
                    on_click=self._on_new_click,
                ),
                padding=ft.padding.all(10),
            ),
            
            # Área scrollable
            ft.Container(
                content=ft.ListView(
                    controls=self._build_all_menu_content(),
                    spacing=1,
                    padding=ft.padding.symmetric(horizontal=4, vertical=6),
                    auto_scroll=False,
                ),
                expand=True,
            ),
            
            # Sección de selección
            ft.Container(
                content=ft.Column([
                    ft.Divider(height=1, color=DriveTheme.GREY_200, thickness=1),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Selección", size=12, color=DriveTheme.GREY_600, weight=ft.FontWeight.W_500),
                            ft.Container(
                                content=self._build_selection_info(),
                                **DriveTheme.get_card_style(),
                                padding=8,
                                margin=ft.margin.only(top=4),
                            )
                        ]),
                        padding=10,
                    )
                ], spacing=0),
            )
        ], spacing=0, expand=True)
    
    def update_width_for_content(self):
        """Recalcula y actualiza el ancho óptimo cuando cambia el contenido"""
        new_width = self._calculate_optimal_width()
        if new_width != self.current_width:
            self.current_width = new_width
            self.page.update()
    
    def get_optimal_width(self):
        """Obtiene el ancho óptimo actual"""
        return self.current_width
    
    def get_width_info(self):
        """Información sobre el ancho del sidebar para debugging"""
        return {
            "current_width": self.current_width,
            "min_width": self.min_width,
            "max_width": self.max_width,
            "calculated_optimal": self._calculate_optimal_width()
        }
    
    def _build_all_menu_content(self):
        """Construye todo el contenido del menú para ListView"""
        controls = []
        
        # Agregar elementos del menú
        for item in self.menu_structure.get_items():
            # Item principal
            main_item = self._create_nav_item(
                key=item["key"],
                icon=item["icon"], 
                text=item["label"],
                has_submenu=bool(item.get("submenus"))
            )
            controls.append(main_item)
            
            # Submenús (si existen y están expandidos)
            if item.get("submenus") and item["key"] in self.expanded_submenus:
                for submenu in item["submenus"]:
                    submenu_item = self._create_submenu_item(
                        key=submenu["key"],
                        text=submenu["label"],
                        parent_key=item["key"]
                    )
                    controls.append(submenu_item)
        
        # Agregar separador si hay herramientas
        if TOOL_BUTTONS:
            controls.append(ft.Divider(height=1, color=DriveTheme.GREY_200))
            controls.append(
                ft.Container(
                    content=ft.Text("Herramientas", size=14, color=DriveTheme.GREY_600),
                    padding=ft.padding.only(left=16, top=8, bottom=8),
                )
            )
            
            # Agregar herramientas
            for tool in TOOL_BUTTONS:
                tool_item = self._create_tool_item(
                    key=tool["key"],
                    icon=tool["icon"],
                    text=tool["label"]
                )
                controls.append(tool_item)
        
        return controls
    
    def _build_tool_section(self):
        """Construye la sección de herramientas si existe"""
        if not TOOL_BUTTONS:
            return []
            
        tools_section = [
            ft.Container(
                content=ft.Text("Herramientas", size=14, color=DriveTheme.GREY_600),
                padding=ft.padding.only(left=16, top=8, bottom=8),
            )
        ]
        
        for tool in TOOL_BUTTONS:
            tool_item = self._create_tool_item(
                key=tool["key"],
                icon=tool["icon"],
                text=tool["label"]
            )
            tools_section.append(tool_item)
            
        return tools_section
    
    def _create_nav_item(self, key: str, icon: str, text: str, has_submenu: bool = False):
        """Crea un elemento de navegación principal"""
        is_selected = self.selected_item == key
        is_expanded = key in self.expanded_submenus
        
        # Icono de expansión para submenús
        trailing_icon = None
        if has_submenu:
            trailing_icon = ft.Icon(
                ft.Icons.KEYBOARD_ARROW_DOWN if is_expanded else ft.Icons.KEYBOARD_ARROW_RIGHT,
                color=DriveTheme.GREY_600,
                size=14  # Icono más pequeño
            )
        
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    icon,
                    color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_600,
                    size=18  # Icono más pequeño
                ),
                title=ft.Text(
                    text,
                    color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_800,
                    size=12,  # Texto más pequeño
                    weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.W_400
                ),
                trailing=trailing_icon,
                on_click=lambda e, k=key, has_sub=has_submenu: self._on_nav_click(k, has_sub),
                content_padding=ft.padding.symmetric(horizontal=8, vertical=2),  # Padding muy reducido
            ),
            bgcolor=ft.Colors.with_opacity(0.1, DriveTheme.PRIMARY_BLUE) if is_selected else None,
            border_radius=6,  # Radio más pequeño
            margin=ft.margin.symmetric(vertical=0, horizontal=2),  # Margen mínimo
        )
    
    def _create_submenu_item(self, key: str, text: str, parent_key: str):
        """Crea un elemento de submenú"""
        is_selected = self.selected_item == key
        
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Container(width=18),  # Espaciado para indentación, más pequeño
                title=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.CIRCLE, size=3, color=DriveTheme.GREY_400),  # Punto más pequeño
                        margin=ft.margin.only(right=8)  # Margen reducido
                    ),
                    ft.Text(
                        text,
                        color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_700,
                        size=11,  # Texto más pequeño para submenús
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.W_400
                    ),
                ], tight=True),
                on_click=lambda e, k=key: self._on_submenu_click(k, parent_key),
                content_padding=ft.padding.only(left=14, right=8, top=1, bottom=1),  # Padding muy reducido
            ),
            bgcolor=ft.Colors.with_opacity(0.05, DriveTheme.PRIMARY_BLUE) if is_selected else None,
            border_radius=6,
            margin=ft.margin.only(left=12, right=2, top=0, bottom=0),  # Margen muy reducido
        )
    
    def _create_tool_item(self, key: str, icon: str, text: str):
        """Crea un elemento de herramienta"""
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    icon,
                    color=DriveTheme.GREY_600,
                    size=16  # Icono más pequeño
                ),
                title=ft.Text(
                    text,
                    color=DriveTheme.GREY_800,
                    size=11,  # Texto más pequeño
                    weight=ft.FontWeight.W_400
                ),
                on_click=lambda e, k=key: self._on_tool_click(k),
                content_padding=ft.padding.symmetric(horizontal=8, vertical=1),  # Padding muy reducido
            ),
            border_radius=6,
            margin=ft.margin.symmetric(horizontal=2, vertical=0),  # Margen mínimo
        )
    
    def _on_nav_click(self, key: str, has_submenu: bool = False):
        """Maneja el clic en elementos principales del menú"""
        if has_submenu:
            # Si tiene submenús, alternar expansión
            if key in self.expanded_submenus:
                self.expanded_submenus.remove(key)
            else:
                self.expanded_submenus.add(key)
        else:
            # Si no tiene submenús, seleccionar el item
            self.selected_item = key
            
        self.page.update()
    
    def _on_submenu_click(self, key: str, parent_key: str):
        """Maneja el clic en elementos de submenú"""
        self.selected_item = key
        # También podrías ejecutar una acción específica aquí
        print(f"Submenu clicked: {key} (parent: {parent_key})")
        self.page.update()
    
    def _on_tool_click(self, key: str):
        """Maneja el clic en herramientas"""
        print(f"Tool clicked: {key}")
        # Implementar lógica específica para cada herramienta
        if key == "chrome":
            # Abrir Chrome o realizar acción específica
            pass
        elif key == "firefox":
            # Abrir Firefox o realizar acción específica
            pass
    
    def _on_new_click(self, e):
        """Maneja el clic en el botón de nuevo archivo/directorio"""
        # Implementar menú contextual o diálogo
        print("Open Directory clicked")
        pass
    
    def select_item(self, key: str):
        """Método público para seleccionar un item programáticamente"""
        self.selected_item = key
        self.page.update()
    
    def expand_submenu(self, parent_key: str):
        """Método público para expandir un submenú programáticamente"""
        self.expanded_submenus.add(parent_key)
        self.page.update()
    
    def build_responsive_height(self, available_height=None):
        """Versión que se adapta a la altura disponible de la ventana"""
        # Calcular altura dinámica para el área scrollable
        header_height = 80   # Altura aproximada del botón superior
        footer_height = 140  # Altura aproximada de la sección de almacenamiento
        min_scroll_height = 200  # Altura mínima para el área scrollable
        
        if available_height:
            scroll_height = max(available_height - header_height - footer_height, min_scroll_height)
        else:
            scroll_height = 400  # Valor por defecto
            
        return ft.Container(
            width=280,
            content=ft.Column([
                # Botón Nuevo/Open Directory (fijo en la parte superior)
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=20),
                            ft.Text("Open Directory", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=8, tight=True),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=16),
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            bgcolor=DriveTheme.SURFACE_WHITE,
                            color=DriveTheme.GREY_800,
                            shadow_color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                            elevation=2,
                        ),
                        on_click=self._on_new_click,
                    ),
                    padding=ft.padding.all(16),
                ),
                
                # Área scrollable con ListView
                ft.Container(
                    content=ft.ListView(
                        controls=self._build_all_menu_content(),
                        spacing=2,
                        padding=ft.padding.symmetric(horizontal=8, vertical=8),
                        auto_scroll=False,
                    ),
                    height=scroll_height,
                ),
                
                # Sección de almacenamiento (fija en la parte inferior)
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=1, color=DriveTheme.GREY_200, thickness=1),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Almacenamiento", size=14, color=DriveTheme.GREY_600),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.CLOUD_OUTLINED, size=16, color=DriveTheme.GREY_600),
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
                )
                
            ], spacing=0),
            bgcolor=DriveTheme.SURFACE_WHITE,
        )

    def _build_selection_info(self):
        """Construye la información de archivos seleccionados"""
        if not self.selected_files:
            return ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=DriveTheme.GREY_400),  # Icono más pequeño
                    ft.Text("Sin selección", size=10, color=DriveTheme.GREY_700),  # Texto más corto y pequeño
                ], spacing=4),  # Spacing reducido
            ])
        
        file_count = len(self.selected_files)
        size_text = self._format_file_size(self.total_size)
        
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OUTLINED if file_count > 1 else ft.Icons.INSERT_DRIVE_FILE_OUTLINED, 
                       size=14, color=DriveTheme.GREY_600),  # Icono más pequeño
                ft.Text(f"{file_count} elem.", 
                       size=10, color=DriveTheme.GREY_600),  # Texto abreviado y más pequeño
            ], spacing=4),  # Spacing reducido
            ft.Row([
                ft.Icon(ft.Icons.DATA_USAGE, size=12, color=DriveTheme.GREY_700),  # Icono más pequeño
                ft.Text(size_text, size=9, color=DriveTheme.GREY_700),  # Solo el tamaño, texto más pequeño
            ], spacing=4),  # Spacing reducido
        ], spacing=2)  # Spacing entre filas reducido
    
    def _format_file_size(self, size_bytes):
        """Formatea el tamaño del archivo en formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size_bytes)} {size_names[i]}"
        else:
            return f"{size_bytes:.1f} {size_names[i]}"
    
    def update_selection(self, selected_files_info):
        """Actualiza la información de archivos seleccionados desde el explorador"""
        # selected_files_info es una lista de diccionarios con info de archivos
        # Ejemplo: [{"name": "archivo.txt", "size": 1024, "type": "file"}, ...]
        self.selected_files = selected_files_info
        self.total_size = sum(file_info.get("size", 0) for file_info in selected_files_info)
        self.page.update()
    
    def clear_selection(self):
        """Limpia la selección de archivos"""
        self.selected_files = []
        self.total_size = 0
        self.page.update()
    
    def get_selection_info(self):
        """Obtiene información de la selección actual"""
        return {
            "count": len(self.selected_files),
            "total_size": self.total_size,
            "files": self.selected_files
        }
    
    def build_collapsed(self):
        """Versión colapsada del sidebar - solo iconos"""
        return ft.Container(
            width=60,  # Ancho muy reducido para solo iconos
            expand=True,
            content=ft.Column([
                # Botón Open Directory colapsado
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        icon_size=20,
                        tooltip="Open Directory",
                        on_click=self._on_new_click,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            bgcolor=DriveTheme.SURFACE_WHITE,
                            color=DriveTheme.GREY_800,
                        ),
                    ),
                    padding=ft.padding.all(8),
                ),
                
                # Área scrollable solo con iconos
                ft.Container(
                    content=ft.ListView(
                        controls=self._build_collapsed_menu_items(),
                        spacing=2,
                        padding=ft.padding.symmetric(horizontal=4, vertical=8),
                        auto_scroll=False,
                    ),
                    expand=True,
                ),
                
                # Sección de selección colapsada
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=1, color=DriveTheme.GREY_200, thickness=1),
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.INFO_OUTLINE,
                                icon_size=16,
                                tooltip=f"{len(self.selected_files)} elementos seleccionados",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                ),
                            ),
                            padding=ft.padding.all(4),
                        )
                    ], spacing=0),
                )
            ], spacing=0, expand=True),
            bgcolor=DriveTheme.SURFACE_WHITE,
        )
    
    def _build_collapsed_menu_items(self):
        """Construye los elementos del menú colapsado (solo iconos)"""
        controls = []
        
        for item in self.menu_structure.get_items():
            # Solo items principales en modo colapsado
            collapsed_item = self._create_collapsed_nav_item(
                key=item["key"],
                icon=item["icon"],
                tooltip=item["label"],
                has_submenu=bool(item.get("submenus"))
            )
            controls.append(collapsed_item)
        
        # Agregar separador y herramientas si existen
        if TOOL_BUTTONS:
            controls.append(ft.Container(height=8))  # Espaciador
            for tool in TOOL_BUTTONS[:3]:  # Solo mostrar primeras 3 herramientas
                tool_item = self._create_collapsed_tool_item(
                    key=tool["key"],
                    icon=tool["icon"],
                    tooltip=tool["label"]
                )
                controls.append(tool_item)
        
        return controls
    
    def _create_collapsed_nav_item(self, key: str, icon: str, tooltip: str, has_submenu: bool = False):
        """Crea un elemento de navegación colapsado (solo icono)"""
        is_selected = self.selected_item == key
        
        return ft.Container(
            content=ft.IconButton(
                icon=icon,
                icon_size=18,
                tooltip=tooltip,
                on_click=lambda e, k=key: self._on_nav_click(k, has_submenu),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    bgcolor=ft.Colors.with_opacity(0.15, DriveTheme.PRIMARY_BLUE) if is_selected else None,
                    color=DriveTheme.PRIMARY_BLUE if is_selected else DriveTheme.GREY_600,
                ),
            ),
            margin=ft.margin.symmetric(vertical=1, horizontal=4),
        )
    
    def collapse_submenu(self, parent_key: str):
        """Método público para colapsar un submenú programáticamente"""
        self.expanded_submenus.discard(parent_key)
        self.page.update()
    
    def _create_collapsed_tool_item(self, key: str, icon: str, tooltip: str):
        """Crea un elemento de herramienta colapsado (solo icono)"""
        return ft.Container(
            content=ft.IconButton(
                icon=icon,
                icon_size=16,
                tooltip=tooltip,
                on_click=lambda e, k=key: self._on_tool_click(k),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    color=DriveTheme.GREY_600,
                ),
            ),
            margin=ft.margin.symmetric(vertical=1, horizontal=4),
        )
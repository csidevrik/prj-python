# =============================
# components/header/tools_component.py (MEJORADO)
# =============================
import flet as ft
from typing import List, Callable, Optional
from config.drive_theme import DriveTheme

class ToolButton:
    def __init__(
        self, 
        icon: str, 
        tooltip: str, 
        on_click: Optional[Callable] = None,
        badge_count: Optional[int] = None,
        mobile_priority: int = 0  # 0=ocultar en móvil, 1=mostrar siempre, 2=mostrar en hamburger
    ):
        self.icon = icon
        self.tooltip = tooltip
        self.on_click = on_click
        self.badge_count = badge_count
        self.mobile_priority = mobile_priority

class ToolsComponent:
    def __init__(self, tools: List[ToolButton], mobile_mode: bool = False):
        self.tools = tools
        self.mobile_mode = mobile_mode
    
    def build(self):
        if self.mobile_mode:
            # En móvil, solo mostrar herramientas con prioridad 1
            visible_tools = [tool for tool in self.tools if tool.mobile_priority == 1]
            if not visible_tools:
                return ft.Container(width=0, height=0)  # Container vacío
        else:
            visible_tools = self.tools
        
        tool_buttons = []
        
        for tool in visible_tools:
            button = ft.IconButton(
                icon=tool.icon,
                tooltip=tool.tooltip,
                icon_color=DriveTheme.GREY_600,
                on_click=tool.on_click,
                icon_size=20 if self.mobile_mode else 24,
            )
            
            # Badge handling
            if tool.badge_count and tool.badge_count > 0:
                tool_buttons.append(
                    ft.Stack([
                        button,
                        ft.Container(
                            content=ft.Text(
                                str(tool.badge_count),
                                size=9 if self.mobile_mode else 10,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ft.Colors.RED,
                            border_radius=8,
                            padding=ft.padding.all(3),
                            right=2,
                            top=2,
                            width=16,
                            height=16,
                        )
                    ])
                )
            else:
                tool_buttons.append(button)
        
        return ft.Container(
            content=ft.Row(tool_buttons, spacing=2 if self.mobile_mode else 4),
            padding=ft.padding.symmetric(horizontal=8),
        )
# =============================
# components/header/user_session.py (MEJORADO)
# =============================
import flet as ft
from typing import Optional, Callable
from config.drive_theme import DriveTheme

class UserSessionComponent:
    def __init__(
        self, 
        user_name: str = "U",
        user_email: Optional[str] = None,
        avatar_url: Optional[str] = None,
        on_profile_click: Optional[Callable] = None,
        on_logout_click: Optional[Callable] = None,
        mobile_mode: bool = False
    ):
        self.user_name = user_name
        self.user_email = user_email
        self.avatar_url = avatar_url
        self.on_profile_click = on_profile_click
        self.on_logout_click = on_logout_click
        self.mobile_mode = mobile_mode
    
    def build(self):
        avatar_size = 14 if self.mobile_mode else 16
        
        avatar_content = ft.CircleAvatar(
            content=ft.Text(
                self.user_name[0].upper() if self.user_name else "U",
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=12 if self.mobile_mode else 14,
            ),
            bgcolor=DriveTheme.PRIMARY_BLUE,
            radius=avatar_size,
        )
        
        return ft.Container(
            content=ft.PopupMenuButton(
                content=avatar_content,
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=18),
                            ft.Text("Mi Perfil", size=14)
                        ], spacing=8),
                        on_click=lambda _: self.on_profile_click() if self.on_profile_click else None
                    ),
                    ft.PopupMenuItem(),  # Divider
                    ft.PopupMenuItem(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGOUT, size=18),
                            ft.Text("Cerrar Sesión", size=14)
                        ], spacing=8),
                        on_click=lambda _: self.on_logout_click() if self.on_logout_click else None
                    ),
                ]
            ),
            padding=ft.padding.all(4),
        )
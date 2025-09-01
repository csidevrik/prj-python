import flet as ft
from src.components.layout.main_layout import MainLayout
from src.config.settings import AppSettings

def main(page: ft.Page):
    try:
        # Configuración inicial de la página
        settings = AppSettings()
        
        page.title              = settings.APP_TITLE
        page.window.width       = settings.WINDOW_WIDTH
        page.window.height      = settings.WINDOW_HEIGHT
        page.window.min_width   = settings.WINDOW_MIN_WIDTH
        page.window.min_height  = settings.WINDOW_MIN_HEIGHT
        page.theme_mode         = ft.ThemeMode.LIGHT
        page.padding            = 0
        page.spacing            = 0
        
        # Crear layout principal
        main_layout = MainLayout(page)
        
        # Agregar al page
        page.add(main_layout.build())
        
        print("✅ FACRET iniciado correctamente")
        
    except Exception as e:
        print(f"❌ Error al iniciar FACRET: {e}")
        # Crear vista de error simple
        error_view = ft.Container(
            content=ft.Column([
                ft.Text("Error al iniciar FACRET", size=24, color="red"),
                ft.Text(f"Error: {str(e)}", size=14),
                ft.ElevatedButton(
                    text="Reintentar", 
                    on_click=lambda _: page.update()
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        page.add(error_view)

if __name__ == "__main__":
    print("🚀 Iniciando FACRET...")
    ft.app(target=main, view=ft.AppView.FLET_APP)
# if __name__ == "__main__":
#     ft.app(target=main, view=ft.AppView.FLET_APP)
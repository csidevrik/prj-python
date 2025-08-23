import flet as ft
from components.app_bar         import AppBarComponent
from components.nav_rail        import NavRailComponent
from components.file_explorer   import FileExplorerComponent
from components.preview_panel   import PreviewPanel

from config.theme import AppGradients

def run_gui():
    def main(page: ft.Page):
        page.window.icon = "../assets/favicon.ico"
        def toggle_nav_rail(e=None):  # Añadir parámetro e=None
            nav_rail.visible = not nav_rail.visible
            nav_rail.update()
        
        # Inicializar componentes
        app_bar         = AppBarComponent(page, on_menu_click=toggle_nav_rail)
        nav_rail        = NavRailComponent(page)
        file_explorer   = FileExplorerComponent(page)
        preview         = PreviewPanel()

        # Layout principal
        layout = ft.Column([
            app_bar.build(),
            ft.Row([
                nav_rail.build(),
                ft.VerticalDivider(width=1),
                ft.Row([
                    file_explorer.build(),
                    ft.VerticalDivider(width=1),
                    preview.build(),
                ], expand=True),
            ], expand=True),
        ], expand=True)

        page.add(layout)

        # Para reemplazar el logo de Flet en la AppBar:
        # 1. Usa un archivo de imagen local (ej: "assets/logo.png") o un SVG.
        # 2. Cambia el parámetro 'leading' de tu AppBar o Container por un ft.Image o ft.Image.asset.

        custom_bar_content = ft.Row(
            [
                # Reemplaza el icono por tu logo personalizado
                ft.Image(
                    src="../assets/favicon.png",  # Cambia la ruta a tu logo
                    width=32,
                    height=32,
                    fit=ft.ImageFit.CONTAIN,
                ),
                # ...existing code...
            ],
            # ...existing code...
        )

    ft.app(target=main)

# ¿Qué es Flet Desktop?
# ---------------------
# Flet Desktop es una variante de Flet que permite crear aplicaciones de escritorio (Windows, macOS, Linux)
# usando Python y la misma API de Flet. Permite acceso a recursos locales y controles nativos.
# Para usar Flet Desktop, simplemente ejecuta tu app con `flet` instalado y NO uses el modo web.
# Más info: https://flet.dev/docs/desktop

# ¿Qué es Poppler?
# ----------------
# Poppler es una librería de código abierto para procesar archivos PDF.
# Es utilizada por herramientas como pdf2image para convertir páginas PDF a imágenes.
# En Windows, debes descargar los binarios de Poppler y agregar su carpeta `bin` al PATH del sistema.
# Descarga: https://github.com/oschwartz10612/poppler-windows/releases/
# En Linux/Mac puedes instalarlo con el gestor de paquetes (ej: `sudo apt install poppler-utils`).

# ¿Para qué sirve Poppler?
# ------------------------
# Poppler es una librería de código abierto especializada en procesar archivos PDF.
# Su función principal es permitir la conversión de páginas PDF a imágenes (PNG, JPEG, etc.)
# y la extracción de contenido de archivos PDF.
#
# En Python, Poppler es utilizada por librerías como pdf2image para convertir páginas PDF en imágenes,
# lo que permite mostrar previsualizaciones de PDFs en aplicaciones gráficas (como Flet, Tkinter, etc.).
#
# Ejemplo de uso:
# - pdf2image usa Poppler para abrir un PDF y convertir la primera página en una imagen PNG.
# - Luego puedes mostrar esa imagen en tu aplicación.
#
# En resumen: Poppler es el motor que hace posible la conversión de PDF a imagen en tu app Python.
# Debes instalarlo en tu sistema para que pdf2image funcione correctamente.

# ¿Qué hace Poppler en Windows?
# -----------------------------
# Poppler en Windows es un conjunto de utilidades y librerías que permiten procesar archivos PDF.
# Su función principal en tu proyecto es servir como backend para convertir páginas PDF a imágenes (PNG, JPEG, etc.)
# cuando usas librerías Python como pdf2image.
#
# ¿Por qué lo necesitas?
# - pdf2image (y otras librerías) no pueden convertir PDFs a imágenes por sí solas.
# - pdf2image llama internamente a las utilidades de Poppler (como pdftoppm.exe) para hacer la conversión.
# - Por eso, debes descargar Poppler para Windows y agregar la carpeta `bin` de Poppler al PATH de tu sistema.
#
# Ejemplo de flujo:
# 1. Tu código llama a pdf2image.convert_from_path("archivo.pdf").
# 2. pdf2image ejecuta pdftoppm.exe (de Poppler) para convertir la página del PDF a una imagen.
# 3. pdf2image recibe la imagen y tú la muestras en tu app Flet.
#
# Sin Poppler, pdf2image no puede funcionar en Windows y no podrás previsualizar PDFs como imágenes.

# NOTA IMPORTANTE SOBRE POPPLER Y DISTRIBUCIÓN DE TU APP
# -------------------------------------------------------
# Si quieres entregar tu proyecto como un solo .exe para usuarios no técnicos de Windows,
# lo ideal es incluir los binarios de Poppler dentro de tu instalador o carpeta del proyecto.
#
# ¿Cómo hacerlo?
# 1. Descarga Poppler para Windows y copia la carpeta "bin" (con pdftoppm.exe, etc.) dentro de tu proyecto,
#    por ejemplo: c:\Users\adminos\dev\github\prj-python\facret\poppler\bin
# 2. Al llamar a convert_from_path, pasa el argumento poppler_path con la ruta relativa:
#    images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path="poppler/bin")
# 3. Si usas PyInstaller para crear el .exe, asegúrate de incluir la carpeta poppler/bin en el bundle.
#
# Así, tus usuarios no tendrán que instalar ni configurar nada extra.
#
# Ejemplo de integración:
#   images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=os.path.join(os.getcwd(), "poppler", "bin"))
#
# Esto hace tu app portable y fácil de usar para cualquier usuario de Windows.

# ¿Dónde ubicar poppler/bin?
# --------------------------
# Lo ideal es que la carpeta poppler/bin esté dentro de tu proyecto, por ejemplo:
# c:\Users\adminos\dev\github\prj-python\facret\src\poppler\bin
#
# Así, puedes usar en tu código:
#   poppler_path = os.path.join(os.path.dirname(__file__), "poppler", "bin")
#   images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
#
# Esto asegura que funcione tanto en desarrollo como en el .exe generado.
# Si usas PyInstaller, incluye src/poppler/bin como parte del bundle.

# Comentario final:
# -----------------
# Flet con Python permite lograr una experiencia de preview de archivos bastante funcional y multiplataforma,
# pero si buscas una experiencia visual y de integración nativa idéntica al File Explorer de Windows,
# tecnologías como Flutter o React Native para Windows pueden ofrecer más flexibilidad gráfica y controles nativos.
# Sin embargo, requieren más configuración y conocimientos de sus respectivos ecosistemas.

# Puedes seguir mejorando tu prototipo en Flet y luego comparar con Flutter/React Native para decidir
# cuál se adapta mejor a tus necesidades y a la experiencia de usuario que buscas.
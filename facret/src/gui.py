import flet as ft
import os
# from src.logic.logic import clean_xml_files, process_all_xml_files

# Ejemplo de framework básico para una GUI con subsecciones tipo Outlook/Fluent UI

class AppGradients:
    @staticmethod
    def main():
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#578881", "#B7EF50"],
        )

    @staticmethod
    def sidebar():
        return ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#B0B0B0", "#E0E0E0"],
        )

    @staticmethod
    def header():
        return ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=["#46758A", "#B7EF50"],
        )

# Modelo de menú y subsecciones
MENU_STRUCTURE = [
    {
        "key": "home",
        "icon": ft.Icons.HOME,
        "label": "Inicio",
        "submenus": []
    },
    {
        "key": "facturas",
        "icon": ft.Icons.RECEIPT,
        "label": "Facturas",
        "submenus": [
            {"key": "facturas_pendientes", "label": "Pendientes"},
            {"key": "facturas_procesadas", "label": "Procesadas"},
        ]
    },
    {
        "key": "retenciones",
        "icon": ft.Icons.RECEIPT_LONG,
        "label": "Retenciones",
        "submenus": [
            {"key": "retenciones_pendientes", "label": "Pendientes"},
            {"key": "retenciones_procesadas", "label": "Procesadas"},
        ]
    },
    {
        "key": "settings",
        "icon": ft.Icons.SETTINGS,
        "label": "Configuración",
        "submenus": [
            {"key": "general", "label": "General"},
            {"key": "apariencia", "label": "Apariencia"},
            {"key": "notificaciones", "label": "Notificaciones"},
        ]
    }
]

class ContentAreas:
    @staticmethod
    def home():
        return ft.Text("Bienvenido a FACRET", size=24)

    @staticmethod
    def facturas(subkey=None):
        if subkey == "facturas_pendientes":
            return ft.Text("Facturas Pendientes")
        elif subkey == "facturas_procesadas":
            return ft.Text("Facturas Procesadas")
        return ft.Text("Panel de Facturas")

    @staticmethod
    def retenciones(subkey=None):
        if subkey == "retenciones_pendientes":
            return ft.Text("Retenciones Pendientes")
        elif subkey == "retenciones_procesadas":
            return ft.Text("Retenciones Procesadas")
        return ft.Text("Panel de Retenciones")

    @staticmethod
    def settings(subkey=None):
        submenu_map = {
            "general": ft.Text("Configuración General"),
            "apariencia": ft.Text("Configuración de Apariencia"),
            "notificaciones": ft.Text("Configuración de Notificaciones"),
        }
        return ft.Column([
            ft.Text("Configuración", size=20, weight="bold"),
            ft.TextField(label="Buscar en configuración...", width=300),
            ft.Row([
                ft.Column([
                    ft.Text("General", weight="bold", bgcolor="#f7f7a1" if subkey == "general" else None),
                    ft.Text("Apariencia", bgcolor="#f7f7a1" if subkey == "apariencia" else None),
                    ft.Text("Notificaciones", bgcolor="#f7f7a1" if subkey == "notificaciones" else None),
                ], width=150),
                ft.VerticalDivider(width=2),
                ft.Container(
                    submenu_map.get(subkey, ft.Text("Selecciona una subsección")),
                    expand=True,
                    bgcolor="#f9f9f9",
                    padding=10,
                )
            ], expand=True)
        ], expand=True, spacing=20)

def run_gui():
    def main(page: ft.Page):
        # page.window.title_bar_hidden = True  # Oculta la barra de título del sistema

        def button_exit(e):
            page.window.destroy()
            page.update()

        def button_maximize(e):
            page.window.height = 1080
            page.window.width = 1920
            page.update()

        def button_minimize(e):
            page.window.minimized = True
            page.update()

        # --- AppBar personalizada con drag para mover ventana ---
        def on_appbar_drag(e):
            # Solo intenta mover la ventana si el método existe y es callable
            drag_move = getattr(page.window, "drag_move", None)
            if callable(drag_move):
                drag_move()

        # Estado para el campo de búsqueda y sugerencias
        search_expanded = False
        search_history = [
            {"text": "Factura 001", "action": lambda: print("Ir a Factura 001")},
            {"text": "Retención 2024", "action": lambda: print("Ir a Retención 2024")},
            {"text": "Configuración", "action": lambda: print("Ir a Configuración")},
        ]
        search_field = ft.TextField(
            visible=False,
            width=0,
            height=36,
            hint_text="Buscar...",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=10),
            autofocus=True,
            on_change=lambda e: update_suggestions(e.control.value),
        )
        suggestions_dropdown = ft.Column(visible=False, spacing=0)

        def update_suggestions(query):
            filtered = [s for s in search_history if query.lower() in s["text"].lower()]
            suggestions_dropdown.controls.clear()
            for s in filtered:
                suggestions_dropdown.controls.append(
                    ft.ListTile(
                        title=ft.Text(s["text"]),
                        on_click=lambda e, action=s["action"]: (action(), collapse_search()),
                    )
                )
            suggestions_dropdown.visible = bool(filtered)
            suggestions_dropdown.update()

        def expand_search(e):
            nonlocal search_expanded
            search_expanded = True
            search_field.visible = True
            search_field.width = 250
            search_field.focus()
            suggestions_dropdown.visible = False
            search_field.update()
            suggestions_dropdown.update()

        def collapse_search():
            nonlocal search_expanded
            search_expanded = False
            search_field.visible = False
            search_field.width = 0
            suggestions_dropdown.visible = False
            search_field.value = ""
            search_field.update()
            suggestions_dropdown.update()

        # Estado para mostrar/ocultar el nav rail
        nav_rail_visible = False

        def toggle_nav_rail(e=None):
            nonlocal nav_rail_visible
            nav_rail_visible = not nav_rail_visible
            nav_rail.visible = nav_rail_visible
            nav_rail.update()

        # --- AppBar personalizada con drag para mover ventana ---
        def on_appbar_drag(e):
            # Solo intenta mover la ventana si el método existe y es callable
            drag_move = getattr(page.window, "drag_move", None)
            if callable(drag_move):
                drag_move()

        custom_bar_content = ft.Row(
            [
                # Icono de hamburguesa a la izquierda

                ft.Text("AppBar", color="black", weight="bold", size=14, tooltip="Title app"),
                ft.Container(expand=True),
                # Campo de búsqueda y sugerencias
                ft.Stack(
                    [
                        search_field,
                        ft.Container(
                            suggestions_dropdown,
                            top=40,
                            left=0,
                            width=250,
                            bgcolor="#fff",
                            border_radius=8,
                            border=ft.border.all(1, "#ccc"),
                            shadow=ft.BoxShadow(blur_radius=4, color="#88888822"),
                            visible=suggestions_dropdown.visible,
                        ),
                    ],
                    width=250,
                    height=50,
                ),
                ft.Row(
                    [
                        # Botón de búsqueda
                        ft.IconButton(
                            ft.Icons.SEARCH,
                            icon_color="black",
                            tooltip="Buscar",
                            style=ft.ButtonStyle(padding=0, shape=None),
                            on_click=expand_search,
                        ),
                        # Botón de menú hamburguesa (ahora con toggle)
                        ft.IconButton(
                            ft.Icons.MENU,
                            icon_color="black",
                            tooltip="Menú",
                            style=ft.ButtonStyle(padding=0, shape=None),
                            on_click=toggle_nav_rail,
                        ),
                        # Botón de notificaciones
                        ft.IconButton(
                            ft.Icons.NOTIFICATIONS,
                            icon_color="black",
                            tooltip="Notificaciones",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                        # Ejemplos de otros botones útiles en la AppBar:
                        # Botón de usuario/perfil
                        ft.IconButton(
                            ft.Icons.ACCOUNT_CIRCLE,
                            icon_color="black",
                            tooltip="Perfil de usuario",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                        # Botón de configuración
                        ft.IconButton(
                            ft.Icons.SETTINGS,
                            icon_color="black",
                            tooltip="Configuración",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                        # Botón de ayuda
                        ft.IconButton(
                            ft.Icons.HELP_OUTLINE,
                            icon_color="black",
                            tooltip="Ayuda",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                        # Botón de tema (oscuro/claro)
                        ft.IconButton(
                            ft.Icons.DARK_MODE,
                            icon_color="black",
                            tooltip="Cambiar tema",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                        # Botón de logout/cerrar sesión
                        ft.IconButton(
                            ft.Icons.LOGOUT,
                            icon_color="black",
                            tooltip="Cerrar sesión",
                            style=ft.ButtonStyle(padding=0, shape=None),
                        ),
                    ],
                    spacing=10,
                ),
                # ft.Row(
                #     [
                #         ft.IconButton(
                #             ft.Icons.MINIMIZE,
                #             icon_color="white",
                #             on_click=button_minimize,
                #             tooltip="Minimizar"
                #         ),
                #         ft.IconButton(
                #             ft.Icons.CROP_SQUARE,
                #             icon_color="white",
                #             on_click=button_maximize,
                #             tooltip="Maximizar"
                #         ),
                #         ft.IconButton(
                #             ft.Icons.CLOSE,
                #             icon_color="white",
                #             on_click=button_exit,
                #             tooltip="Cerrar"
                #         ),
                #     ],
                #     spacing=0,
                # ),
            ],
            alignment="start",
            vertical_alignment="center",
        )

        custom_bar = ft.GestureDetector(
            content=ft.Container(
                content=custom_bar_content,
                height=48,
                bgcolor="#3DDCFC",
                padding=ft.padding.symmetric(horizontal=16),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=["#46758A", "#B7EF50"],
                ),
            ),
            on_pan_start=on_appbar_drag,
        )

        # Calcular el ancho óptimo del nav rail según el texto más largo
        menu_labels = ["Chrome", "Firefox", "Facturas", "Retenciones", "Pagos", "Configuración"]
        max_label_len = max(len(label) for label in menu_labels)
        nav_width = 40 + max_label_len * 12  # 40px para icono y padding, 12px por letra aprox

        # Nav rail SOLO con menú, sin contenido de archivos ni preview
        nav_rail = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Menú", color="black", size=14, text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    *[
                        ft.ListTile(
                            leading=ft.Icon(menu["icon"]),
                            title=ft.Text(menu["label"]),
                            on_click=lambda e, k=menu["key"]: set_content_area(k, None),
                        )
                        for menu in MENU_STRUCTURE
                    ]
                ],
                spacing=0,
                expand=True,
            ),
            width=nav_width,
            bgcolor="#B0B0B0",
            alignment=ft.alignment.top_center,
            visible=nav_rail_visible,
            padding=0,
            margin=0,
        )

        # Submenú dinámico (solo si el menú tiene submenús)
        def get_submenu():
            menu = next((m for m in MENU_STRUCTURE if m["key"] == current_area), None)
            if menu and menu["submenus"]:
                return ft.Container(
                    content=ft.Column([
                        ft.Text("Submenú", size=12, weight="bold"),
                        *[
                            ft.ListTile(
                                title=ft.Text(sub["label"], bgcolor="#f7f7a1" if current_subkey == sub["key"] else None),
                                on_click=lambda e, subk=sub["key"]: set_content_area(current_area, subk),
                            )
                            for sub in menu["submenus"]
                        ]
                    ], spacing=0),
                    width=180,
                    bgcolor="#f3f3f3",
                    padding=10,
                )
            return ft.Container(width=0)

        # Estado para el directorio seleccionado y archivos
        selected_dir = None
        files_list = []
        selected_file = None

        # --- Buscador de archivos dentro del directorio seleccionado ---
        file_search_query = ""
        file_search_field = ft.TextField(
            visible=True,  # Ahora siempre visible en la primera fila
            width=250,
            height=32,
            hint_text="Buscar archivo...",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=8),
            text_size=12,
            autofocus=False,
            on_change=lambda e: on_file_search_change(e.control.value),
        )
        file_suggestions_dropdown = ft.Column(visible=False, spacing=0)

        def on_file_search_change(query):
            nonlocal file_search_query
            file_search_query = query
            update_file_suggestions(query)
            update_files_list()  # Resalta en tiempo real

        def update_file_suggestions(query):
            if not selected_dir or not files_list:
                file_suggestions_dropdown.visible = False
                file_suggestions_dropdown.update()
                return
            filtered = [f for f in files_list if query.lower() in f.lower()]
            file_suggestions_dropdown.controls.clear()
            for fname in filtered:
                file_suggestions_dropdown.controls.append(
                    ft.ListTile(
                        title=ft.Text(fname, size=12),
                        on_click=lambda e, name=fname: (show_preview(name), collapse_file_search()),
                    )
                )
            file_suggestions_dropdown.visible = bool(filtered)
            file_suggestions_dropdown.update()

        def expand_file_search(e):
            file_search_field.visible = True
            file_search_field.width = 200
            file_search_field.focus()
            file_suggestions_dropdown.visible = False
            file_search_field.update()
            file_suggestions_dropdown.update()

        def collapse_file_search():
            file_search_field.visible = False
            file_search_field.width = 0
            file_suggestions_dropdown.visible = False
            file_search_field.value = ""
            file_search_field.update()
            file_suggestions_dropdown.update()

        # --- Botón y label de directorio ---
        dir_label = ft.Text("", size=8, selectable=True, expand=True)
        open_dir_button = ft.ElevatedButton(
            "Open directory",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda e: file_picker.get_directory_path(),
        )

        # FilePicker debe ser añadido a la página
        file_picker = ft.FilePicker(
            on_result=lambda e: on_result(e)
        )
        page.overlay.append(file_picker)

        def on_result(e: ft.FilePickerResultEvent):
            nonlocal selected_dir
            if e.path and os.path.isdir(e.path):
                selected_dir = e.path
                dir_label.value = selected_dir
                dir_label.update()
                update_files_list()
                # Mostrar buscador de archivos solo si hay un directorio válido
                file_search_field.visible = True
                file_search_field.width = 200
                file_search_field.update()
            else:
                selected_dir = None
                dir_label.value = ""
                dir_label.update()
                files_column.controls.clear()
                files_column.update()
                preview_label.value = "Selecciona un archivo para ver el preview."
                preview_label.update()
                file_search_field.visible = False
                file_search_field.width = 0
                file_search_field.update()

        def pick_directory():
            def on_result(e: ft.FilePickerResultEvent):
                nonlocal selected_dir
                if e.path and os.path.isdir(e.path):
                    selected_dir = e.path
                    dir_label.value = selected_dir
                    dir_label.update()
                    update_files_list()
                    file_search_field.visible = True
                    file_search_field.width = 200
                    file_search_field.update()
                else:
                    selected_dir = None
                    dir_label.value = ""
                    dir_label.update()
                    files_column.controls.clear()
                    files_column.update()
                    preview_label.value = "Selecciona un archivo para ver el preview."
                    preview_label.update()
                    file_search_field.visible = False
                    file_search_field.width = 0
                    file_search_field.update()
            page.dialog = ft.FilePicker(on_result=on_result)
            page.dialog.get_directory_path()

        def highlight_text(text, query):
            if not query:
                return [ft.Text(text, size=12)]
            parts = []
            idx = 0
            q = query.lower()
            t = text.lower()
            while True:
                found = t.find(q, idx)
                if found == -1:
                    parts.append(ft.Text(text[idx:], size=12))
                    break
                if found > idx:
                    parts.append(ft.Text(text[idx:found], size=12))
                parts.append(ft.Text(text[found:found+len(q)], size=12, bgcolor="#06bd98"))
                idx = found + len(q)
            return parts

        def update_files_list():
            nonlocal files_list
            if not selected_dir:
                files_list = []
                files_column.controls.clear()
                files_column.update()
                return
            try:
                files = os.listdir(selected_dir)
                files_list.clear()
                for f in files:
                    files_list.append(f)
                files_column.controls.clear()
                for f in files_list:
                    # Resalta borde si hay match
                    is_match = file_search_query and file_search_query.lower() in f.lower()
                    files_column.controls.append(
                        ft.Container(
                            ft.ListTile(
                                title=ft.Row(highlight_text(f, file_search_query), spacing=0),
                                on_click=lambda e, fname=f: show_preview(fname),
                            ),
                            border=ft.border.all(2, "#06bd98") if is_match else None,
                            border_radius=6,
                            padding=2,
                            margin=2,
                        )
                    )
                files_column.update()
            except Exception as ex:
                files_column.controls.clear()
                files_column.controls.append(ft.Text(f"Error: {ex}", color="red", size=12))
                files_column.update()

        preview_label = ft.Text("Selecciona un archivo para ver el preview.", size=12, selectable=True, expand=True)
        pdf_viewer = ft.Container(visible=False, expand=True)

        # Para integrar la previsualización de PDFs como imagen sin dañar tu código actual:
        # 1. Instala pdf2image: pip install pdf2image
        # 2. Descarga Poppler y agrega su carpeta bin al PATH (en Windows).
        # 3. Agrega la función show_pdf_as_image y modifíca show_preview para usarla.

        import tempfile
        try:
            from pdf2image import convert_from_path
        except ImportError:
            convert_from_path = None

        # Ajusta aquí la ruta a la carpeta bin de Poppler descargada
        POPPLER_BIN_PATH = os.path.join(os.path.dirname(__file__), "poppler-24.08.0", "Library", "bin")

        def show_pdf_as_image(pdf_path):
            if convert_from_path is None:
                pdf_viewer.content = ft.Text("pdf2image no está instalado.", color="red")
                pdf_viewer.visible = True
                pdf_viewer.update()
                return
            try:
                # Elimina la imagen previa para evitar caché
                img_path = os.path.join(tempfile.gettempdir(), f"preview_{os.path.basename(pdf_path)}.png")
                images = convert_from_path(
                    pdf_path,
                    first_page=1,
                    last_page=1,
                    poppler_path=POPPLER_BIN_PATH
                )
                if images:
                    images[0].save(img_path, "PNG")
                    pdf_viewer.content = ft.Image(src=img_path, expand=True, fit=ft.ImageFit.CONTAIN)
                    pdf_viewer.visible = True
                    pdf_viewer.update()
                else:
                    pdf_viewer.content = ft.Text("No se pudo renderizar el PDF.", color="red")
                    pdf_viewer.visible = True
                    pdf_viewer.update()
            except Exception as ex:
                pdf_viewer.content = ft.Text(f"Error al mostrar PDF: {ex}", color="red")
                pdf_viewer.visible = True
                pdf_viewer.update()

        def show_preview(fname):
            nonlocal selected_file
            selected_file = fname
            if not selected_dir:
                preview_label.value = "No hay directorio seleccionado."
                preview_label.visible = True
                pdf_viewer.visible = False
                preview_label.update()
                pdf_viewer.update()
                return
            full_path = os.path.join(selected_dir, fname)
            if os.path.isdir(full_path):
                preview_label.value = f"{fname} es un directorio."
                preview_label.visible = True
                pdf_viewer.visible = False
            elif fname.lower().endswith(".pdf"):
                preview_label.visible = False
                pdf_viewer.visible = True
                show_pdf_as_image(full_path)
            else:
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2048)
                        preview_label.value = content if content else "(Archivo vacío)"
                        preview_label.visible = True
                        pdf_viewer.visible = False
                except Exception as ex:
                    preview_label.value = f"No se puede mostrar preview: {ex}"
                    preview_label.visible = True
                    pdf_viewer.visible = False
            preview_label.update()
            pdf_viewer.update()

        files_column = ft.Column(expand=True, scroll="auto")

        # --- Nueva fila 1: campo de búsqueda ---
        search_row = ft.Container(
            content=ft.Stack(
                [
                    file_search_field,
                    ft.Container(
                        file_suggestions_dropdown,
                        top=36,
                        left=0,
                        width=250,
                        bgcolor="#fff",
                        border_radius=8,
                        border=ft.border.all(1, "#ccc"),
                        shadow=ft.BoxShadow(blur_radius=4, color="#88888822"),
                        visible=file_suggestions_dropdown.visible,
                    ),
                ],
                width=250,
                height=40,
            ),
            padding=ft.padding.only(left=16, top=8, bottom=8),
        )

        # --- Nueva fila 2: botón, label y contenido de archivos ---
        dir_row = ft.Row(
            controls=[
                open_dir_button,
                dir_label,
            ],
            alignment="start",
            vertical_alignment="center",
            spacing=10,
        )

        files_list_container = ft.Container(
            files_column,
            width=300,
            bgcolor="#f6f6f6",
            expand=False,
            padding=5,
        )

        # --- Fila inferior: archivos y preview ---
        files_and_preview_row = ft.Row(
            controls=[
                files_list_container,
                ft.VerticalDivider(width=2, color="#cccccc"),
                ft.Container(
                    ft.Stack([preview_label, pdf_viewer]),
                    expand=True,
                    bgcolor="#f9f9f9",
                    padding=0,
                    alignment=ft.alignment.center,
                ),
            ],
            expand=True,
            spacing=0,
        )

        # --- Content area ---
        content_area = ft.Container(
            content=ft.Column(
                [
                    search_row,      # Primera fila: campo de búsqueda
                    dir_row,         # Segunda fila: botón y label de directorio
                    files_and_preview_row,  # Tercera fila: archivos y preview
                ],
                expand=True,
                spacing=0,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#578881", "#B7EF50"],
            ),
            alignment=ft.alignment.top_left,
            expand=True,
            padding=0,
            margin=0,
        )

        # Layout principal
        layout = ft.Column(
            controls=[
                custom_bar,
                ft.Row(
                    controls=[
                        nav_rail,
                        get_submenu(),
                        content_area,
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )

        page.add(layout)
        update_content_area()

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
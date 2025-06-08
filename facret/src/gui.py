import flet as ft
import os
# from src.logic.logic import clean_xml_files, process_all_xml_files

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

                ft.Text("AppBar", color="black", weight="bold", size=20, tooltip="Title app"),
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
                    ft.Text("Tools", color="black", size=22, text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.OPEN_IN_BROWSER),
                        title=ft.Text(menu_labels[0]),
                        on_click=lambda e: print("Ir a " + menu_labels[0]),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.OPEN_IN_BROWSER),
                        title=ft.Text(menu_labels[1]),
                        on_click=lambda e: print("Ir a " + menu_labels[1]),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                        title=ft.Text(menu_labels[2]),
                        on_click=lambda e: print("Ir a " + menu_labels[2]),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.RECEIPT),
                        title=ft.Text(menu_labels[3]),
                        on_click=lambda e: print("Ir a " + menu_labels[3]),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.RECEIPT_LONG),
                        title=ft.Text(menu_labels[4]),
                        on_click=lambda e: print("Ir a " + menu_labels[4]),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ATTACH_MONEY),
                        title=ft.Text(menu_labels[5]),
                        on_click=lambda e: print("Ir a " + menu_labels[5]),
                    ),
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

        def on_drag(e: ft.DragUpdateEvent):
            nonlocal nav_rail
            new_width = nav_rail.width + e.delta_x
            if new_width < 60:
                new_width = 60
            if new_width > 300:
                new_width = 300
            nav_rail.width = new_width
            nav_rail.update()

        gesture = ft.GestureDetector(
            content=ft.VerticalDivider(width=2, color="#888888"),  # Línea más delgada
            drag_interval=10,
            on_pan_update=on_drag,
            on_hover=lambda e: (setattr(e.control, "mouse_cursor", ft.MouseCursor.RESIZE_LEFT_RIGHT), e.control.update()),
        )

        # Estado para el directorio seleccionado y archivos
        selected_dir = None
        files_list = []
        selected_file = None

        # --- Buscador de archivos dentro del directorio seleccionado ---
        file_search_field = ft.TextField(
            visible=False,
            width=0,
            height=32,
            hint_text="Buscar archivo...",
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=8),
            text_size=12,
            autofocus=False,
            on_change=lambda e: update_file_suggestions(e.control.value),
        )
        file_suggestions_dropdown = ft.Column(visible=False, spacing=0)

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
        dir_label = ft.Text("", size=14, selectable=True, expand=True)
        open_dir_button = ft.ElevatedButton(
            "Open directory",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda e: pick_directory(),
        )

        def pick_directory():
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
            page.dialog = ft.FilePicker(on_result=on_result)
            page.dialog.get_directory_path()

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
                    files_column.controls.append(
                        ft.ListTile(
                            title=ft.Text(f, size=12),
                            on_click=lambda e, fname=f: show_preview(fname),
                        )
                    )
                files_column.update()
            except Exception as ex:
                files_column.controls.clear()
                files_column.controls.append(ft.Text(f"Error: {ex}", color="red", size=12))
                files_column.update()

        preview_label = ft.Text("Selecciona un archivo para ver el preview.", size=12, selectable=True, expand=True)

        def show_preview(fname):
            nonlocal selected_file
            selected_file = fname
            if not selected_dir:
                preview_label.value = "No hay directorio seleccionado."
                preview_label.update()
                return
            full_path = os.path.join(selected_dir, fname)
            if os.path.isdir(full_path):
                preview_label.value = f"{fname} es un directorio."
            else:
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2048)
                        preview_label.value = content if content else "(Archivo vacío)"
                except Exception as ex:
                    preview_label.value = f"No se puede mostrar preview: {ex}"
            preview_label.update()

        files_column = ft.Column(expand=True, scroll="auto")

        # --- Fila superior: botón, label y buscador de archivos ---
        dir_row = ft.Row(
            controls=[
                open_dir_button,
                dir_label,
                ft.Stack(
                    [
                        file_search_field,
                        ft.Container(
                            file_suggestions_dropdown,
                            top=36,
                            left=0,
                            width=200,
                            bgcolor="#fff",
                            border_radius=8,
                            border=ft.border.all(1, "#ccc"),
                            shadow=ft.BoxShadow(blur_radius=4, color="#88888822"),
                            visible=file_suggestions_dropdown.visible,
                        ),
                    ],
                    width=200,
                    height=40,
                ),
                ft.IconButton(
                    ft.Icons.SEARCH,
                    icon_color="black",
                    tooltip="Buscar archivo",
                    style=ft.ButtonStyle(padding=0, shape=None),
                    on_click=expand_file_search,
                ),
            ],
            alignment="start",
            vertical_alignment="center",
            spacing=10,
        )

        # --- Fila inferior: archivos y preview ---
        files_and_preview_row = ft.Row(
            controls=[
                ft.Container(files_column, width=300, bgcolor="#f6f6f6", expand=False, padding=5),
                ft.VerticalDivider(width=2, color="#cccccc"),
                ft.Container(preview_label, expand=True, bgcolor="#f9f9f9", padding=5),
            ],
            expand=True,
            spacing=0,
        )

        # --- Content area ---
        content_area = ft.Container(
            content=ft.Column(
                [
                    dir_row,
                    files_and_preview_row,
                ],
                expand=True,
                spacing=10,
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
                        gesture,
                        content_area,
                    ],
                    expand=True,
                    spacing=0,  # Sin espacio entre columnas
                ),
            ],
            expand=True,
            spacing=0,
        )

        page.add(layout)
        # No update_files_list() aquí, solo se actualiza tras seleccionar un directorio

        pass

    ft.app(target=main)
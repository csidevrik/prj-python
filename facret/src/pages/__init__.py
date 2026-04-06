# =============================
# pages/__init__.py
# =============================
"""
Carpeta pages/ — pantallas completas de FACRET.

Patrón obligatorio para cada página nueva:
  1. Crear archivo:  pages/{feature}_page.py
  2. Crear clase:    class {Feature}Page:
                         def __init__(self, page: ft.Page): ...
                         def build(self) -> ft.Control: ...
  3. Registrar en:   config/menu_config.py
                         MenuItem(key="...", page_class="pages.{feature}_page.{Feature}Page")

El router (gui.py → _load_page) importa la clase dinámicamente,
por lo que agregar una nueva página NO requiere tocar gui.py.
"""

```
facret/
├── README.md                # Documentación del proyecto
├── poetry.lock              # Dependencias resueltas
├── pyproject.toml           # Configuración de Poetry
└── src/
    ├── main.py              # Punto de entrada principal de la aplicación
    ├── run_desktop.py       # Alternativa de ejecución en escritorio
    ├── assets/
    │   ├── favicon.ico      # Icono principal de la aplicación
    │   └── favicon.png      # Versión alternativa en PNG
    ├── components/
    │   └── nav_rail.py      # Componente de menú lateral (Navigation Rail)
    ├── config/
    │   ├── theme.py         # Definición de colores, estilos y gradientes
    │   └── menu_structure.py# Estructura del menú y submenús
    └── logic/               # (Opcional) Lógica de negocio
```

# ⚙️ Instalación

## Clonar el repositorio

```bash
git clone https://github.com/usuario/facret.git
cd facret
```

## Instalar dependencias con Poetry

Asegúrate de tener instalado Poetry.

```bash
poetry install
```

Si solo quieres instalar dependencias sin empaquetar el proyecto:

```bash
poetry install --no-root
```

## Activar el entorno virtual

```bash
poetry shell
```



## ▶️ Ejecución

Para iniciar la aplicación:




## 🧩 Componentes principales

### 1. **`main.py`**

Archivo principal que arranca la aplicación.

Funciones clave:

* Configura la ventana (icono, tamaño, barra estándar del sistema operativo).
* Implementa la **barra superior personalizada** con botones de minimizar, maximizar y cerrar (usando `ctypes` en Windows).
* Contiene el  **layout principal** :
  * Menú lateral (`NavRailComponent`).
  * Barra superior con gradiente (`AppGradients`).
  * Contenedor de contenido central.

---

### 2. **`nav_rail.py`**

Componente de **menú lateral** inspirado en  *Navigation Rail* .

* Construye dinámicamente la lista de menús y submenús a partir de `menu_structure.py`.
* Permite seleccionar un menú y expandir submenús.
* Incluye métodos para:
  * `.toggle()` → mostrar/ocultar el panel lateral.
  * `.update()` → refrescar el contenido.
  * `.on_menu_click()` y `.on_submenu_click()` → manejo de eventos de selección.

Se expone como `nav_rail.view` para integrarlo en el layout de la aplicación.

---

### 3. **`theme.py`**

Define la  **paleta de colores** , estilos tipográficos y gradientes de la aplicación.

* `AppColors` → colores base y de fondo.
* `AppStyles` → estilos reutilizables (ejemplo: tipografías, tamaños de texto).
* `AppGradients` → colección de gradientes predefinidos con nombres (`by_name("Summer")`).

Esto permite mantener la coherencia visual y cambiar la apariencia global desde un solo lugar.

---

### 4. **Favicon (`assets/favicon.ico` y `favicon.png`)**

Iconos que representan la aplicación en la ventana del sistema operativo.

* `favicon.ico` → usado en Windows como icono de la ventana (`page.window.icon`).
* `favicon.png` → versión alternativa para compatibilidad.

---

## 🎨 Estilos y personalización

* Todos los colores se gestionan desde `theme.py`.
* Los menús y submenús se definen en `config/menu_structure.py`.
* Puedes reemplazar los iconos en `assets/` por los de tu aplicación.

---

## 🚀 Próximos pasos

* Agregar nuevos **componentes personalizados** dentro de `src/components/`.
* Ampliar la lógica de negocio en `src/logic/`.
* Internacionalización y soporte multi-idioma.
* Empaquetar como aplicación instalable (ejemplo: con `flet pack`).

---

## 🖼️ Captura de ejemplo

*(inserta aquí una captura de la app ejecutándose con el menú lateral abierto y la barra superior personalizada)*

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia que decidas (MIT, GPL, etc.).

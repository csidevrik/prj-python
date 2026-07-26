# 🔄 Flujo de Estadísticas — Arquitectura Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                         APP FACRET                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌──────────────────────┐
│   Download FACS     │         │   Gestión FACS       │
│                     │         │                      │
│ [Carpeta...]────┐   │         │ [Carpeta...]─────┐   │
│ [Guardar]       │   │         │ [Explorar]       │   │
│                 │   │         │                  │   │
│                 ▼   │         │                  ▼   │
│          ┌──────────┐│         │          ┌──────────┐│
│          │Save      ││         │          │on_change ││
│          │Config   ││         │          │on_pick   ││
│          └──────────┘│         │          └──────────┘│
│                 │   │         │                  │   │
└─────────────────┼───┘         └──────────────────┼───┘
                  │                                 │
                  │ set_value("carpeta_trabajo", │ set_value("carpeta_trabajo",
                  │           value)              │           value)
                  │                                 │
                  │  ┌────────────────────────────┐  │
                  └─►│  facs_config.json          │◄─┘
                     │  {                         │
                     │    "carpeta_guardar": "D\  │
                     │    "carpeta_trabajo": "D\  │ ← SINCRONIZADAS
                     │    ...                      │
                     │  }                          │
                     └────────────────────────────┘
                           ▲ load_config()
                           │
                  ┌────────┴───────────┐
                  │                    │
                  │                    ▼
                ┌──────────────────────────────┐
                │      gui.py                  │
                │                              │
                │  config = load_config()      │
                │  carpeta_trabajo =           │
                │      config.get("...")       │
                │  sidebar = Sidebar(          │
                │      carpeta_trabajo=...     │
                │  )                           │
                └────────────┬─────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  DriveSidebar      │
                    │  _build_storage    │
                    │  _section()        │
                    └────────┬───────────┘
                             │
                get_folder_stats(carpeta_trabajo)
                             │
                             ▼
                    ┌────────────────────────────┐
                    │ logic/folder_stats.py      │
                    │                            │
                    │ • Recorre carpeta          │
                    │ • Cuenta archivos          │
                    │ • Cuenta subcarpetas       │
                    │ • Suma tamaños en bytes    │
                    │ • Formatea (MB/GB)         │
                    │ • Retorna FolderStats      │
                    └────────┬───────────────────┘
                             │
                             ▼
                    ┌────────────────────────────┐
                    │ FolderStats(              │
                    │   num_archivos: 42,       │
                    │   num_carpetas: 3,        │
                    │   tamanio_mb: 234.56,     │
                    │   tamanio_str: "234.56 MB"│
                    │ )                         │
                    └────────┬───────────────────┘
                             │
                             ▼
                    ┌────────────────────────────┐
                    │ Sidebar muestra:           │
                    │                            │
                    │ Almacenamiento             │
                    │ 💾 234.56 MB               │
                    │ 📄 42 archivos             │
                    │ 📁 3 carpetas              │
                    │                            │
                    └────────────────────────────┘
```

---

## 📊 Tabla de Responsabilidades

| Componente | Responsabilidad |
|-----------|-----------------|
| **Download FACS** | Permite al user configurar carpeta de descarga |
| **Gestión FACS** | Usa la carpeta configurada |
| **config_manager.py** | Lee/escribe en `facs_config.json` |
| **facs_config.json** | Persiste `carpeta_trabajo` en disco |
| **gui.py** | Lee config al iniciar, pasa al sidebar |
| **sidebar.py** | Recibe carpeta, llama a `get_folder_stats()` |
| **folder_stats.py** | Calcula estadísticas reales |
| **Sidebar UI** | Muestra resultados en tiempo real |

---

## 🔄 Flujo de Sincronización

### Caso 1: Usuario configura carpeta en Download FACS

```
1. User escribe: C:\Temp\MisFacturas
2. User hace clic: "Guardar Configuración"
3. facs_downloader_page._save_config() ejecuta:
   └─ save_config({
        "carpeta_guardar": "C:\Temp\MisFacturas",
        "carpeta_trabajo": "C:\Temp\MisFacturas"  ← SYNC
      })
4. JSON se actualiza en disco
5. User navega a "Gestión FACS"
6. facs_manager_page.__init__() carga:
   └─ carpeta_trabajo = load_config().get("carpeta_trabajo", "")
7. Sidebar se reconstruye con nueva carpeta
8. get_folder_stats("C:\Temp\MisFacturas") calcula estadísticas
9. UI muestra: "💾 X.XX MB | 📄 XX archivos | 📁 X carpetas"
```

### Caso 2: Usuario cambia carpeta en Gestión FACS

```
1. User hace clic: "Explorar" (FilePicker)
2. User selecciona: D:\Otros\Facturas
3. facs_manager_page._on_picker_result() ejecuta:
   └─ set_value("carpeta_trabajo", "D:\Otros\Facturas")
4. JSON se actualiza en disco
5. Sidebar se reconstruye (si está visible)
6. Estadísticas se muestran de la nueva carpeta
7. Cuando User vuelve a Download FACS
8. Campo "carpeta de descarga local" muestra la nueva ruta
   (porque load_config() lee la misma clave)
```

---

## 🎯 Sincronización Bidireccional

```
Download FACS
    ↓ (configura)
carpeta_guardar ──┐
                  ├──→ facs_config.json ──→ carpeta_trabajo
                  │
carpeta_trabajo ◄─┘
    ↑ (usa)
Gestión FACS
```

**Clave:** Ambas páginas leen/escriben la misma clave `carpeta_trabajo` en config.

---

## 🚨 Manejo de Errores

### Carpeta no existe
```python
get_folder_stats("D:\NoExiste")
→ Retorna None
→ Sidebar muestra: "Sin datos"
```

### Carpeta sin permisos
```python
get_folder_stats("C:\System32")
→ Intenta calcular parcialmente
→ Devuelve stats parciales (archivos accesibles)
```

### Sin carpeta configurada
```python
get_folder_stats("")
→ Retorna None
→ Sidebar muestra: "Sin datos"
```

---

## 📈 Rendimiento

- **Carpeta pequeña (<100 archivos):** ~50-100ms
- **Carpeta mediana (<10k archivos):** ~500-1000ms
- **Carpeta grande (>10k archivos):** ~2-5 segundos

💡 **Tip:** Para carpetas grandes, considerar caché o calcular en background con threading.

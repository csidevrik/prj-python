# PDF Processor — Comprobantes de Retención EMOV

Proyecto Python para extraer datos estructurados de comprobantes de retención emitidos por **EMOV** (Empresa Municipal de Movilidad, Cuenca, Ecuador).

PDF de ejemplo: `001-200-000022198.pdf`

---

## Objetivo

Extraer automáticamente los siguientes campos del PDF como JSON:

| Campo                      | Descripción                              |
| -------------------------- | ----------------------------------------- |
| `ruc_emisor`             | RUC de la empresa que emite la retención |
| `numero_retencion`       | Número del comprobante de retención     |
| `numero_autorizacion`    | Número de autorización SRI              |
| `fecha_autorizacion`     | Fecha de autorización                    |
| `razon_social_proveedor` | Nombre del proveedor retenido             |
| `ruc_proveedor`          | RUC del proveedor                         |
| `fecha_emision_factura`  | Fecha de la factura relacionada           |
| `comprobante_tipo`       | Tipo de comprobante (factura, etc.)       |
| `comprobante_numero`     | Número de la factura relacionada         |
| `base_imponible`         | Base imponible                            |
| `impuesto`               | Tipo de impuesto                          |
| `porcentaje_retencion`   | Porcentaje aplicado                       |
| `valor_retenido`         | Valor retenido                            |

---

## Lo explorado hasta ahora

### Herramientas probadas

- **docling** + **pymupdf**: extracción de texto por coordenadas `(x0, y0, x1, y1)` en puntos tipográficos.
- **pymupdf** (`page.get_text("blocks")`): dump de todos los bloques de texto con sus bounding boxes.
  - La página A4 mide 595×842 pts según `page.rect`.

### Problema encontrado con parsing espacial

Se intentó un parser semántico basado en proximidad espacial (etiqueta a la izquierda, valor a la derecha en la misma banda Y), pero algunos bloques mezclan etiqueta y valor en el mismo registro en orden invertido. Ejemplo:

```
'CARLOS ARIZAGA TORAL S/N Y TARQUINO CORDERO\nDirección\nMatriz:'
```

Esto hace que el enfoque puramente espacial sea frágil.

### Conclusión: usar Vision LLM

El enfoque correcto es:

1. Renderizar la página como imagen PNG con `pymupdf` (`page.get_pixmap()`).
2. Enviarla a la **API de Anthropic (Claude)** con visión.
3. Pedirle que devuelva un JSON estructurado con los campos del comprobante.

---

## Archivos

| Archivo                 | Descripción                                                               |
| ----------------------- | -------------------------------------------------------------------------- |
| `dumper.py`           | Dumpea todos los bloques de texto del PDF con sus bounding boxes (pymupdf) |
| `pdf-processor-01.py` | Prueba inicial con docling para extraer texto por regiones                 |
| `test.py`             | Archivo de pruebas                                                         |

---

## Siguiente paso

Implementar `parser.py` que:

1. Abra el PDF con pymupdf.
2. Renderice la página 0 como imagen PNG.
3. Llame a la API de Anthropic (modelo con visión, ej. `claude-opus-4-6`) enviando la imagen.
4. Devuelva los campos como JSON estructurado.

### Dependencias necesarias

```bash
pip install pymupdf anthropic
```

### API Key

Configurar la variable de entorno:

```bash
export ANTHROPIC_API_KEY="sk-..."
```

---






## Estado actual (2026-04-06)

- [X] pymupdf instalado
- [X] Bloques de texto dumpeados y analizados
- [ ] API key de Anthropic configurada
- [ ] `parser.py` implementado con Vision LLM









## 📁 Estructura del proyecto con Poetry

**text**

```
prj-python/
├── pyproject.toml          # Configuración principal de Poetry
├── poetry.lock             # (se genera automáticamente)
├── .env                    # Variables de entorno (API key, etc.)
├── pdfs/                   # Tus PDFs de entrada
├── outputs/                # JSONs extraídos
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── vision_extractor.py
│   └── main.py
└── tests/
```

## 🔧 Paso 1: Inicializar Poetry en lugar de virtualenv

### 1.1 Instalar Poetry (si no lo tienes)

**bash**

```
# Windows (PowerShell como administrador)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# O con pip (menos recomendado)
pip install poetry
```

### 1.2 Crear el proyecto con Poetry

Dentro de `c:\Users\adminos\dev\github\prj-python` (carpeta ya existente):

**bash**

```
cd c:\Users\adminos\dev\github\prj-python
poetry init
```

Te hará preguntas interactivas. Puedes responder así:

* Package name: `prj-python` (o dejarlo por defecto)
* Version: `0.1.0`
* Description: `Extractor de comprobantes de retención EMOV con visión`
* Author: tu nombre
* License: (deja vacío)
* Python version: `^3.10` (o la que uses)

Luego te preguntará si quieres añadir dependencias. Por ahora responde **no** (las añadiremos manualmente después).

Esto generará un archivo `pyproject.toml`.

### 1.3 Agregar las dependencias necesarias

**bash**

```
poetry add pymupdf python-dotenv requests
# Si prefieres usar Anthropic en lugar de DeepSeek:
# poetry add anthropic
```

Si además quieres usar **Ollama** (modelo local sin API key), añade:

**bash**

```
poetry add requests  # ya la tienes
```

Para desarrollo (opcional, pero útil):

**bash**

```
poetry add --dev pytest black
```

### 1.4 Activar el entorno virtual de Poetry

Poetry crea automáticamente un entorno virtual aislado. Para activarlo y usarlo en tu terminal:

**bash**

```
poetry shell
```

A partir de ahí, todos los comandos `python` ejecutarán el entorno.

Si prefieres no activar el shell, puedes anteponer `poetry run` a cada comando, por ejemplo:

**bash**

```
poetry run python src/main.py
```

## 📝 Paso 2: Configurar el archivo `.env` (igual que antes)

Crea `.env` en la raíz con tu API key de DeepSeek (aunque tenga saldo cero, la estructura sigue igual):

**text**

```
DEEPSEEK_API_KEY=sk-xxxxx
```

*(Recuerda que luego puedes cambiar a Ollama u otro)*

## 🧩 Paso 3: Adaptar los módulos de código (sin cambios, salvo importaciones)

El código Python que ya habíamos escrito (`src/config.py`, `src/vision_extractor.py`, `src/main.py`) funciona igual con Poetry. Solo asegúrate de que los imports sean relativos correctos (porque `src` es un paquete). Por ejemplo, en `main.py`:

**python**

```
from src.vision_extractor import pdf_page_to_base64, extract_retencion_deepseek
```

## 🚀 Paso 4: Ejecutar el script con Poetry

Desde la raíz del proyecto (con o sin `poetry shell` activo):

**bash**

```
poetry run python src/main.py
```

Si activaste el shell con `poetry shell`, simplemente:

**bash**

```
python src/main.py
```

## 📦 Paso extra: Exportar dependencias (si las necesitas para otro lado)

Aunque Poetry maneja todo, a veces necesitas un `requirements.txt` por compatibilidad:

**bash**

```
poetry export -f requirements.txt --output requirements.txt
```

## 🔄 Comparativa: `venv` vs `Poetry`

| Acción               | Con venv                          | Con Poetry                                        |
| --------------------- | --------------------------------- | ------------------------------------------------- |
| Crear entorno         | `python -m venv venv`           | `poetry init`+`poetry shell`                  |
| Activar entorno       | `venv\Scripts\activate`         | `poetry shell`                                  |
| Instalar dependencias | `pip install pymupdf`           | `poetry add pymupdf`                            |
| Guardar dependencias  | `pip freeze > requirements.txt` | Se guardan automáticamente en `pyproject.toml` |
| Ejecutar script       | `python src/main.py`            | `poetry run python src/main.py`                 |

## 🧪 Prueba de concepto con Poetry y tu API key (aunque tenga saldo cero)

Crea un script rápido `test_poetry.py` en la raíz:

**python**

```
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.config import get_api_key
from src.vision_extractor import pdf_page_to_base64, extract_retencion_deepseek

try:
    key = get_api_key("deepseek")
    print(f"API key cargada: {key[:10]}...")
except Exception as e:
    print(f"Error con API key: {e}")

# Procesar un PDF real (si existe)
pdf_path = "pdfs/001-200-000022198.pdf"
if Path(pdf_path).exists():
    b64 = pdf_page_to_base64(pdf_path)
    print("Imagen convertida a base64, longitud:", len(b64))
    # datos = extract_retencion_deepseek(b64)  # descomentar cuando tengas saldo
else:
    print("PDF no encontrado")
```

Ejecútalo con:

**bash**

```
poetry run python test_poetry.py
```

import os
import base64
import json
import pymupdf  # PyMuPDF
from anthropic import Anthropic
from pathlib import Path

# Carga tu API key desde variable de entorno (más seguro)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("Falta la variable de entorno ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def pdf_page_to_image(pdf_path: str, page_num: int = 0, dpi: int = 200) -> str:
    """
    Convierte una página del PDF a imagen PNG en memoria y devuelve base64.
    """
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    # Aumentar resolución (zoom) para mejor OCR visual
    zoom = dpi / 72  # 72 es DPI estándar de PDF
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_data = pix.tobytes("png")
    doc.close()
    return base64.b64encode(img_data).decode("utf-8")

def extract_retencion_from_image(base64_image: str) -> dict:
    """
    Envía la imagen a Claude con instrucciones para extraer campos específicos.
    """
    prompt = """
Eres un experto en extracción de datos de comprobantes de retención de Ecuador (EMOV, Cuenca).
De la siguiente imagen de un comprobante de retención, extrae los siguientes campos exactamente como aparecen:

- ruc_emisor: RUC de la empresa que emite la retención (EMOV).
- numero_retencion: Número del comprobante de retención (ej: 001-200-000022198).
- numero_autorizacion: Número de autorización SRI.
- fecha_autorizacion: Fecha de autorización (formato YYYY-MM-DD o como aparezca).
- razon_social_proveedor: Nombre completo del proveedor al que se retiene.
- ruc_proveedor: RUC del proveedor.
- fecha_emision_factura: Fecha de la factura original (si aparece).
- comprobante_tipo: Tipo de comprobante de venta (factura, nota de crédito, etc.).
- comprobante_numero: Número del comprobante de venta.
- base_imponible: Valor base imponible (solo números, sin signo $).
- impuesto: Tipo de impuesto (ej: IVA, IR).
- porcentaje_retencion: Porcentaje aplicado (ej: 30%, 10%).
- valor_retenido: Valor retenido (número).

Devuelve SOLO un objeto JSON válido con esos campos. Si algún campo no existe, pon null.
No agregues texto adicional, solo el JSON.
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # o "claude-3-opus-20240229"
        max_tokens=1024,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # La respuesta es texto plano, puede incluir marcadores de código
    respuesta_texto = response.content[0].text
    # Limpiar: quitar ```json ... ``` si existe
    if "```json" in respuesta_texto:
        respuesta_texto = respuesta_texto.split("```json")[1].split("```")[0]
    elif "```" in respuesta_texto:
        respuesta_texto = respuesta_texto.split("```")[1].split("```")[0]
    return json.loads(respuesta_texto.strip())

def procesar_retencion(pdf_path: str) -> dict:
    """
    Procesa un PDF de retención (se asume que el comprobante está en la primera página).
    """
    print(f"Procesando {pdf_path}...")
    base64_img = pdf_page_to_image(pdf_path, page_num=0, dpi=200)
    datos = extract_retencion_from_image(base64_img)
    return datos

if __name__ == "__main__":
    # Prueba con tu PDF
    pdf_ejemplo = r"c:\Users\adminos\dev\github\prj-python\001-200-000022198.pdf"
    if Path(pdf_ejemplo).exists():
        resultado = procesar_retencion(pdf_ejemplo)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(f"No se encuentra el PDF: {pdf_ejemplo}")
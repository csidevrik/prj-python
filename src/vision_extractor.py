import json
import pymupdf
from src.config import get_deepseek_api_key
from openai import OpenAI

client = OpenAI(api_key=get_deepseek_api_key(), base_url="https://api.deepseek.com")

def pdf_page_to_text(pdf_path: str, page_num: int = 0) -> str:
    """Extrae el texto de una página del PDF."""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    text = page.get_text()
    doc.close()
    return text

def extract_retencion_from_text(text: str) -> dict:
    """Envía el texto a DeepSeek API y extrae los campos como JSON."""
    prompt = f"""
Eres un asistente experto en documentos fiscales de Ecuador (comprobantes de retención de EMOV).
Extrae los siguientes campos del texto del comprobante.
Devuelve **solo** un objeto JSON válido, sin texto adicional, sin comillas triples.

Campos solicitados:
- ruc_emisor
- numero_retencion
- numero_autorizacion
- fecha_autorizacion
- razon_social_proveedor
- ruc_proveedor
- fecha_emision_factura
- comprobante_tipo
- comprobante_numero
- base_imponible (número, sin símbolos)
- impuesto (ej: IVA, IR)
- porcentaje_retencion (ej: 30%, 10% → conserva el símbolo % si aparece)
- valor_retenido (número)

Si un campo no existe, asigna null.
Ejemplo de formato de salida:
{{
  "ruc_emisor": "1792069306001",
  "numero_retencion": "001-200-000022198",
  ...
}}

Texto del comprobante:
{text}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en documentos fiscales de Ecuador."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"},
        stream=False
    )

    content = response.choices[0].message.content

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    return json.loads(content.strip())
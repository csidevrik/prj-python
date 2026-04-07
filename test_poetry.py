import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.config import get_api_key
from src.vision_extractor import pdf_page_to_base64, extract_retencion_deepseek

try:
    key = get_api_key("sk-704feab001a649bcb23f9ff03dd9783a")
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
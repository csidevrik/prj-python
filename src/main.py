import json
from pathlib import Path
from src.vision_extractor import pdf_page_to_text, extract_retencion_from_text

def procesar_pdf(pdf_path: Path) -> dict:
    print(f"📄 Procesando: {pdf_path.name}")
    text = pdf_page_to_text(str(pdf_path))
    datos = extract_retencion_from_text(text)
    return datos

def main():
    pdf_dir = Path("pdfs")
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("⚠️ No se encontraron archivos PDF en la carpeta 'pdfs/'")
        return

    for pdf_file in pdf_files:
        try:
            resultado = procesar_pdf(pdf_file)
            out_file = out_dir / f"{pdf_file.stem}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"✅ Guardado: {out_file}")
        except Exception as e:
            print(f"❌ Error en {pdf_file.name}: {e}")

if __name__ == "__main__":
    main()
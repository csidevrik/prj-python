import pymupdf

doc = pymupdf.open("001-200-000022198.pdf")
page = doc.load_page(0)

# Extrae todos los bloques de texto con sus bounding boxes
blocks = page.get_text("blocks")  # lista de (x0, y0, x1, y1, texto, ...)

for b in blocks:
    x0, y0, x1, y1, texto = b[0], b[1], b[2], b[3], b[4]
    print(f"[{x0:.0f},{y0:.0f} -> {x1:.0f},{y1:.0f}]  {texto.strip()!r}")

doc.close()

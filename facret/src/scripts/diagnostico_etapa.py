# =============================
# scripts/diagnostico_etapa.py
# =============================
"""
Diagnóstico de solo lectura del sitio de Pago Empresas de ETAPA.

Abre Chromium visible, espera a que inicies sesión a mano (usuario, clave y reCAPTCHA),
y luego guarda en data/informes/diagnostico/ la lista de órdenes y, si indicas un Id,
el detalle de esa orden. No pulsa ningún botón de acción.

Uso:
    poetry run python src/scripts/diagnostico_etapa.py
    poetry run python src/scripts/diagnostico_etapa.py --orden 7971
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from logic.etapa_playwright import (  # noqa: E402
    abrir_navegador,
    abrir_orden,
    capturar_pantalla,
    esperar_login,
    ir_a_ordenes,
    volcar_pagina,
)

CARPETA = SRC.parent / "data" / "informes" / "diagnostico"


def ejecutar(id_orden: int | None) -> None:
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    playwright, contexto = abrir_navegador()
    try:
        pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
        print("Inicia sesión en la ventana de ETAPA (usuario, clave y reCAPTCHA).")
        if not esperar_login(pagina):
            print("No se detectó el inicio de sesión en 10 minutos. Se cancela.")
            return

        print("Sesión detectada. Leyendo la lista de órdenes...")
        ir_a_ordenes(pagina)
        html, ids = volcar_pagina(pagina, CARPETA, f"ordenes_{marca}")
        captura = CARPETA / f"ordenes_{marca}.jpg"
        captura.write_bytes(capturar_pantalla(pagina))
        print(f"  HTML: {html}\n  Elementos: {ids}\n  Captura: {captura}")

        if id_orden is not None:
            print(f"Leyendo el detalle de la orden {id_orden}...")
            abrir_orden(pagina, id_orden)
            html, ids = volcar_pagina(pagina, CARPETA, f"orden_{id_orden}_{marca}")
            print(f"  HTML: {html}\n  Elementos: {ids}")
    finally:
        contexto.close()
        playwright.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnóstico de solo lectura del sitio de ETAPA.")
    parser.add_argument("--orden", type=int, help="Id de una orden para volcar su detalle")
    args = parser.parse_args()
    ejecutar(args.orden)


if __name__ == "__main__":
    main()

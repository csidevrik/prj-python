# =============================
# scripts/crear_regla_outlook.py
# =============================
"""
Crea en Outlook clásico la regla que mueve los correos de ETAPA a FACS.
Si la regla ya existe, no hace nada.

Uso:
    python scripts/crear_regla_outlook.py
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from logic.outlook_reader import REMITENTE_ETAPA, RUTA_FACS, OutlookETAPA  # noqa: E402

NOMBRE_REGLA = "ETAPA a FACS"
TIPO_REGLA_RECIBIDO = 0


def regla_existe(reglas, nombre: str) -> bool:
    return any(reglas.Item(i).Name == nombre for i in range(1, reglas.Count + 1))


def crear_regla(outlook: OutlookETAPA) -> None:
    carpeta = outlook.carpeta(RUTA_FACS)
    store = outlook.namespace.DefaultStore
    reglas = store.GetRules()

    if regla_existe(reglas, NOMBRE_REGLA):
        print(f"La regla '{NOMBRE_REGLA}' ya existe. No se modifica.")
        return

    regla = reglas.Create(NOMBRE_REGLA, TIPO_REGLA_RECIBIDO)
    regla.Conditions.SenderAddress.Enabled = True
    regla.Conditions.SenderAddress.Address = [REMITENTE_ETAPA]
    regla.Actions.MoveToFolder.Enabled = True
    regla.Actions.MoveToFolder.Folder = carpeta
    regla.Enabled = True
    reglas.Save()
    print(f"Regla '{NOMBRE_REGLA}' creada: remitente {REMITENTE_ETAPA} -> {RUTA_FACS}")


def main() -> None:
    crear_regla(OutlookETAPA())


if __name__ == "__main__":
    main()

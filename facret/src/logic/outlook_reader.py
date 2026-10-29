# =============================
# logic/outlook_reader.py
# =============================
"""
Lectura y movimiento de correos de ETAPA en Outlook clásico vía COM.
Requiere Outlook de escritorio configurado con la cuenta.
"""
import os

import win32com.client

REMITENTE_ETAPA = "info@comunicados-etapa.com"
RUTA_FACS = "Inbox\\CONTRACT\\ETAPA\\FACS"
CLASE_CORREO = 43


class OutlookETAPA:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")

    def carpeta(self, ruta: str):
        partes = [p for p in ruta.split("\\") if p]
        if partes[0].lower() == "inbox":
            partes = partes[1:]
        actual = self.namespace.GetDefaultFolder(6)
        for parte in partes:
            actual = actual.Folders[parte]
        return actual

    def correos_etapa(self, carpeta) -> list:
        items = carpeta.Items
        correos = []
        for i in range(1, items.Count + 1):
            mensaje = items.Item(i)
            if mensaje.Class != CLASE_CORREO:
                continue
            if REMITENTE_ETAPA in (mensaje.SenderEmailAddress or "").lower():
                correos.append(mensaje)
        return correos


def info_correo(mensaje) -> dict:
    return {
        "entry_id": mensaje.EntryID,
        "remitente": mensaje.SenderEmailAddress,
        "asunto": mensaje.Subject,
        "recibido": mensaje.ReceivedTime.strftime("%Y-%m-%d %H:%M"),
    }


def guardar_xml_adjuntos(mensaje, directorio: str) -> list[str]:
    rutas = []
    for adjunto in mensaje.Attachments:
        nombre = adjunto.FileName
        if not nombre.lower().endswith(".xml"):
            continue
        ruta = os.path.join(directorio, f"{len(rutas)}_{nombre}")
        adjunto.SaveAsFile(ruta)
        rutas.append(ruta)
    return rutas


def mover(mensaje, carpeta_destino) -> None:
    mensaje.Move(carpeta_destino)

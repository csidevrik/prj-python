# =============================
# logic/facs_downloader.py
# =============================
"""
Descargador de facturas ETAPA via Outlook local.
No requiere cuenta Microsoft paga ni configuración de Azure.
Solo necesita Outlook instalado y configurado con la cuenta.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional


class DescargadorFacturas:
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self._log = log_callback or print

        import win32com.client
        self._log("🔄 Conectando a Outlook...")
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self._log(f"✅ Conectado a Outlook")
        self._log(f"📧 Usuario: {self.namespace.CurrentUser.Name}")

    def descargar_facturas_etapa(
        self,
        carpeta_outlook: str = "Inbox\\CONTRACT\\ETAPA\\FACS",
        carpeta_guardar: str = "D:\\Facturas_ETAPA",
        correo_remitente: str = "info@comunicados-etapa.com",
    ) -> int:
        Path(carpeta_guardar).mkdir(parents=True, exist_ok=True)

        folder = self._get_folder(carpeta_outlook)
        total = 0

        self._log(f"🔍 Buscando facturas en: {carpeta_outlook}")

        for message in folder.Items:
            if correo_remitente.lower() not in message.SenderEmailAddress.lower():
                continue

            for attachment in message.Attachments:
                filename = attachment.FileName

                if not (filename.endswith(".xml") or filename.endswith(".pdf")):
                    continue

                filepath = os.path.join(carpeta_guardar, filename)

                if os.path.exists(filepath):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{ts}{ext}"
                    filepath = os.path.join(carpeta_guardar, filename)

                attachment.SaveAsFile(filepath)
                total += 1
                self._log(f"✅ Descargado: {filename}")

        self._log(f"✨ Total: {total} archivos descargados")
        self._log(f"📂 Guardados en: {carpeta_guardar}")
        return total

    def _get_folder(self, folder_path: str):
        """Navega a una subcarpeta de Outlook dada una ruta separada por \\"""
        parts = folder_path.split("\\")
        current = self.namespace.GetDefaultFolder(6)  # 6 = Inbox

        if parts[0].lower() == "inbox":
            parts = parts[1:]

        for part in parts:
            current = current.Folders[part]

        return current

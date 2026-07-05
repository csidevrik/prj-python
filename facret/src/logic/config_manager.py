# =============================
# logic/config_manager.py
# =============================
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent / "config" / "facs_config.json"

DEFAULT_CONFIG = {
    "carpeta_outlook": "Inbox\CONTRACT\ETAPA\FACS",
    "correo_remitente": "info@comunicados-etapa.com",
    "correo_destinatario": "csigua@emov.gob.ec",
    "carpeta_guardar": "D:\Facturas_ETAPA",
    "carpeta_trabajo": "",
}


def load_config() -> Dict[str, Any]:
    """Lee la configuración desde el JSON. Si no existe, devuelve default."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Guarda la configuración en el JSON."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_value(key: str, default: Any = None) -> Any:
    """Obtiene un valor específico de la configuración."""
    config = load_config()
    return config.get(key, default)


def set_value(key: str, value: Any) -> None:
    """Establece un valor específico y lo guarda."""
    config = load_config()
    config[key] = value
    save_config(config)

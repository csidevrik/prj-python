import os
from dotenv import load_dotenv

load_dotenv()

def get_deepseek_api_key() -> str:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("No se encontró DEEPSEEK_API_KEY en el archivo .env")
    return key
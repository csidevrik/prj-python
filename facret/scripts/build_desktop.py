#!/usr/bin/env python3
"""
Script para compilar la aplicación para escritorio
"""
import subprocess
import sys
import os

def build_desktop():
    """Compilar aplicación de escritorio"""
    print("🏗️  Compilando aplicación de escritorio...")
    
    try:
        # Comando para compilar con Flet
        result = subprocess.run([
            sys.executable, "-m", "flet", "pack", "main.py",
            "--name", "FACRET",
            "--icon", "src/assets/icons/app_icon.ico"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Compilación exitosa!")
        print(f"📦 Salida: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        print("❌ Error en la compilación:")
        print(f"Error: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_desktop()
    sys.exit(0 if success else 1)
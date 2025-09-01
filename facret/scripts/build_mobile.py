#!/usr/bin/env python3
"""
Script para compilar la aplicación para Android
"""
import subprocess
import sys

def build_android():
    """Compilar aplicación para Android"""
    print("📱 Compilando aplicación para Android...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "flet", "build", "apk",
            "--project", "facret-mobile"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Compilación para Android exitosa!")
        print(f"📦 APK generado: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        print("❌ Error en la compilación para Android:")
        print(f"Error: {e.stderr}")
        return False
    
    return True

def build_ios():
    """Compilar aplicación para iOS (solo en macOS)"""
    print("🍎 Compilando aplicación para iOS...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "flet", "build", "ipa"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Compilación para iOS exitosa!")
        print(f"📦 IPA generado: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        print("❌ Error en la compilación para iOS:")
        print(f"Error: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    import platform
    
    android_success = build_android()
    
    # iOS solo en macOS
    ios_success = True
    if platform.system() == "Darwin":
        ios_success = build_ios()
    else:
        print("ℹ️  Compilación de iOS solo disponible en macOS")
    
    sys.exit(0 if android_success and ios_success else 1)
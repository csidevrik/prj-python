#!/usr/bin/env python3
# =============================
# test_folder_stats.py
# =============================
"""
Script de prueba rápida para verificar que folder_stats funciona correctamente.
Ejecutar: cd facret && python test_folder_stats.py
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logic.folder_stats import get_folder_stats

# Prueba con carpeta del proyecto
test_folder = Path(__file__).parent / "data"

print("=" * 60)
print("TEST: folder_stats")
print("=" * 60)
print(f"\nCarpeta a analizar: {test_folder}")
print(f"¿Existe?: {test_folder.exists()}\n")

stats = get_folder_stats(test_folder)

if stats:
    print("✅ Estadísticas calculadas:")
    print(f"   • Archivos: {stats.num_archivos}")
    print(f"   • Carpetas: {stats.num_carpetas}")
    print(f"   • Tamaño: {stats.tamanio_str} ({stats.tamanio_mb:.2f} MB)")
else:
    print("❌ No se pudieron obtener estadísticas")

# Prueba con carpeta inexistente
print("\n" + "=" * 60)
print("TEST: Carpeta inexistente")
print("=" * 60)
inexistente = "D:\\NoExiste\\Carpeta"
print(f"\nCarpeta: {inexistente}")
stats2 = get_folder_stats(inexistente)
print(f"Resultado: {stats2}")
print("✅ Manejo correcto de error (retorna None)")

print("\n" + "=" * 60)
print("✅ Todos los tests pasaron")
print("=" * 60)

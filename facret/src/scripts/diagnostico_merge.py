"""
Diagnóstico: Identifica registros sin match en el merge
"""

import pandas as pd
from datetime import datetime, timedelta

RUTA_FACTURAS = r"c:\Users\csigua\dev\github\prj-python\facret\facturas.csv"
RUTA_INVENTARIO = r"c:\Users\csigua\dev\github\prj-python\facret\INVENTARIO_DATOS_ENLACES.csv"

print("📂 Leyendo archivos...")

# Leer facturas
df_facturas = pd.read_csv(RUTA_FACTURAS)
print(f"✅ Facturas: {len(df_facturas)} registros")

# Leer inventario
df_inventario = pd.read_csv(RUTA_INVENTARIO, quotechar='"', on_bad_lines='skip')
print(f"✅ Inventario: {len(df_inventario)} servicios")

# Renombrar
df_facturas.rename(columns={'code_inst': 'COD.SERV'}, inplace=True)

# Hacer merge con indicator para ver qué matcheó
df_merged = df_facturas.merge(
    df_inventario[['COD.SERV', 'GRUPO', 'UBICACION', 'TIPO UPGRADE', 'BANDW']],
    on='COD.SERV',
    how='left',
    indicator=True
)

print(f"\n📊 Merge result:")
print(df_merged['_merge'].value_counts())

# Mostrar registros SIN match (left_only)
sin_match = df_merged[df_merged['_merge'] == 'left_only']
print(f"\n❌ Registros SIN match en inventario: {len(sin_match)}")

if len(sin_match) > 0:
    print("\nDetalle de servicios SIN match:")
    print(sin_match[['COD.SERV', 'number_fac', 'value_serv', 'GRUPO', 'UBICACION']].to_string())

    print("\n\nCódigos de servicio SIN encontrar en inventario:")
    for cod in sin_match['COD.SERV'].unique():
        print(f"  - {cod}")

# Mostrar registros CON blancos
print(f"\n⚠️ Registros CON valores en blanco:")
con_blancos = df_merged[df_merged['GRUPO'].isna()]
print(f"Total: {len(con_blancos)}")

if len(con_blancos) > 0:
    print("\nDetalle:")
    print(con_blancos[['COD.SERV', 'number_fac', 'GRUPO', 'UBICACION', 'TIPO UPGRADE', 'BANDW']].to_string())

# Guardar CSV de diagnóstico
df_merged.to_csv(r"c:\Users\csigua\dev\github\prj-python\facret\diagnostico_merge.csv", index=False)
print(f"\n✅ Archivo de diagnóstico guardado: diagnostico_merge.csv")

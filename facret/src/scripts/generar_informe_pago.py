"""
Generador Automático de Informe Técnico Previo al Pago
Automatiza la creación del informe Word a partir de CSV de facturas e inventario
"""

import pandas as pd
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

RUTA_FACTURAS = r"c:\Users\csigua\dev\github\prj-python\facret\facturas.csv"
RUTA_INVENTARIO = r"c:\Users\csigua\dev\github\prj-python\facret\INVENTARIO_DATOS_ENLACES.csv"
RUTA_SALIDA = r"c:\Users\csigua\dev\github\prj-python\facret\reportes"
PERIODO = "OCTUBRE 2026"  # Cambiar según periodo

# Crear carpeta reportes si no existe
os.makedirs(RUTA_SALIDA, exist_ok=True)

# =============================================================================
# FUNCIONES UTILITARIAS
# =============================================================================

def excel_date_to_python(excel_date):
    """Convierte número serial de Excel a fecha Python"""
    if pd.isna(excel_date):
        return None
    # Excel epoch: 30/12/1899
    base_date = datetime(1899, 12, 30)
    return base_date + timedelta(days=int(excel_date))

def set_cell_background(cell, fill_color):
    """Establece color de fondo en celda Word"""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), fill_color)
    cell._element.get_or_add_tcPr().append(shading_elm)

def add_table_header(table, headers, bg_color="4472C4"):
    """Agrega encabezado con formato a tabla"""
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        if i < len(hdr_cells):
            cell = hdr_cells[i]
            cell.text = header_text
            set_cell_background(cell, bg_color)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)

# =============================================================================
# LEER Y PROCESAR DATOS
# =============================================================================

print("📂 Leyendo archivos...")

# Leer facturas
df_facturas = pd.read_csv(RUTA_FACTURAS)
print(f"✅ Facturas: {len(df_facturas)} registros")

# Leer inventario (quotechar maneja ubicaciones con comas)
df_inventario = pd.read_csv(RUTA_INVENTARIO, quotechar='"', on_bad_lines='skip')
print(f"✅ Inventario: {len(df_inventario)} servicios")

# Convertir fechas seriales del inventario a formato legible
df_inventario['F.I.S'] = df_inventario['F.I.S'].apply(excel_date_to_python)
df_inventario['F.F.S'] = df_inventario['F.F.S'].apply(excel_date_to_python)

# Renombrar columna para match
df_facturas.rename(columns={'code_inst': 'COD.SERV'}, inplace=True)

# JOIN: facturas + inventario
df_merged = df_facturas.merge(
    df_inventario[['COD.SERV', 'GRUPO', 'UBICACION', 'TIPO UPGRADE', 'BANDW']],
    on='COD.SERV',
    how='left'
)

print(f"✅ Merge: {len(df_merged)} registros procesados")

# Agrupar por GRUPO para subtotales
grupos = df_merged.groupby('GRUPO')

# =============================================================================
# CREAR DOCUMENTO WORD
# =============================================================================

print("📝 Generando documento Word...")

doc = Document()

# ENCABEZADO
title = doc.add_heading('INFORME TECNICO PREVIO AL PAGO', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph(
    'SERVICIO MENSUALIZADO DE INTERNET, DATOS Y HOUSING\n'
    'CONTRATO: RE-CEP-EMOVEP-2026-03'
)
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph(f'PERIODO: {PERIODO}')
doc.add_paragraph(f'Fecha de emisión: {datetime.now().strftime("%d/%m/%Y")}')

doc.add_paragraph()

# SECCIÓN 1: ANTECEDENTES
doc.add_heading('1. ANTECEDENTES', 1)
doc.add_paragraph(
    'Previo al pago de servicios de Internet y Datos provisto por ETAPA EP, '
    'se detalla el resumen de facturas procesadas en este período.'
)

# SECCIÓN 2: DESCRIPCIÓN GENERAL
doc.add_heading('2. DESCRIPCIÓN DEL SERVICIO', 1)
doc.add_paragraph(
    'Los servicios contratados comprenden enlaces de Internet, Datos y Housing '
    'distribuidos en los siguientes grupos:'
)

# Tabla resumen por grupo
table_grupos = doc.add_table(rows=1, cols=3)
table_grupos.style = 'Light Grid Accent 1'
add_table_header(table_grupos, ['GRUPO', 'CANTIDAD SERVICIOS', 'TOTAL FACTURADO'])

for grupo_name, grupo_data in grupos:
    row_cells = table_grupos.add_row().cells
    row_cells[0].text = str(grupo_name)
    row_cells[1].text = str(len(grupo_data))
    row_cells[2].text = f"${grupo_data['value_serv'].sum():.2f}"

doc.add_paragraph()

# SECCIÓN 3: DETALLE DE FACTURAS
doc.add_heading('3. DETALLE DE FACTURAS POR GRUPO', 1)

# Tabla principal de facturas
table_facturas = doc.add_table(rows=1, cols=11)
table_facturas.style = 'Light Grid Accent 1'

headers = [
    'PARTIDA', 'GRUPO', 'CÓDIGO', 'UBICACIÓN',
    'TIPO', 'BANDW', 'FACTURA', 'VALOR', 'FEC. EMISIÓN', 'FEC. VENCIMIENTO'
]
add_table_header(table_facturas, headers)

partida = 1
for _, row in df_merged.iterrows():
    row_cells = table_facturas.add_row().cells
    row_cells[0].text = str(partida)
    row_cells[1].text = str(row['GRUPO']) if pd.notna(row['GRUPO']) else ""
    row_cells[2].text = str(row['COD.SERV'])
    row_cells[3].text = str(row['UBICACION']) if pd.notna(row['UBICACION']) else ""
    row_cells[4].text = str(row['TIPO UPGRADE']) if pd.notna(row['TIPO UPGRADE']) else ""
    row_cells[5].text = str(row['BANDW']) if pd.notna(row['BANDW']) else ""
    row_cells[6].text = str(row['number_fac'])
    row_cells[7].text = f"${row['value_serv']:.2f}"
    row_cells[8].text = str(row['fecha_emision'])
    row_cells[9].text = str(row['fecha_max_pago'])
    partida += 1

doc.add_paragraph()

# SECCIÓN 4: RESUMEN FINANCIERO
doc.add_heading('4. RESUMEN FINANCIERO', 1)

table_resumen = doc.add_table(rows=1, cols=2)
table_resumen.style = 'Light Grid Accent 1'
add_table_header(table_resumen, ['CONCEPTO', 'MONTO'])

# Subtotales por grupo
for grupo_name, grupo_data in grupos:
    row_cells = table_resumen.add_row().cells
    row_cells[0].text = f"Subtotal Grupo {grupo_name}"
    row_cells[1].text = f"${grupo_data['value_serv'].sum():.2f}"

# Total general
row_cells = table_resumen.add_row().cells
row_cells[0].text = "TOTAL FACTURAS"
total = df_merged['value_serv'].sum()
row_cells[1].text = f"${total:.2f}"

# Dar formato a la fila de total
last_row = table_resumen.rows[-1]
for cell in last_row.cells:
    set_cell_background(cell, "FFC000")
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.bold = True

doc.add_paragraph()

# SECCIÓN 5: OBSERVACIONES
doc.add_heading('5. OBSERVACIONES Y CONCLUSIONES', 1)
doc.add_paragraph(
    f'Se solicita la cancelación de {len(df_merged)} facturas por un monto total '
    f'de ${total:.2f} (sin incluir IVA), correspondientes al período {PERIODO}.'
)

doc.add_paragraph()
doc.add_paragraph('Elaborado por: Sr. Carlos Sigua')
doc.add_paragraph(f'Fecha: {datetime.now().strftime("%d de %B de %Y")}')

# =============================================================================
# GUARDAR DOCUMENTO
# =============================================================================

nombre_archivo = f"INFORME_PAGO_{PERIODO.replace(' ', '_')}.docx"
ruta_completa = os.path.join(RUTA_SALIDA, nombre_archivo)

doc.save(ruta_completa)

print(f"✅ Documento generado: {ruta_completa}")
print(f"📊 Total facturas: {len(df_merged)}")
print(f"💰 Total a pagar: ${total:.2f}")

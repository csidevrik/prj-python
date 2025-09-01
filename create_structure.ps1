# Script para crear la estructura de carpetas del proyecto FACRET
# Versión simplificada y funcional

Write-Host "Creando estructura de carpetas para proyecto facret..." -ForegroundColor Green

# Obtener la ruta actual
$currentPath = Get-Location
Write-Host "Ruta actual: $currentPath" -ForegroundColor Cyan

# Función para crear carpetas
function Create-Folder {
    param([string]$Path)
    if (-not (Test-Path -Path $Path)) {
        try {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Host "CREADO: $Path" -ForegroundColor Green
        } catch {
            Write-Host "ERROR al crear: $Path - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "YA EXISTE: $Path" -ForegroundColor Yellow
    }
}

# Función para crear archivos
function Create-File {
    param([string]$Path, [string]$Content = "")
    try {
        if (-not (Test-Path -Path $Path)) {
            New-Item -ItemType File -Path $Path -Force | Out-Null
            if ($Content) {
                Set-Content -Path $Path -Value $Content -Encoding UTF8
            }
            Write-Host "ARCHIVO CREADO: $Path" -ForegroundColor Cyan
        } else {
            Write-Host "ARCHIVO EXISTE: $Path" -ForegroundColor DarkCyan
        }
    } catch {
        Write-Host "ERROR al crear archivo: $Path - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Crear carpeta raíz del proyecto
Write-Host "`nCreando carpeta raiz facret..." -ForegroundColor Blue
Create-Folder -Path "facret"

# Cambiar al directorio del proyecto
try {
    Set-Location "facret"
    Write-Host "Cambiado a directorio facret" -ForegroundColor Green
} catch {
    Write-Host "ERROR: No se pudo cambiar al directorio facret" -ForegroundColor Red
    exit 1
}

Write-Host "`nCreando estructura de carpetas..." -ForegroundColor Blue

# Lista de todas las carpetas a crear
$folders = @(
    "src",
    "src\components",
    "src\components\layout",
    "src\components\ui",
    "src\components\navigation",
    "src\views",
    "src\core",
    "src\core\services",
    "src\core\utils", 
    "src\core\models",
    "src\config",
    "src\assets",
    "src\assets\icons",
    "src\assets\images",
    "src\assets\styles",
    "tests",
    "tests\unit",
    "tests\integration",
    "docs",
    "docs\api",
    "docs\user",
    "docs\user\screenshots",
    "data",
    "data\templates",
    "data\templates\xml_templates",
    "data\templates\report_templates",
    "data\samples",
    "data\samples\sample_xml",
    "data\samples\sample_pdf",
    "data\exports",
    "data\exports\logs",
    "data\exports\reports",
    "scripts"
)

# Crear todas las carpetas
foreach ($folder in $folders) {
    Create-Folder -Path $folder
}

Write-Host "`nCreando archivos __init__.py..." -ForegroundColor Blue

# Lista de archivos __init__.py
$initFiles = @(
    "src\__init__.py",
    "src\components\__init__.py",
    "src\components\layout\__init__.py",
    "src\components\ui\__init__.py",
    "src\components\navigation\__init__.py",
    "src\views\__init__.py",
    "src\core\__init__.py",
    "src\core\services\__init__.py",
    "src\core\utils\__init__.py",
    "src\core\models\__init__.py",
    "src\config\__init__.py",
    "tests\__init__.py",
    "tests\unit\__init__.py",
    "tests\integration\__init__.py"
)

foreach ($file in $initFiles) {
    Create-File -Path $file -Content "# Init file"
}

Write-Host "`nCreando archivos principales..." -ForegroundColor Blue

# main.py
$mainContent = 'import flet as ft

def main(page: ft.Page):
    page.title = "facret - Facturacion Electronica"
    page.window_width = 1200
    page.window_height = 800
    page.add(ft.Text("facret App - En desarrollo"))

if __name__ == "__main__":
    ft.app(target=main)'

Create-File -Path "main.py" -Content $mainContent

# requirements.txt
$requirements = 'flet>=0.24.0
lxml>=4.9.3
openpyxl>=3.1.2
python-dateutil>=2.8.2
reportlab>=4.0.4
Pillow>=10.0.0'

Create-File -Path "requirements.txt" -Content $requirements

# requirements-dev.txt
$requirementsDev = '-r requirements.txt
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0'

Create-File -Path "requirements-dev.txt" -Content $requirementsDev

# .gitignore
$gitignore = '__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/
.env
.venv
env/
venv/
.vscode/
.idea/
.flet/
*.log
data/exports/logs/*
data/exports/reports/*'

Create-File -Path ".gitignore" -Content $gitignore

# README.md
$readme = '# facret - Sistema de Facturacion Electronica

## Instalacion
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar
```
python main.py
```'

Create-File -Path "README.md" -Content $readme

# Crear archivos .gitkeep para carpetas vacias
Create-File -Path "data\exports\logs\.gitkeep" -Content ""
Create-File -Path "data\exports\reports\.gitkeep" -Content ""
Create-File -Path "src\assets\icons\.gitkeep" -Content ""
Create-File -Path "src\assets\images\.gitkeep" -Content ""

# Volver al directorio original
Set-Location $currentPath

Write-Host "`nESTRUCTURA CREADA EXITOSAMENTE!" -ForegroundColor Green
Write-Host "`nProximos pasos:" -ForegroundColor Cyan
Write-Host "1. cd facret" -ForegroundColor White
Write-Host "2. python -m venv venv" -ForegroundColor White  
Write-Host "3. venv\Scripts\activate" -ForegroundColor White
Write-Host "4. pip install -r requirements.txt" -ForegroundColor White
Write-Host "5. python main.py" -ForegroundColor White

Write-Host "`nRuta del proyecto: $currentPath\facret" -ForegroundColor Magenta
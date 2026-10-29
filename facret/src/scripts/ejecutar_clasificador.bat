@echo off
cd /d "%~dp0\..\.."
if not exist data\informes mkdir data\informes
poetry run python src\scripts\clasificar_facturas.py --real >> data\informes\tarea.log 2>&1

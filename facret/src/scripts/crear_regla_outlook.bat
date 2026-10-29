@echo off
cd /d "%~dp0\..\.."
poetry run python src\scripts\crear_regla_outlook.py

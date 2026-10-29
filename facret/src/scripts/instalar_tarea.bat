@echo off
schtasks /Create /TN "FACRET_ClasificadorETAPA" /TR "\"%~dp0ejecutar_clasificador.bat\"" /SC MINUTE /MO 5 /IT /F

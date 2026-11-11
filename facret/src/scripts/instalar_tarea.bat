@echo off
schtasks /Create /TN "FACRET_ClasificadorETAPA" /TR "\"%~dp0ejecutar_clasificador.bat\"" /SC HOURLY /MO 1 /IT /F

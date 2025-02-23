import PyInstaller.__main__
import sys
import os

def build_exe():
    # Directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directorio de salida para el exe
    dist_dir = os.path.join(current_dir, '..', 'dmig-web', 'static', 'downloads')
    
    # Asegurarse que el directorio de destino existe
    os.makedirs(dist_dir, exist_ok=True)
    
    # Usar el separador correcto según el sistema operativo
    separator = ';' if sys.platform.startswith('win') else ':'
    
    # Configuración común para ambas versiones
    common_options = [
        'main.py',  # Script principal
        '--onefile',  # Crear un solo archivo ejecutable
        '--noconsole',  # Sin ventana de consola
        '--name', 'dmig_agent',  # Nombre base del ejecutable
        '--add-data', f'VERSION{separator}.',  # Usar el separador correcto
        '--hidden-import', 'win32timezone',
        '--hidden-import', 'win32api',
        '--hidden-import', 'win32con',
    ]
    
    # Construir versión x64
    PyInstaller.__main__.run([
        *common_options,
        '--distpath', dist_dir,
        '--name', 'dmig_agent_x64'
    ])
    
    # Construir versión x86
    if sys.maxsize > 2**32:  # Solo si estamos en un sistema x64
        PyInstaller.__main__.run([
            *common_options,
            '--distpath', dist_dir,
            '--name', 'dmig_agent_x86',
            '--target-arch', 'x86'
        ])

if __name__ == '__main__':
    build_exe() 
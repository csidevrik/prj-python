import PyInstaller.__main__
import os

def build_exe():
    """Construye el ejecutable del agente"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--name=dmig-agent',
        '--add-data=utils;utils',  # Incluir el directorio utils
        '--hidden-import=utils.network',  # Importaciones ocultas
        '--hidden-import=utils.system',
        '--hidden-import=utils.validation',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        '--clean'
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
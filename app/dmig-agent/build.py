import os
import PyInstaller.__main__

def build_exe():
    """Construye el ejecutable del agente"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_path = os.path.join(script_dir, "utils")  # Ruta absoluta de utils
    path_sep = ";" if os.name == "nt" else ":"  # ';' en Windows, ':' en Linux

    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--name=dmig-agent',
        f'--add-data={utils_path}{path_sep}utils',  # Usa ruta absoluta
        '--hidden-import=utils.network',
        '--hidden-import=utils.system',
        '--hidden-import=utils.validation',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        '--clean'
    ])

if __name__ == '__main__':
    build_exe()

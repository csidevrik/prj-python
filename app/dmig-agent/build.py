import os
<<<<<<< HEAD
import sys
=======
import PyInstaller.__main__
>>>>>>> 53c0c336bf6b57b4fa90bec44f9a9fef6100c557

def build_exe():
    """Construye el ejecutable del agente para x86 y x64"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
<<<<<<< HEAD
    
    # Opciones base comunes
    base_options = [
        'service.py',
        '--onefile',
        '--add-data=utils;utils',
        '--hidden-import=wmi',
        '--hidden-import=win32com.client',
        '--hidden-import=win32serviceutil',
        '--hidden-import=win32service',
        '--hidden-import=win32event',
        '--hidden-import=servicemanager',
        '--hidden-import=pythoncom',
        '--hidden-import=psutil',
        '--hidden-import=win32timezone',
        '--hidden-import=win32api',
=======
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
>>>>>>> 53c0c336bf6b57b4fa90bec44f9a9fef6100c557
        '--workpath=build',
        '--clean'
<<<<<<< HEAD
    ]

    # Construir versión x86 (32-bit)
    x86_options = base_options + [
        '--name=dmig_agent_x86',
        '--distpath=dist/x86',
        '--target-architecture', 'x86'
    ]
    print("\n🔨 Construyendo versión x86...")
    PyInstaller.__main__.run(x86_options)

    # Construir versión x64 (64-bit)
    x64_options = base_options + [
        '--name=dmig_agent_x64',
        '--distpath=dist/x64'
    ]
    print("\n🔨 Construyendo versión x64...")
    PyInstaller.__main__.run(x64_options)

    print("\n✅ Construcción completada:")
    print("   - dist/x86/dmig_agent_x86.exe (32-bit)")
    print("   - dist/x64/dmig_agent_x64.exe (64-bit)")
=======
    ])
>>>>>>> 53c0c336bf6b57b4fa90bec44f9a9fef6100c557

if __name__ == '__main__':
    build_exe()

import platform
import socket
import uuid
import json
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import subprocess
import sys
import ctypes
import time
import threading

def get_all_ips():
    """Obtiene todas las IPs de las interfaces de red"""
    ips = []
    try:
        # Intentar obtener la IP principal primero
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Esto nos da la IP que se usa para salir a internet
            s.connect(('8.8.8.8', 1))
            main_ip = s.getsockname()[0]
            ips.append(main_ip)
        except:
            pass
        finally:
            s.close()

        # Obtener el resto de las IPs
        interfaces = socket.getaddrinfo(socket.gethostname(), None)
        for interface in interfaces:
            ip = interface[4][0]
            # Filtrar IPs locales, IPv6 y duplicados
            if not ip.startswith(('127.', '::1', 'fe80:')) and ':' not in ip and ip not in ips:
                ips.append(ip)
        
        # Ordenar las IPs
        ips = sorted(ips, key=lambda x: (
            # Priorizar IPs que empiezan con 192.169
            not x.startswith('192.169'),
            # Luego ordenar normalmente
            tuple(int(part) for part in x.split('.'))
        ))
        
        print("\nIPs disponibles:")
        for i, ip in enumerate(ips, 1):
            print(f"{i}. {ip}{' (IP principal)' if ip == main_ip else ''}")
        
        if len(ips) > 1:
            while True:
                try:
                    choice = input("\nSeleccione el número de la IP a usar (Enter para usar la primera): ").strip()
                    if not choice:
                        return ips[0]
                    choice = int(choice)
                    if 1 <= choice <= len(ips):
                        selected_ip = ips[choice - 1]
                        print(f"\nIP seleccionada: {selected_ip}")
                        return selected_ip
                    print("Número inválido, intente de nuevo")
                except ValueError:
                    print("Entrada inválida, intente de nuevo")
        elif ips:
            return ips[0]
    except Exception as e:
        print(f"Error al obtener IPs: {e}")
    
    return '0.0.0.0'  # Fallback a todas las interfaces

class DmigAgent:
    def __init__(self, port=8000):
        # Obtener la IP real de la máquina
        self.ip = get_all_ips()
        self.port = port
        
        print(f"\nIniciando agente DMIG...")
        print(f"IP seleccionada: {self.ip}")
        print(f"Puerto: {self.port}")
        
        try:
            # Intentar primero con la IP específica
            print(f"\nIntentando iniciar servidor en {self.ip}:{self.port}")
            self.server = SimpleXMLRPCServer(
                (self.ip, self.port), 
                allow_none=True,
                logRequests=True
            )
        except Exception as e:
            print(f"\n⚠️ No se pudo iniciar en IP específica: {str(e)}")
            print("Intentando con 0.0.0.0...")
            
            # Si falla, intentar con 0.0.0.0
            self.server = SimpleXMLRPCServer(
                ('0.0.0.0', self.port), 
                allow_none=True,
                logRequests=True
            )
        
        self.register_functions()

    def register_functions(self):
        """Registra las funciones RPC disponibles"""
        self.server.register_function(self.get_system_info, 'get_system_info')
        self.server.register_function(self.test_connection, 'test_connection')
        print("\n✅ Funciones registradas:")
        print("- get_system_info")
        print("- test_connection")

    def get_system_info(self):
        """Obtiene información del sistema"""
        try:
            info = {
                'os': platform.system() + ' ' + platform.release(),
                'architecture': platform.machine(),
                'hostname': socket.gethostname(),
                'ip': self.ip,  # Usar la IP detectada
                'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                               for elements in range(0,8*6,8)][::-1])
            }
            print(f"\n✅ get_system_info llamado, retornando: {info}")
            return json.dumps(info)
        except Exception as e:
            print(f"\n❌ Error en get_system_info: {str(e)}")
            raise

    def test_connection(self):
        """Función simple para probar la conexión"""
        return json.dumps({
            'status': 'ok',
            'message': 'Conexión exitosa',
            'timestamp': time.time()
        })

    def start(self):
        """Inicia el servidor RPC"""
        print(f"""
============================================
    Agente DMIG iniciado correctamente
============================================
- IP: {self.ip}
- Puerto: {self.port}
- Hostname: {socket.gethostname()}
- Sistema: {platform.system()} {platform.release()}
- Arquitectura: {platform.machine()}

El agente está esperando conexiones...
Presione Ctrl+C para detener el agente.
============================================
""")
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n⚡ Deteniendo el agente...")
            self.server.server_close()
        except Exception as e:
            print(f"\n❌ Error en el servidor: {str(e)}")
            self.server.server_close()
            raise

def test_local_connection(ip, port=8000):
    """Prueba la conexión local al agente"""
    try:
        print(f"\nProbando conexión a {ip}:{port}")
        
        # Esperar un momento para asegurar que el servidor está listo
        time.sleep(1)
        
        with xmlrpc.client.ServerProxy(f'http://{ip}:{port}', allow_none=True, verbose=True) as proxy:
            # Probar conexión básica
            print("Intentando test_connection()...")
            result = proxy.test_connection()
            print(f"Test conexión: {json.loads(result)}")
            
            print("\nIntentando get_system_info()...")
            info = proxy.get_system_info()
            print(f"Info sistema: {json.loads(info)}")
            
            return True
    except Exception as e:
        print(f"❌ Error al probar conexión: {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        # Verificar privilegios de administrador
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Se requieren privilegios de administrador")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        
        print("✅ Ejecutando con privilegios de administrador")
        
        # Iniciar el agente
        agent = DmigAgent()
        
        # Probar conexión local en otro thread
        def delayed_test():
            time.sleep(2)  # Esperar 2 segundos
            print("\n🔍 Iniciando prueba de conexión local...")
            if test_local_connection(agent.ip):  # Usar la IP seleccionada
                print("✅ Prueba de conexión exitosa")
            else:
                print("❌ Prueba de conexión fallida")
        
        test_thread = threading.Thread(target=delayed_test)
        test_thread.daemon = True  # El thread se cerrará cuando el programa principal termine
        test_thread.start()
        
        # Iniciar el agente
        print("\n🚀 Iniciando servidor RPC...")
        agent.start()
        
    except Exception as e:
        print(f"\n❌ Error fatal: {type(e).__name__}: {str(e)}")
        with open('agent_error.log', 'w') as f:
            f.write(f"{type(e).__name__}: {str(e)}")
        print("\nPresione ENTER para cerrar...")
        input()
        sys.exit(1) 
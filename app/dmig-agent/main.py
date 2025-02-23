import platform
import socket
import uuid
import json
from xmlrpc.server import SimpleXMLRPCServer
import subprocess
import sys
import ctypes

class DmigAgent:
    def __init__(self, port=8000):
        self.port = port
        self.server = SimpleXMLRPCServer(('0.0.0.0', self.port), allow_none=True)
        self.register_functions()

    def register_functions(self):
        """Registra las funciones RPC disponibles"""
        try:
            # Registrar cada método individualmente
            self.server.register_function(self.get_system_info, 'get_system_info')
            print("✅ Método 'get_system_info' registrado")
            
            self.server.register_function(self.change_ip_address, 'change_ip_address')
            print("✅ Método 'change_ip_address' registrado")
            
            self.server.register_function(self.change_hostname, 'change_hostname')
            print("✅ Método 'change_hostname' registrado")
            
            self.server.register_function(self.start_service, 'start_service')
            print("✅ Método 'start_service' registrado")
        except Exception as e:
            print(f"❌ Error al registrar métodos RPC: {str(e)}")

    def get_system_info(self):
        """Obtiene información del sistema"""
        info = {
            'os': platform.system() + ' ' + platform.release(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'ip': socket.gethostbyname(socket.gethostname()),
            'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,8*6,8)][::-1])
        }
        return json.dumps(info)

    def change_ip_address(self, new_ip, subnet_mask, gateway):
        """Cambia la dirección IP del sistema"""
        try:
            if platform.system() == 'Windows':
                # Obtiene el nombre de la interfaz de red
                interface = subprocess.check_output(
                    'netsh interface ipv4 show interfaces',
                    shell=True
                ).decode()
                
                # Asume que queremos configurar la primera interfaz activa
                interface_name = interface.split('\n')[3].split()[0]
                
                # Configura la nueva IP
                subprocess.check_call(
                    f'netsh interface ipv4 set address name="{interface_name}" '
                    f'static {new_ip} {subnet_mask} {gateway}',
                    shell=True
                )
                return json.dumps({'success': True, 'message': 'IP actualizada correctamente'})
            else:
                return json.dumps({'success': False, 'message': 'Sistema operativo no soportado'})
        except Exception as e:
            return json.dumps({'success': False, 'message': str(e)})

    def change_hostname(self, new_hostname):
        """Cambia el nombre del host"""
        try:
            if platform.system() == 'Windows':
                subprocess.check_call(f'wmic computersystem where name="%computername%" '
                                   f'call rename name="{new_hostname}"', shell=True)
                return json.dumps({'success': True, 'message': 'Hostname actualizado correctamente'})
            else:
                return json.dumps({'success': False, 'message': 'Sistema operativo no soportado'})
        except Exception as e:
            return json.dumps({'success': False, 'message': str(e)})

    def start_service(self):
        """Inicia el agente como servicio de Windows"""
        try:
            if platform.system() == 'Windows':
                # Aquí iría la lógica para registrar el servicio de Windows
                # Por ahora solo simulamos
                return json.dumps({
                    'success': True,
                    'message': 'Servicio iniciado correctamente'
                })
            else:
                return json.dumps({
                    'success': False,
                    'message': 'Sistema operativo no soportado'
                })
        except Exception as e:
            return json.dumps({
                'success': False,
                'message': str(e)
            })

    def start(self):
        """Inicia el servidor RPC"""
        print(f"""
============================================
    Agente DMIG iniciado correctamente
============================================
- Puerto: {self.port}
- IP local: {socket.gethostbyname(socket.gethostname())}
- Hostname: {socket.gethostname()}

Métodos RPC disponibles:
- get_system_info
- change_ip_address
- change_hostname
- start_service

El agente está esperando conexiones...
Presione Ctrl+C para detener el agente.
============================================
""")
        self.server.serve_forever()

if __name__ == '__main__':
    try:
        # Verificar si se ejecuta con privilegios de administrador
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
            
        agent = DmigAgent()
        agent.start()
    except Exception as e:
        with open('agent_error.log', 'w') as f:
            f.write(str(e))
        sys.exit(1)

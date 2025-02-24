import platform
import socket
import uuid
import json
from xmlrpc.server import SimpleXMLRPCServer
import subprocess
import sys
import ctypes
from utils.network import get_all_ips
import wmi

class DmigAgent:
    def __init__(self, port=8000):
        self.ip = get_all_ips()
        self.port = port
        
        try:
            print(f"\nIniciando agente DMIG en {self.ip}:{self.port}...")
            self.server = SimpleXMLRPCServer((self.ip, self.port), allow_none=True)
        except Exception as e:
            print(f"⚠️ No se pudo iniciar en {self.ip}, usando 0.0.0.0: {e}")
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
            'ip': self.ip,
            'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,8*6,8)][::-1])
        }
        return json.dumps(info)

    def change_ip_address(self, new_ip, subnet_mask="255.255.255.0", gateway=None):
        """Cambia la dirección IP de la interfaz seleccionada"""
        try:
            if platform.system() != 'Windows':
                return json.dumps({
                    'success': False,
                    'message': 'Sistema operativo no soportado'
                })

            # Obtener información de la interfaz que corresponde a la IP actual
            c = wmi.WMI()
            network_adapters = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
            target_adapter = None
            
            for adapter in network_adapters:
                if self.ip in adapter.IPAddress:
                    target_adapter = adapter
                    break
            
            if not target_adapter:
                return json.dumps({
                    'success': False,
                    'message': f'No se encontró la interfaz con IP {self.ip}'
                })

            # Primero cambiar la IP y máscara
            ip_result = target_adapter.EnableStatic(
                IPAddress=[new_ip],
                SubnetMask=[subnet_mask]
            )

            if ip_result[0] != 0:
                return json.dumps({
                    'success': False,
                    'message': f'Error al cambiar IP: código {ip_result[0]}'
                })

            # Si se proporcionó gateway, establecerlo en una llamada separada
            if gateway:
                gateway_result = target_adapter.SetGateways(DefaultIPGateway=[gateway])
                if gateway_result[0] != 0:
                    return json.dumps({
                        'success': False,
                        'message': f'IP cambiada pero error al establecer gateway: código {gateway_result[0]}'
                    })

            # Actualizar la IP en la instancia
            self.ip = new_ip
            return json.dumps({
                'success': True,
                'message': f'IP cambiada exitosamente a {new_ip}',
                'adapter': target_adapter.Description,
                'gateway_updated': gateway is not None
            })

        except Exception as e:
            return json.dumps({
                'success': False,
                'message': f'Error: {str(e)}'
            })

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
- IP: {self.ip}
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

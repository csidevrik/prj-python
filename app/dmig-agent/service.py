import win32serviceutil
import win32service
import win32event
import win32timezone
import servicemanager
import socket
import sys
import os
import time
import threading
from main import DmigAgent

class DmigService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DmigAgent"
    _svc_display_name_ = "DMIG Agent Service"
    _svc_description_ = "Servicio de agente DMIG para migración de red"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.agent = None
        self.server_thread = None
        self.is_alive = True
        self.running = True

    def log_info(self, message):
        """Registra mensaje informativo"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PID_UNKNOWN,
            message
        )

    def log_warning(self, message):
        """Registra advertencia"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_WARNING_TYPE,
            servicemanager.PID_UNKNOWN,
            message
        )

    def log_error(self, message):
        """Registra error"""
        servicemanager.LogErrorMsg(message)

    def verify_port_status(self):
        """Verifica si el puerto está en uso"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.agent.ip, self.agent.port))
            sock.close()
            return result == 0
        except:
            return False

    def verify_server(self):
        """Verifica que el servidor RPC esté funcionando"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # timeout de 1 segundo
            result = sock.connect_ex(('127.0.0.1', self.agent.port))
            sock.close()
            return result == 0
        except:
            return False

    def SvcStop(self):
        """Detiene el servicio"""
        try:
            # Primero reportar que estamos en proceso de parada
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.running = False
            self.is_alive = False
            
            # Señalizar el evento de parada
            win32event.SetEvent(self.stop_event)
            
            # Dar tiempo para que el servidor se detenga
            time.sleep(1)
            
            if self.agent and self.agent.server:
                try:
                    self.agent.server.shutdown()
                    self.agent.server.server_close()
                except:
                    pass
                
            if self.server_thread and self.server_thread.is_alive():
                try:
                    self.server_thread.join(timeout=3)
                except:
                    pass
                    
            # Forzar la terminación si es necesario
            if self.server_thread and self.server_thread.is_alive():
                self.log_warning("Forzando terminación del servidor...")
                
            self.log_info("Servicio detenido correctamente")
            
        except Exception as e:
            self.log_error(f"Error al detener servicio: {str(e)}")
        finally:
            # Asegurar que el servicio se marque como detenido
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start_rpc_server(self):
        """Inicia el servidor RPC"""
        try:
            if self.agent and self.agent.server:
                self.log_info(f"Iniciando servidor RPC en {self.agent.ip}:{self.agent.port}")
                self.agent.server.serve_forever()
        except Exception as e:
            self.log_error(f"Error en servidor RPC: {str(e)}")
            raise

    def SvcDoRun(self):
        """Ciclo principal del servicio"""
        try:
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            
            # Crear el agente RPC
            self.agent = DmigAgent()
            
            self.log_info(f"""
=== Iniciando DMIG Agent ===
IP: {self.agent.ip}
Puerto: {self.agent.port}
Hostname: {socket.gethostname()}
==========================
            """)

            # Verificar que el servidor se creó correctamente
            if not hasattr(self.agent, 'server'):
                raise Exception("El servidor RPC no se inicializó correctamente")

            # Iniciar servidor en thread separado
            self.server_thread = threading.Thread(
                target=self.start_rpc_server,
                daemon=True  # El thread se cerrará cuando el servicio se detenga
            )
            self.server_thread.start()
            
            # Esperar a que el servidor esté listo
            retries = 0
            while not self.verify_server() and retries < 10:
                time.sleep(1)
                retries += 1
                self.log_info(f"Esperando que el servidor RPC esté listo... ({retries}/10)")
            
            if not self.verify_server():
                raise Exception("El servidor RPC no pudo iniciarse después de 10 intentos")
            
            self.log_info(f"✅ Servidor RPC activo en puerto {self.agent.port}")
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            
            # Loop principal
            while self.running:
                if not self.verify_server():
                    self.log_warning("Servidor RPC no responde, reiniciando...")
                    self.server_thread = threading.Thread(
                        target=self.start_rpc_server,
                        daemon=True
                    )
                    self.server_thread.start()
                
                rc = win32event.WaitForSingleObject(self.stop_event, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
                    
                # Verificar estado del servidor cada 5 segundos
                if not self.server_thread.is_alive() and self.running:
                    self.log_warning("Servidor RPC caído, intentando reiniciar...")
                    self.server_thread = threading.Thread(
                        target=self.start_rpc_server,
                        daemon=True
                    )
                    self.server_thread.start()
                    self.log_info("Thread del servidor RPC reiniciado")

            # Verificar que el puerto está en uso
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.agent.ip, self.agent.port))
            sock.close()
            
            if result != 0:
                self.log_warning(f"¡ADVERTENCIA! Puerto {self.agent.port} no está respondiendo")
            else:
                self.log_info(f"Puerto {self.agent.port} está activo y respondiendo")
            
            self.log_info("Servicio iniciado correctamente")

        except Exception as e:
            self.log_error(f"Error en el servicio: {str(e)}")
            self.running = False
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(DmigService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error al iniciar el dispatcher: {str(e)}")
    else:
        win32serviceutil.HandleCommandLine(DmigService) 
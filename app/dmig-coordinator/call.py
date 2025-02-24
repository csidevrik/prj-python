from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Label, Button, Input, Static
import xmlrpc.client
import json
import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from textual.worker import get_current_worker

from widgets.connection_tester import ConnectionTester
from styles.test_screen import TEST_SCREEN_CSS

class TestScreen(App):
    """Pantalla principal para probar conexión con agente"""
    
    CSS = TEST_SCREEN_CSS

    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=3)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="test_container"):
            with Vertical(classes="input-section"):
                yield Label("Prueba de Conexión con Agente DMIG", classes="title")
                with Horizontal(classes="input-row"):
                    yield Label("IP del Agente:")
                    yield Input(placeholder="IP", id="ip_input", value="192.169.100.38")
                with Horizontal(classes="input-row"):
                    yield Label("Puerto:")
                    yield Input(placeholder="Puerto", id="port_input", value="8000")
                
                # Sección para cambiar IP
                yield Label("Cambiar IP", classes="section-title")
                with Horizontal(classes="input-row"):
                    yield Label("Nueva IP:")
                    yield Input(placeholder="192.168.1.100", id="new_ip_input")
                with Horizontal(classes="input-row"):
                    yield Label("Máscara:")
                    yield Input(placeholder="255.255.255.0", id="subnet_mask_input")
                with Horizontal(classes="input-row"):
                    yield Label("Gateway:")
                    yield Input(placeholder="192.168.1.1", id="gateway_input")
                
                # Sección para cambiar Hostname
                yield Label("Cambiar Hostname", classes="section-title")
                with Horizontal(classes="input-row"):
                    yield Label("Nuevo Hostname:")
                    yield Input(placeholder="NEW-HOST-NAME", id="hostname_input")
                
                # Botones de acción
                with Horizontal(classes="button-row"):
                    yield Button("Probar Conexión", id="test_btn", variant="primary")
                    yield Button("Cambiar IP", id="change_ip_btn")
                    yield Button("Cambiar Hostname", id="change_hostname_btn")
            
            with Vertical(id="results_section"):
                yield Label("📝 Resultados de la prueba:", classes="results-title")
                with ScrollableContainer(id="results_container"):
                    yield Static("", id="results")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja los eventos de botones"""
        if event.button.id == "test_btn":
            # Usar el worker de Textual para ejecutar la tarea asíncrona
            self.run_worker(self.test_connection())
        elif event.button.id == "change_ip_btn":
            self.run_worker(self.change_ip())
        elif event.button.id == "change_hostname_btn":
            # También convertir change_hostname a async
            self.run_worker(self.change_hostname())

    async def make_rpc_call(self, ip: str, port: int, method: str, *args) -> dict:
        """Hace una llamada RPC con timeout y manejo de errores"""
        url = f'http://{ip}:{port}'
        loop = asyncio.get_event_loop()
        
        try:
            # Crear proxy con timeout
            proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            proxy._ServerProxy__transport.timeout = 5  # timeout de 5 segundos
            
            # Ejecutar llamada RPC en thread separado
            rpc_method = getattr(proxy, method)
            result = await loop.run_in_executor(self.executor, rpc_method, *args)
            return json.loads(result)
        except Exception as e:
            # Escapar caracteres especiales del mensaje de error
            error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
            return {
                'success': False,
                'message': f'Error de conexión: {error_msg}'
            }

    async def test_connection(self) -> None:
        """Prueba la conexión básica con el agente"""
        results = self.query_one("#results")
        
        try:
            ip = self.query_one("#ip_input").value
            port = int(self.query_one("#port_input").value)
            url = f'http://{ip}:{port}'
            output = [f"\n🔌 Intentando conectar a {url}..."]
            
            # Hacer llamada RPC con timeout
            result = await self.make_rpc_call(ip, port, 'get_system_info')
            
            if result.get('success') is False:
                # Asegurarse que el mensaje de error esté escapado
                message = result.get('message', '').replace('[', '\\[').replace(']', '\\]')
                output.append(f"❌ {message}")
            else:
                output.append("✅ Respuesta recibida:")
                for key, value in result.items():
                    output.append(f"   {key}: {value}")
                output.append("\n✅ Conexión establecida correctamente")
        
        except ValueError:
            output = ["❌ Error: Puerto inválido"]
        except Exception as e:
            # Escapar caracteres especiales en el mensaje de error
            error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
            output = [
                f"\n❌ Error: {error_msg}",
                "   Verifica que:",
                "   1. El agente esté corriendo en la IP y puerto especificados",
                "   2. No haya firewalls bloqueando la conexión",
                "   3. La red entre las máquinas esté funcionando (prueba con ping)"
            ]
        
        # Unir y actualizar el resultado
        results.update("\n".join(output))

    async def change_ip(self) -> None:
        """Cambia la IP del agente"""
        results = self.query_one("#results")
        
        try:
            ip = self.query_one("#ip_input").value
            port = int(self.query_one("#port_input").value)
            new_ip = self.query_one("#new_ip_input").value
            subnet_mask = self.query_one("#subnet_mask_input").value
            gateway = self.query_one("#gateway_input").value

            output = [f"\n🔌 Intentando cambiar IP {ip} → {new_ip}..."]
            
            # Hacer llamada RPC con timeout
            result = await self.make_rpc_call(
                ip, port, 'change_ip_address',
                new_ip, subnet_mask, gateway
            )
            
            if result.get('success'):
                output.extend([
                    "✅ IP cambiada correctamente",
                    f"   Mensaje: {result.get('message')}",
                    "\n⚠️ La conexión se perderá mientras el agente cambia su IP"
                ])
            else:
                output.extend([
                    "❌ Error al cambiar IP",
                    f"   Mensaje: {result.get('message')}"
                ])
                
        except ValueError:
            output = ["❌ Error: Datos inválidos"]
        except Exception as e:
            output = [f"\n❌ Error inesperado: {str(e)}"]
        
        results.update("\n".join(output))

    async def change_hostname(self) -> None:
        """Cambia el hostname del agente"""
        results = self.query_one("#results")
        
        try:
            ip = self.query_one("#ip_input").value
            port = int(self.query_one("#port_input").value)
            new_hostname = self.query_one("#hostname_input").value
            
            output = [f"\n🔌 Intentando cambiar hostname..."]
            
            result = await self.make_rpc_call(
                ip, port, 'change_hostname', new_hostname
            )
            
            if result.get('success'):
                output.extend([
                    "✅ Hostname cambiado correctamente",
                    f"   Mensaje: {result.get('message')}"
                ])
            else:
                output.extend([
                    "❌ Error al cambiar hostname",
                    f"   Mensaje: {result.get('message')}"
                ])
                
        except ValueError:
            output = ["❌ Error: Puerto inválido"]
        except Exception as e:
            output = [f"\n❌ Error inesperado: {str(e)}"]
        
        results.update("\n".join(output))

if __name__ == "__main__":
    app = TestScreen()
    app.run() 
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Label, Button, Input, Static
import xmlrpc.client
import json

from widgets.connection_tester import ConnectionTester
from styles.test_screen import TEST_SCREEN_CSS

class TestScreen(App):
    """Pantalla principal para probar conexión con agente"""
    
    CSS = TEST_SCREEN_CSS

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
        if event.button.id == "test_btn":
            self.test_connection()
        elif event.button.id == "change_ip_btn":
            self.change_ip()
        elif event.button.id == "change_hostname_btn":
            self.change_hostname()

    def test_connection(self) -> None:
        """Realiza la prueba de conexión con el agente"""
        ip = self.query_one("#ip_input").value
        port = self.query_one("#port_input").value
        results = self.query_one("#results")
        
        try:
            port = int(port)
            url = f'http://{ip}:{port}'
            output = [f"\n🔌 Intentando conectar a {url}..."]
            
            with xmlrpc.client.ServerProxy(url, allow_none=True) as proxy:
                # Probar get_system_info
                try:
                    output.append("\n1. Probando get_system_info()...")
                    info = proxy.get_system_info()
                    info_dict = json.loads(info)
                    output.append("✅ Respuesta recibida:")
                    for key, value in info_dict.items():
                        output.append(f"   {key}: {value}")
                except Exception as e:
                    output.append(f"❌ Error en get_system_info: {str(e)}")

                # Probar change_ip_address
                try:
                    output.append("\n2. Probando change_ip_address()...")
                    result = proxy.change_ip_address("192.168.1.100", "255.255.255.0", "192.168.1.1")
                    result_dict = json.loads(result)
                    output.append("✅ Respuesta recibida:")
                    output.append(f"   success: {result_dict.get('success')}")
                    output.append(f"   message: {result_dict.get('message')}")
                except Exception as e:
                    output.append(f"❌ Error en change_ip_address: {str(e)}")

                # Probar change_hostname
                try:
                    output.append("\n3. Probando change_hostname()...")
                    result = proxy.change_hostname("NEW-HOST-NAME")
                    result_dict = json.loads(result)
                    output.append("✅ Respuesta recibida:")
                    output.append(f"   success: {result_dict.get('success')}")
                    output.append(f"   message: {result_dict.get('message')}")
                except Exception as e:
                    output.append(f"❌ Error en change_hostname: {str(e)}")

                # Probar start_service
                try:
                    output.append("\n4. Probando start_service()...")
                    result = proxy.start_service()
                    result_dict = json.loads(result)
                    output.append("✅ Respuesta recibida:")
                    output.append(f"   success: {result_dict.get('success')}")
                    output.append(f"   message: {result_dict.get('message')}")
                except Exception as e:
                    output.append(f"❌ Error en start_service: {str(e)}")

        except ValueError:
            output = ["❌ Error: El puerto debe ser un número"]
        except Exception as e:
            output = [
                f"\n❌ Error de conexión: {str(e)}",
                "   Verifica que:",
                "   1. El agente esté corriendo en la IP y puerto especificados",
                "   2. No haya firewalls bloqueando la conexión",
                "   3. La red entre las máquinas esté funcionando (prueba con ping)"
            ]
        
        results.update("\n".join(output))

    def change_ip(self) -> None:
        """Cambia la IP del agente"""
        ip = self.query_one("#ip_input").value
        port = self.query_one("#port_input").value
        new_ip = self.query_one("#new_ip_input").value
        subnet_mask = self.query_one("#subnet_mask_input").value
        gateway = self.query_one("#gateway_input").value
        results = self.query_one("#results")
        
        try:
            port = int(port)
            url = f'http://{ip}:{port}'
            output = [f"\n🔌 Intentando cambiar IP en {url}..."]
            
            with xmlrpc.client.ServerProxy(url, allow_none=True) as proxy:
                result = proxy.change_ip_address(new_ip, subnet_mask, gateway)
                result_dict = json.loads(result)
                output.append("✅ Respuesta recibida:")
                output.append(f"   success: {result_dict.get('success')}")
                output.append(f"   message: {result_dict.get('message')}")
                
        except Exception as e:
            output = [f"\n❌ Error al cambiar IP: {str(e)}"]
        
        results.update("\n".join(output))

    def change_hostname(self) -> None:
        """Cambia el hostname del agente"""
        ip = self.query_one("#ip_input").value
        port = self.query_one("#port_input").value
        new_hostname = self.query_one("#hostname_input").value
        results = self.query_one("#results")
        
        try:
            port = int(port)
            url = f'http://{ip}:{port}'
            output = [f"\n🔌 Intentando cambiar hostname en {url}..."]
            
            with xmlrpc.client.ServerProxy(url, allow_none=True) as proxy:
                result = proxy.change_hostname(new_hostname)
                result_dict = json.loads(result)
                output.append("✅ Respuesta recibida:")
                output.append(f"   success: {result_dict.get('success')}")
                output.append(f"   message: {result_dict.get('message')}")
                
        except Exception as e:
            output = [f"\n❌ Error al cambiar hostname: {str(e)}"]
        
        results.update("\n".join(output))

if __name__ == "__main__":
    app = TestScreen()
    app.run() 
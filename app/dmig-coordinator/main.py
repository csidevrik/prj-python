from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Static, Label, Button, Input
from textual.binding import Binding
from textual.screen import Screen
import xmlrpc.client
import socket
import json
import ipaddress
from typing import Dict
import asyncio

class NodeInfo(Static):
    """Widget para mostrar información detallada de un nodo"""
    
    def __init__(self, node_data: Dict):
        super().__init__()
        self.node_data = node_data

    def compose(self) -> ComposeResult:
        yield Static(f"Sistema Operativo: {self.node_data.get('os', 'N/A')}")
        yield Static(f"Arquitectura: {self.node_data.get('architecture', 'N/A')}")
        yield Static(f"Hostname: {self.node_data.get('hostname', 'N/A')}")
        yield Static(f"IP: {self.node_data.get('ip', 'N/A')}")
        yield Static(f"MAC: {self.node_data.get('mac', 'N/A')}")

class NetworkScanner:
    @staticmethod
    async def scan_network(network_str: str, port: int = 8000) -> Dict[str, dict]:
        try:
            nodes = {}
            network = ipaddress.IPv4Network(network_str)
            
            async def check_host(ip):
                try:
                    with xmlrpc.client.ServerProxy(f'http://{ip}:{port}') as proxy:
                        info = json.loads(proxy.get_system_info())
                        return ip, info
                except:
                    return None

            tasks = [check_host(str(ip)) for ip in network.hosts()]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result:
                    ip, info = result
                    nodes[ip] = info
            
            return nodes
        except ValueError as e:
            raise ValueError(f"Red inválida: {str(e)}")

class ConfigScreen(Screen):
    """Pantalla de configuración"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Configuración de Red", classes="title"),
                Horizontal(
                    Label("Red a escanear (CIDR):"),
                    Input(placeholder="Ej: 192.168.1.0/24", id="network_input", value="10.10.10.0/24"),
                    classes="config-row"
                ),
                Horizontal(
                    Label("Puerto de agentes:"),
                    Input(placeholder="Puerto", id="port_input", value="8000"),
                    classes="config-row"
                ),
                Button("Guardar y Continuar", id="save_config", variant="primary"),
                id="config_container"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_config":
            network = self.query_one("#network_input").value
            port = self.query_one("#port_input").value
            try:
                # Validar red
                ipaddress.IPv4Network(network)
                # Validar puerto
                port = int(port)
                if not (1 <= port <= 65535):
                    raise ValueError("Puerto fuera de rango")
                
                # Guardar configuración y cambiar a pantalla principal
                self.app.network = network
                self.app.port = port
                self.app.push_screen(NetworkMigrationScreen())
            except ValueError as e:
                self.notify(f"Error de configuración: {str(e)}", severity="error")

class NetworkMigrationScreen(Screen):
    """Pantalla principal para la migración de red"""

    BINDINGS = [
        Binding("r", "refresh", "Actualizar"),
        Binding("c", "change_ip", "Cambiar IP"),
        Binding("h", "change_hostname", "Cambiar Hostname"),
        Binding("s", "start_service", "Iniciar Servicio"),
        Binding("q", "quit", "Salir"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label(f"Red actual: {self.app.network}", id="network_label"),
                Label("Escaneando red en busca de agentes...", id="status_label"),
                DataTable(id="nodes_table"),
                Horizontal(
                    Button("Actualizar", id="refresh_btn", variant="primary"),
                    Button("Cambiar IP", id="change_ip_btn"),
                    Button("Cambiar Hostname", id="change_hostname_btn"),
                    Button("Iniciar Servicio", id="start_service_btn"),
                    classes="controls"
                ),
                id="main_container"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("IP", "Hostname", "OS", "Arquitectura", "Estado")
        self.refresh_nodes()

    async def refresh_nodes(self) -> None:
        status_label = self.query_one("#status_label")
        table = self.query_one(DataTable)
        table.clear()
        
        try:
            status_label.update("Escaneando red en busca de agentes...")
            nodes = await NetworkScanner.scan_network(self.app.network, self.app.port)
            
            if not nodes:
                status_label.update("No se encontraron agentes en la red")
                return
                
            status_label.update(f"Se encontraron {len(nodes)} agentes")
            
            for ip, info in nodes.items():
                table.add_row(
                    ip,
                    info['hostname'],
                    info['os'],
                    info['architecture'],
                    "✅ Conectado"
                )
        except Exception as e:
            self.notify(f"Error al escanear la red: {str(e)}", severity="error")

    async def action_refresh(self) -> None:
        await self.refresh_nodes()

    def action_start_service(self) -> None:
        """Inicia el servicio en los agentes seleccionados"""
        table = self.query_one(DataTable)
        selected = table.cursor_row
        if selected is None:
            self.notify("Seleccione un agente primero", severity="warning")
            return

        ip = table.get_row_at(selected)[0]
        try:
            with xmlrpc.client.ServerProxy(f'http://{ip}:{self.app.port}') as proxy:
                result = json.loads(proxy.start_service())
                if result.get('success'):
                    self.notify("Servicio iniciado correctamente")
                else:
                    self.notify(f"Error: {result.get('message')}", severity="error")
        except Exception as e:
            self.notify(f"Error al iniciar servicio: {str(e)}", severity="error")

class NodeDetailScreen(Screen):
    """Pantalla para mostrar detalles de un nodo"""

    def __init__(self, node_data: Dict):
        super().__init__()
        self.node_data = node_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield NodeInfo(self.node_data)
        yield Footer()

class DmigCoordinator(App):
    """Aplicación principal del coordinador"""

    CSS = """
    .title {
        text-align: center;
        padding: 1;
    }
    .config-row {
        height: 3;
        margin: 1;
    }
    .controls {
        height: 3;
        align: center middle;
    }
    #config_container {
        align: center middle;
    }
    #main_container {
        width: 100%;
        height: 100%;
    }
    #nodes_table {
        width: 100%;
        height: 1fr;
    }
    .status_label {
        text-align: center;
        padding: 1;
    }
    Button {
        margin: 1 2;
    }
    """

    def __init__(self):
        super().__init__()
        self.network = "10.10.10.0/24"
        self.port = 8000

    def on_mount(self) -> None:
        self.push_screen(ConfigScreen())

if __name__ == "__main__":
    app = DmigCoordinator()
    app.run() 
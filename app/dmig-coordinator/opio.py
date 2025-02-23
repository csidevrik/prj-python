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
            
            # Mejorar la detección de IP local
            local_ip = None
            try:
                # Intentar obtener la IP real de la interfaz
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("192.169.100.38", port))  # Conectar al agente conocido
                local_ip = s.getsockname()[0]
                s.close()
            except:
                # Fallback a método alternativo
                local_ip = socket.gethostbyname(socket.gethostname())
            
            print(f"\n🔍 IP Local detectada: {local_ip}")
            print(f"🌐 Escaneando red: {network_str}")
            print(f"🔌 Puerto: {port}")
            
            async def check_host(ip: str) -> tuple[str, dict] | None:
                try:
                    url = f'http://{ip}:{port}'
                    with xmlrpc.client.ServerProxy(url, allow_none=True) as proxy:
                        # Aumentamos el timeout para redes más lentas
                        proxy._ServerProxy__transport.timeout = 5
                        try:
                            info = proxy.get_system_info()
                            info_dict = json.loads(info)
                            print(f"✅ Agente encontrado en {ip}")
                            return ip, info_dict
                        except Exception as e:
                            print(f"No se encontró agente en {ip}")
                            return None
                except Exception as e:
                    return None

            # Primero intentar con la IP conocida
            known_ip = "192.169.100.38"
            result = await check_host(known_ip)
            if result:
                ip, info = result
                nodes[ip] = info
                print(f"✅ Agente encontrado en IP conocida: {known_ip}")

            # Luego escanear el resto de la red de manera más eficiente
            batch_size = 50  # Reducimos el batch size para mejor control
            all_ips = [str(ip) for ip in network.hosts() if str(ip) != known_ip]
            
            for i in range(0, len(all_ips), batch_size):
                batch = all_ips[i:i + batch_size]
                tasks = [check_host(ip) for ip in batch]
                results = await asyncio.gather(*tasks)
                
                for result in results:
                    if result:
                        ip, info = result
                        nodes[ip] = info

            return nodes
            
        except Exception as e:
            print(f"❌ Error al escanear la red: {type(e).__name__}: {str(e)}")
            raise

class ConfigScreen(Screen):
    """Pantalla de configuración"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("Configuración de Red", classes="title"),
                Horizontal(
                    Label("Red a escanear (CIDR):"),
                    Input(placeholder="Ej: 192.168.1.0/24", id="network_input", value="192.169.100.0/24"),
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
        Binding("q", "quit", "Salir", key_display="Q"),
    ]

    def compose(self) -> ComposeResult:
        """Compone la interfaz de la pantalla"""
        yield Header()
        yield Container(
            Vertical(
                Label(f"Red actual: {self.app.network}", id="network_label"),
                Label("Esperando escaneo de red...", id="status_label"),
                DataTable(id="nodes_table"),
                Horizontal(
                    Button("Actualizar", id="refresh_btn", variant="primary"),
                    Button("Cambiar IP", id="change_ip_btn"),
                    Button("Cambiar Hostname", id="change_hostname_btn"),
                    Button("Iniciar Servicio", id="start_service_btn"),
                    Button("Salir", id="quit_btn", variant="error"),
                    classes="controls"
                ),
                id="main_container"
            )
        )
        yield Footer()

    def update_network_label(self) -> None:
        """Actualiza la etiqueta de red actual"""
        network_label = self.query_one("#network_label")
        network_label.update(f"Red actual: {self.app.network} (Puerto: {self.app.port})")

    def on_mount(self) -> None:
        """Configuración inicial de la tabla"""
        table = self.query_one(DataTable)
        table.add_columns(
            "IP", 
            "Hostname", 
            "Sistema Operativo",
            "Arquitectura", 
            "MAC",
            "Estado"
        )
        self.update_network_label()

    async def refresh_nodes(self) -> None:
        """Actualiza la lista de nodos en la red"""
        status_label = self.query_one("#status_label")
        table = self.query_one(DataTable)
        table.clear()
        
        try:
            status_label.update(f"⚡ Iniciando escaneo de red {self.app.network}...")
            self.refresh_btn = self.query_one("#refresh_btn")
            self.refresh_btn.disabled = True
            
            nodes = await NetworkScanner.scan_network(self.app.network, self.app.port)
            
            if not nodes:
                status_label.update("❌ No se encontraron agentes en la red")
                return
            
            total_nodes = len(nodes)
            status_label.update(f"✅ Se encontraron {total_nodes} agente{'s' if total_nodes > 1 else ''}")
            
            # Ordenar nodos por IP
            sorted_nodes = dict(sorted(nodes.items(), key=lambda x: tuple(map(int, x[0].split('.')))))
            
            for ip, info in sorted_nodes.items():
                table.add_row(
                    ip,
                    info['hostname'],
                    info['os'],
                    info['architecture'],
                    info['mac'],
                    "✅ Conectado"
                )
                    
        except Exception as e:
            status_label.update("❌ Error al escanear la red")
            self.notify(f"Error: {str(e)}", severity="error")
        finally:
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.disabled = False

    async def action_start_service(self) -> None:
        """Inicia el servicio en los agentes seleccionados"""
        table = self.query_one(DataTable)
        selected = table.cursor_row
        
        # Verificar si la tabla tiene datos
        if table.row_count == 0:
            self.notify("No hay agentes disponibles en la tabla", severity="warning")
            return
        
        if selected is None:
            self.notify("Seleccione un agente primero", severity="warning")
            return
        
        ip = table.get_row_at(selected)[0]
        try:
            # Crear una tarea asíncrona para la llamada RPC
            async def call_start_service():
                loop = asyncio.get_event_loop()
                proxy = xmlrpc.client.ServerProxy(f'http://{ip}:{self.app.port}')
                # Ejecutar la llamada RPC en un thread separado
                result = await loop.run_in_executor(
                    None, 
                    lambda: json.loads(proxy.start_service())
                )
                return result

            # Ejecutar la llamada RPC de manera asíncrona
            result = await call_start_service()
            
            if result.get('success'):
                self.notify("✅ Servicio iniciado correctamente")
                # Actualizar el estado en la tabla
                row = table.cursor_row
                current_row_data = list(table.get_row_at(row))
                current_row_data[-1] = "✅ Servicio Iniciado"
                table.update_row_at(row, *current_row_data)
            else:
                self.notify(f"❌ Error: {result.get('message')}", severity="error")
                
        except Exception as e:
            self.notify(f"❌ Error al iniciar servicio: {str(e)}", severity="error")

    async def action_refresh(self) -> None:
        """Acción para el atajo de teclado R"""
        await self.refresh_nodes()

    async def action_quit(self) -> None:
        """Acción para salir de la aplicación"""
        try:
            self.notify("¡Hasta luego!", severity="information")
            await asyncio.sleep(0.5)
            self.app.exit()
        except Exception as e:
            self.notify(f"Error al salir: {str(e)}", severity="error")

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
        margin: 1;
    }
    #network_label, #status_label {
        text-align: center;
        padding: 1;
        background: $panel;
    }
    Button {
        margin: 1 2;
    }
    #quit_btn {
        background: red;
        margin-left: 4;
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
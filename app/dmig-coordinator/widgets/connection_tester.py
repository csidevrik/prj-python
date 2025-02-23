from textual.widgets import Static, Label
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Vertical

class ConnectionTester(Static):
    """Widget para mostrar resultados de la prueba de conexión"""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="results_section"):
            yield Label("📝 Resultados de la prueba:", classes="results-title")
            with ScrollableContainer(id="results_container"):
                yield Static("", id="results") 
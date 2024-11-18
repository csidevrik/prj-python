#!/usr/bin/python3
import subprocess
import ipaddress
import threading
import socket
import time
import sys
import re

class NetworkScanner:
    def __init__(self, network):
        self.network = network
        self.active_hosts = []
        self.lock = threading.Lock()

    def ping_host(self, ip):
        try:
            # Usar ping con timeout corto
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                with self.lock:
                    self.active_hosts.append(str(ip))
                    print(f"Host encontrado: {ip}")
                
                # Intentar obtener el hostname
                try:
                    hostname = socket.gethostbyaddr(str(ip))[0]
                    print(f"Hostname: {hostname}")
                except socket.herror:
                    pass
                
                # Intentar obtener MAC address
                try:
                    arp_output = subprocess.check_output(['arp', '-n', str(ip)]).decode()
                    mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', arp_output)
                    if mac:
                        print(f"MAC: {mac.group()}")
                except:
                    pass
        except Exception as e:
            print(f"Error al escanear {ip}: {e}")

    def scan(self):
        print(f"Escaneando red {self.network}...")
        threads = []
        
        try:
            network = ipaddress.ip_network(self.network)
        except ValueError:
            print("Error: Dirección de red inválida")
            return

        # Crear threads para cada IP
        for ip in network.hosts():
            thread = threading.Thread(target=self.ping_host, args=(ip,))
            thread.start()
            threads.append(thread)
            
            # Limitar el número de threads concurrentes
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []

        # Esperar que terminen los threads restantes
        for t in threads:
            t.join()

        print("\nResumen del escaneo:")
        print(f"Total de hosts encontrados: {len(self.active_hosts)}")
        print("Hosts activos:", ", ".join(self.active_hosts))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: ./network_scanner.py <red>")
        print("Ejemplo: ./network_scanner.py 192.168.1.0/24")
        sys.exit(1)

    scanner = NetworkScanner(sys.argv[1])
    scanner.scan()
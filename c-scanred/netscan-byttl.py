#!/usr/bin/python3
import subprocess
import ipaddress
import threading
import socket
import time
import sys
import re
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class NetworkScanner:
    def __init__(self, network):
        self.network = network
        self.active_hosts = []
        self.lock = threading.Lock()
        self.scan_results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_os_by_ttl(self, ip):
        try:
            # Ejecutar ping y capturar la salida completa
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
            
            # Buscar el valor TTL en la salida
            ttl_match = re.search(r'ttl=(\d+)', result.stdout)
            if ttl_match:
                ttl = int(ttl_match.group(1))
                # Determinar el SO basado en el TTL
                if ttl <= 64:
                    return "Linux/Unix"
                elif ttl <= 128:
                    return "Windows"
                elif ttl <= 255:
                    return "Cisco/Network Device"
                else:
                    return "Unknown"
            return "Unknown"
        except:
            return "Unknown"

    def ping_host(self, ip):
        try:
            # Usar ping con timeout corto
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
            
            if result.returncode == 0:
                host_info = {
                    'ip': str(ip),
                    'hostname': 'N/A',
                    'mac': 'N/A',
                    'vendor': 'N/A',
                    'ip_version': 'IPv4' if isinstance(ip, ipaddress.IPv4Address) else 'IPv6',
                    'os': self.get_os_by_ttl(ip)
                }

                # Intentar obtener el hostname
                try:
                    host_info['hostname'] = socket.gethostbyaddr(str(ip))[0]
                except:
                    pass

                # Intentar obtener MAC address
                try:
                    arp_output = subprocess.check_output(['arp', '-n', str(ip)]).decode()
                    mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', arp_output)
                    if mac:
                        host_info['mac'] = mac.group()
                except:
                    pass

                # Escaneo rápido de puertos comunes
                common_ports = [21, 22, 23, 25, 53, 80, 443, 445, 3389, 8080]
                open_ports = []
                for port in common_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.1)
                        result = sock.connect_ex((str(ip), port))
                        if result == 0:
                            service = socket.getservbyport(port)
                            open_ports.append({
                                'port': port,
                                'service': service,
                                'state': 'open',
                                'version': 'N/A'
                            })
                        sock.close()
                    except:
                        pass

                host_info['ports'] = open_ports

                with self.lock:
                    self.scan_results.append(host_info)
                    print(f"Host encontrado: {ip}")
                    print(f"Sistema Operativo: {host_info['os']}")
                    print(f"Hostname: {host_info['hostname']}")
                    print(f"MAC: {host_info['mac']}")
                    if open_ports:
                        print("Puertos abiertos:")
                        for port in open_ports:
                            print(f"  {port['port']}/{port['service']}")
                    print("-" * 50)

        except Exception as e:
            print(f"Error al escanear {ip}: {e}")

    def generate_csv_report(self):
        filename = f"network_scan_{self.timestamp}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['IP', 'Sistema Operativo', 'Hostname', 'MAC', 'IP Version', 'Puertos']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for host in self.scan_results:
                ports_str = '; '.join([f"{p['port']}/{p['service']}" 
                                     for p in host['ports']])
                writer.writerow({
                    'IP': host['ip'],
                    'Sistema Operativo': host['os'],
                    'Hostname': host['hostname'],
                    'MAC': host['mac'],
                    'IP Version': host['ip_version'],
                    'Puertos': ports_str
                })
        print(f"\nReporte CSV generado: {filename}")

    def generate_pdf_report(self):
        filename = f"network_scan_{self.timestamp}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=1,
            spaceAfter=30
        )
        elements.append(Paragraph('Reporte de Escaneo de Red', title_style))
        elements.append(Paragraph(f'Red: {self.network}', title_style))
        elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', title_style))
        elements.append(Spacer(1, 20))

        # Contenido por cada host
        for host in self.scan_results:
            # Información básica del host
            data = [
                ['IP:', host['ip']],
                ['Sistema Operativo:', host['os']],
                ['Hostname:', host['hostname']],
                ['MAC:', host['mac']],
                ['Tipo IP:', host['ip_version']]
            ]
            
            t = Table(data, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Tabla de puertos
            if host['ports']:
                elements.append(Paragraph('Puertos detectados:', styles['Heading2']))
                port_data = [['Puerto', 'Servicio', 'Estado']]
                for port in host['ports']:
                    port_data.append([
                        str(port['port']),
                        port['service'],
                        port['state']
                    ])
                
                t = Table(port_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(t)
            
            elements.append(Spacer(1, 30))

        doc.build(elements)
        print(f"\nReporte PDF generado: {filename}")

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
        print(f"Total de hosts encontrados: {len(self.scan_results)}")
        
        # Generar reportes
        self.generate_csv_report()
        self.generate_pdf_report()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: ./network_scanner.py <red>")
        print("Ejemplo: ./network_scanner.py 192.168.1.0/24")
        sys.exit(1)

    scanner = NetworkScanner(sys.argv[1])
    scanner.scan()
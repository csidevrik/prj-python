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
import nmap
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
        self.nm = nmap.PortScanner()

    def get_host_info(self, ip):
        info = {
            'ip': str(ip),
            'hostname': 'N/A',
            'mac': 'N/A',
            'vendor': 'N/A',
            'ports': [],
            'ip_version': 'IPv4' if isinstance(ip, ipaddress.IPv4Address) else 'IPv6',
            'status': 'down'
        }

        try:
            # Escaneo básico con nmap
            self.nm.scan(hosts=str(ip), arguments='-sn')
            if str(ip) in self.nm.all_hosts():
                info['status'] = 'up'
                
                # Escaneo de puertos
                self.nm.scan(hosts=str(ip), arguments='-sS -sV -p-')
                if str(ip) in self.nm.all_hosts():
                    for proto in self.nm[str(ip)].all_protocols():
                        ports = self.nm[str(ip)][proto].keys()
                        for port in ports:
                            service = self.nm[str(ip)][proto][port]
                            port_info = {
                                'port': port,
                                'state': service['state'],
                                'service': service['name'],
                                'version': service['version']
                            }
                            info['ports'].append(port_info)

                # Obtener hostname
                try:
                    info['hostname'] = socket.gethostbyaddr(str(ip))[0]
                except:
                    pass

                # Obtener MAC y vendor
                try:
                    if 'mac' in self.nm[str(ip)]['addresses']:
                        info['mac'] = self.nm[str(ip)]['addresses']['mac']
                        if 'vendor' in self.nm[str(ip)]:
                            info['vendor'] = self.nm[str(ip)]['vendor'].get(info['mac'], 'N/A')
                except:
                    pass

            with self.lock:
                if info['status'] == 'up':
                    self.scan_results.append(info)
                    print(f"Host encontrado: {ip}")
                    print(f"Hostname: {info['hostname']}")
                    print(f"MAC: {info['mac']}")
                    print(f"Vendor: {info['vendor']}")
                    print(f"Tipo IP: {info['ip_version']}")
                    if info['ports']:
                        print("Puertos abiertos:")
                        for port in info['ports']:
                            print(f"  {port['port']}/{port['service']} ({port['version']})")
                    print("-" * 50)

        except Exception as e:
            print(f"Error al escanear {ip}: {e}")

    def generate_csv_report(self):
        filename = f"network_scan_{self.timestamp}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['IP', 'Hostname', 'MAC', 'Vendor', 'IP Version', 'Puertos']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for host in self.scan_results:
                ports_str = '; '.join([f"{p['port']}/{p['service']} ({p['version']})" 
                                     for p in host['ports']])
                writer.writerow({
                    'IP': host['ip'],
                    'Hostname': host['hostname'],
                    'MAC': host['mac'],
                    'Vendor': host['vendor'],
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
                ['Hostname:', host['hostname']],
                ['MAC:', host['mac']],
                ['Vendor:', host['vendor']],
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
                port_data = [['Puerto', 'Estado', 'Servicio', 'Versión']]
                for port in host['ports']:
                    port_data.append([
                        str(port['port']),
                        port['state'],
                        port['service'],
                        port['version']
                    ])
                
                t = Table(port_data, colWidths=[1*inch, 1*inch, 2*inch, 2*inch])
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
            thread = threading.Thread(target=self.get_host_info, args=(ip,))
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
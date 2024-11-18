#!/usr/bin/python3
import subprocess
import ipaddress
import threading
import socket
import time
import sys
import re
import csv
import requests
import json
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
        # Cache para vendors de MAC para evitar consultas repetidas
        self.mac_vendor_cache = {}

    def get_vendor_from_api(self, mac):
        """Obtiene el fabricante desde la API de MacVendors.com"""
        if not mac or mac == 'N/A':
            return 'N/A'

        # Primero revisar el cache
        if mac in self.mac_vendor_cache:
            return self.mac_vendor_cache[mac]

        # Limpiar la MAC para obtener solo los primeros 6 dígitos
        mac_prefix = mac.replace(':', '').replace('-', '')[:6].upper()

        try:
            # Método 1: API de MacVendors.com
            url = f'https://api.macvendors.com/{mac}'
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                vendor = response.text
                self.mac_vendor_cache[mac] = vendor
                time.sleep(1)  # Respetar el rate limit de la API
                return vendor

        except Exception as e:
            pass

        try:
            # Método 2: API de macaddress.io (requiere API key)
            # Nota: Necesitas registrarte para obtener una API key
            url = 'https://api.macaddress.io/v1'
            headers = {'X-Authentication-Token': 'TU_API_KEY'}
            params = {'output': 'json', 'search': mac}
            response = requests.get(url, headers=headers, params=params, timeout=2)
            if response.status_code == 200:
                data = response.json()
                vendor = data.get('vendorDetails', {}).get('companyName', 'Unknown')
                self.mac_vendor_cache[mac] = vendor
                return vendor

        except Exception as e:
            pass

        try:
            # Método 3: Base de datos local del IEEE
            url = f'http://standards-oui.ieee.org/oui/oui.txt'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if mac_prefix in line:
                        vendor = line.split('\t')[-1].strip()
                        self.mac_vendor_cache[mac] = vendor
                        return vendor

        except Exception as e:
            pass

        # Si todo falla, intentar con wireshark OUI
        try:
            # Método 4: Base de datos de Wireshark
            url = 'https://gitlab.com/wireshark/wireshark/-/raw/master/manuf'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.split('\t')
                    if len(parts) > 1 and mac_prefix in parts[0]:
                        vendor = parts[-1].strip()
                        self.mac_vendor_cache[mac] = vendor
                        return vendor

        except Exception as e:
            pass

        vendor = 'Unknown'
        self.mac_vendor_cache[mac] = vendor
        return vendor

    def get_os_by_ttl_and_ports(self, ip, ttl, open_ports):
        """Detecta el SO usando combinación de TTL y puertos abiertos"""
        os_guess = []

        # Análisis por TTL
        if ttl <= 64:
            os_guess.append("Linux/Unix")
        elif ttl <= 128:
            os_guess.append("Windows")
        elif ttl <= 255:
            os_guess.append("Cisco/Network")

        # Análisis por puertos
        port_numbers = [p['port'] for p in open_ports]
        
        if 3389 in port_numbers:
            os_guess.append("Windows (RDP)")
        if 22 in port_numbers:
            os_guess.append("Linux/Unix (SSH)")
        if 445 in port_numbers:
            os_guess.append("Windows (SMB)")
        if set([135, 139, 445]).intersection(port_numbers):
            os_guess.append("Windows (NetBIOS/SMB)")
        if set([111, 2049]).intersection(port_numbers):
            os_guess.append("Linux/Unix (NFS)")

        # Retornar el SO más probable
        if os_guess:
            return max(set(os_guess), key=os_guess.count)
        return "Unknown"

    def scan_host(self, ip):
        try:
            # Realizar ping y capturar TTL
            ping_output = subprocess.check_output(
                ['ping', '-c', '1', '-W', '1', str(ip)],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            ttl_match = re.search(r'ttl=(\d+)', ping_output)
            ttl = int(ttl_match.group(1)) if ttl_match else 0

            host_info = {
                'ip': str(ip),
                'hostname': 'N/A',
                'mac': 'N/A',
                'vendor': 'N/A',
                'ip_version': 'IPv4' if isinstance(ip, ipaddress.IPv4Address) else 'IPv6',
                'ttl': ttl,
                'os': 'Unknown'
            }

            # Obtener hostname
            try:
                host_info['hostname'] = socket.gethostbyaddr(str(ip))[0]
            except:
                pass

            # Obtener MAC y vendor
            try:
                arp_output = subprocess.check_output(['arp', '-n', str(ip)]).decode()
                mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', arp_output)
                if mac_match:
                    mac = mac_match.group()
                    host_info['mac'] = mac
                    host_info['vendor'] = self.get_vendor_from_api(mac)
            except:
                pass

            # Escaneo de puertos
            common_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3389, 8080]
            open_ports = []
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((str(ip), port))
                    if result == 0:
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = f"unknown-port-{port}"
                        open_ports.append({
                            'port': port,
                            'service': service,
                            'state': 'open'
                        })
                    sock.close()
                except:
                    pass

            host_info['ports'] = open_ports
            host_info['os'] = self.get_os_by_ttl_and_ports(ip, ttl, open_ports)

            with self.lock:
                self.scan_results.append(host_info)
                print(f"\nHost encontrado: {ip}")
                print(f"Sistema Operativo: {host_info['os']}")
                print(f"Hostname: {host_info['hostname']}")
                print(f"MAC: {host_info['mac']}")
                print(f"Fabricante: {host_info['vendor']}")
                if open_ports:
                    print("Puertos abiertos:")
                    for port in open_ports:
                        print(f"  {port['port']}/{port['service']}")
                print("-" * 50)

        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            print(f"Error al escanear {ip}: {e}")

    def generate_csv_report(self):
        filename = f"network_scan_{self.timestamp}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['IP', 'Sistema Operativo', 'Hostname', 'MAC', 'Fabricante', 'IP Version', 'TTL', 'Puertos']
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
                    'Fabricante': host['vendor'],
                    'IP Version': host['ip_version'],
                    'TTL': host.get('ttl', 'N/A'),
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
                ['Fabricante:', host['vendor']],
                ['Tipo IP:', host['ip_version']],
                ['TTL:', str(host.get('ttl', 'N/A'))]
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
            thread = threading.Thread(target=self.scan_host, args=(ip,))
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
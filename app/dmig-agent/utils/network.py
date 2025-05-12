import socket
import psutil  

def get_all_ips():
    """Obtiene todas las IPs de las interfaces de red"""
    ips = []
    try:
        # Intentar obtener la IP principal primero
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Esto nos da la IP que se usa para salir a internet
            s.connect(('8.8.8.8', 1))
            main_ip = s.getsockname()[0]
            ips.append(main_ip)
        except:
            pass
        finally:
            s.close()

        # Obtener el resto de las IPs
        interfaces = socket.getaddrinfo(socket.gethostname(), None)
        for interface in interfaces:
            ip = interface[4][0]
            # Filtrar IPs locales, IPv6 y duplicados
            if not ip.startswith(('127.', '::1', 'fe80:')) and ':' not in ip and ip not in ips:
                ips.append(ip)
        
        # Eliminar duplicados y ordenar naturalmente
        ips = sorted(list(set(ips)), key=lambda x: tuple(int(part) for part in x.split('.')))
        
        print("\nIPs disponibles:")
        for i, ip in enumerate(ips, 1):
            print(f"{i}. {ip}{' (IP principal)' if ip == main_ip else ''}")
        
        if len(ips) > 1:
            while True:
                try:
                    choice = input("\nSeleccione el número de la IP a usar (Enter para usarla): ").strip()
                    if not choice:
                        return ips[0]
                    choice = int(choice)
                    if 1 <= choice <= len(ips):
                        selected_ip = ips[choice - 1]
                        print(f"\nIP seleccionada: {selected_ip}")
                        return selected_ip
                    print("Número inválido, intente de nuevo")
                except ValueError:
                    print("Entrada inválida, intente de nuevo")
        elif ips:
            return ips[0]
        
    except Exception as e:
        print(f"Error al obtener IPs: {e}")
        return '0.0.0.0' 

def get_interface_by_ip(ip_address):
    """Obtiene el nombre de la interfaz de red asociada a una dirección IP."""
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                return interface
    return None

def get_mac_by_interface(interface_name):
    """Obtiene la dirección MAC de una interfaz de red específica."""
    if interface_name in psutil.net_if_addrs():
        for addr in psutil.net_if_addrs()[interface_name]:
            if addr.family == psutil.AF_LINK:  # Identifica direcciones MAC
                return addr.address
    return None

def get_mac_by_ip(ip_address):
    """Dada una IP, obtiene la MAC de la interfaz asociada."""
    interface = get_interface_by_ip(ip_address)
    if not interface:
        return None
    return get_mac_by_interface(interface)
import socket

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
                    choice = input("\nSeleccione el número de la IP a usar (Enter para usar la primera): ").strip()
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
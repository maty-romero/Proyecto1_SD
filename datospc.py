import socket
import os
import platform
import psutil
from scapy.all import ARP, Ether, srp

# -----------------------------
# Funciones utilitarias
# -----------------------------

def obtener_ip_local():
    """Obtiene la IP principal de la máquina (LAN)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # No importa que no llegue a destino
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def obtener_interfaces():
    """Lista todas las interfaces de red y sus IPs."""
    interfaces = {}
    addrs = psutil.net_if_addrs()
    for nombre, lista in addrs.items():
        ips = [x.address for x in lista if x.family == socket.AF_INET]
        if ips:
            interfaces[nombre] = ips
    return interfaces

def obtener_hostname(ip):
    """Obtiene el nombre de host de una dirección IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

def escanear_red(subred=None):
    """Escanea la red local usando ARP para identificar dispositivos activos."""
    if subred is None:
        ip_local = obtener_ip_local()
        # Determinar subred automática: 192.168.1.37 -> 192.168.1.0/24
        partes = ip_local.split(".")
        subred = f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"

    arp_request = ARP(pdst=subred)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    paquete = broadcast / arp_request

    # Enviar ARP y recibir respuestas
    respuestas, _ = srp(paquete, timeout=2, verbose=False)

    dispositivos = []
    for _, respuesta in respuestas:
        dispositivos.append({
            "ip": respuesta.psrc,
            "mac": respuesta.hwsrc,
            "hostname": obtener_hostname(respuesta.psrc)
        })
    return dispositivos

# -----------------------------
# Main
# -----------------------------

def main():
    hostname = socket.gethostname()
    ip_local = obtener_ip_local()
    usuario = os.getlogin()
    sistema = platform.system() + " " + platform.release()
    puerto_default = 9090

    print("=== Información de la máquina local ===")
    print(f"Hostname: {hostname}")
    print(f"IP principal: {ip_local}")
    print(f"Usuario actual: {usuario}")
    print(f"Sistema operativo: {sistema}")
    print(f"Puerto por defecto: {puerto_default}")
    print("Interfaces activas e IPs:")
    interfaces = obtener_interfaces()
    for nombre, ips in interfaces.items():
        print(f"  {nombre}: {', '.join(ips)}")
    print("=======================================")

    print("\n=== Escaneo de la red local (ARP) ===")
    dispositivos = escanear_red()
    for disp in dispositivos:
        print(f"IP: {disp['ip']}, MAC: {disp['mac']}, Hostname: {disp['hostname']}")
    print("=======================================")

if __name__ == "__main__":
    main()

import threading

var_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def conectarse(): 
    try: 
        threading.Thread(target=_escuchar, daemon=True).start()
    except Exception as e: 
        print(f"Ocurrio error al unirse: {e}")

def _escuchar(): 
    pass 

def enviar_mensaje(ip_destino, puerto_destino, payload=None): 
    """Envía un mensaje a un proceso específico."""
    try:
        mensaje = {"hearbeat"}
        var_socket.sendto(json.dumps(msg).encode(), (ip_destino, puerto_destino))
    except socket.gaierror:
        pass # Ignorar si el host no se puede resolver (proceso caído)     

def escuchar(self):
    """Escucha mensajes entrantes."""
    while True:
        try:
            data, addr = self.sock.recvfrom(1024)
            message = json.loads(data.decode())
            self.handle_message(message)
        except Exception as e:
            print(f"[{self.id}] Error escuchando: {e}")

def procesar_mensaje(mensaje): 
    """Procesa un mensaje recibido."""
    if mensaje == "HEARTBEAT": 
        print("Se recibio Hearbeat!")    
        
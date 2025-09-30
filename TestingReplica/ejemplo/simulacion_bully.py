import os
import socket
import threading
import time
import json

class BullyProcess:
    def __init__(self, process_id, all_processes):
        self.id = process_id
        self.all_processes = all_processes
        self.peers = sorted([p for p in all_processes if p != self.id])
        self.coordinator = max(all_processes)
        self.is_election_active = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', 5000))
        print(f"[{self.id}] Iniciado. Coordinador inicial: {self.coordinator}.")

    def send_message(self, target_id, message_type, payload=None):
        """Envía un mensaje a un proceso específico."""
        try:
            msg = {"type": message_type, "from": self.id}
            if payload:
                msg.update(payload)
            target_host = f"p{target_id}"
            self.sock.sendto(json.dumps(msg).encode(), (target_host, 5000))
        except socket.gaierror:
            pass # Ignorar si el host no se puede resolver (proceso caído)

    def listen(self):
        """Escucha mensajes entrantes."""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                self.handle_message(message)
            except Exception as e:
                print(f"[{self.id}] Error escuchando: {e}")

    def handle_message(self, message):
        """Procesa un mensaje recibido."""
        msg_type = message['type']
        sender_id = message['from']
        
        if msg_type == 'ELECTION':
            print(f"[{self.id}] Recibió ELECTION de {sender_id}")
            if self.id > sender_id:
                self.send_message(sender_id, 'OK')
                if not self.is_election_active:
                    self.start_election()
        elif msg_type == 'OK':
            print(f"[{self.id}] Recibió OK de {sender_id}, deteniendo mi candidatura.")
            self.is_election_active = False # Alguien superior está activo
        elif msg_type == 'COORDINATOR':
            new_coordinator = message['coordinator_id']
            self.coordinator = new_coordinator
            self.is_election_active = False
            print(f"[{self.id}] Nuevo coordinador es {self.coordinator}")
        elif msg_type == 'PING':
            self.send_message(sender_id, 'PONG')

    def start_election(self):
        """Inicia el proceso de elección."""
        print(f"[{self.id}] Inicia una elección.")
        self.is_election_active = True
        higher_processes = [p for p in self.peers if p > self.id]

        if not higher_processes:
            # No hay nadie superior, este proceso gana.
            self.announce_victory()
            return

        for p_id in higher_processes:
            self.send_message(p_id, 'ELECTION')
        
        # Esperar un tiempo por respuestas OK
        time.sleep(2) 
        if self.is_election_active:
            # Si después de esperar no recibimos OK, ganamos
            self.announce_victory()

    def announce_victory(self):
        """Anuncia que este proceso es el nuevo coordinador."""
        print(f"-----> [{self.id}] GANA la elección y es el nuevo coordinador.")
        self.coordinator = self.id
        self.is_election_active = False
        for p_id in self.peers:
            if p_id != self.id:
                self.send_message(p_id, 'COORDINATOR', {'coordinator_id': self.id})

    def heartbeat(self):
        """Verifica si el coordinador está vivo."""
        while True:
            time.sleep(5)
            if self.id != self.coordinator:
                print(f"[{self.id}] Enviando ping a coordinador {self.coordinator}...")
                # Usamos un socket temporal para detectar el fallo
                ping_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ping_sock.settimeout(2)
                try:
                    msg = json.dumps({"type": "PING", "from": self.id}).encode()
                    ping_sock.sendto(msg, (f"p{self.coordinator}", 5000))
                    ping_sock.recvfrom(1024) # Esperar PONG
                except (socket.timeout, socket.gaierror):
                    print(f"[{self.id}] El coordinador {self.coordinator} no respondió. Iniciando elección.")
                    self.start_election()
                    break # Salir del bucle de heartbeat y esperar nuevo coord.
                finally:
                    ping_sock.close()

    def run(self):
        """Inicia los hilos del proceso."""
        threading.Thread(target=self.listen, daemon=True).start()
        if self.id != self.coordinator:
            threading.Thread(target=self.heartbeat, daemon=True).start()

if __name__ == "__main__":
    process_id = int(os.getenv("PROCESS_ID"))
    all_processes = [int(p) for p in os.getenv("ALL_PROCESSES").split(',')]
    bully = BullyProcess(process_id, all_processes)
    bully.run()
    # Mantener el script vivo
    while True:
        time.sleep(1)
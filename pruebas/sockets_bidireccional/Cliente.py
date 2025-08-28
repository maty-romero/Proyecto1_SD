import socket
import threading
import sys

def recibir_mensajes(s):
    """Maneja la recepción de mensajes del servidor en un hilo separado."""
    while True:
        try:
            data = s.recv(1024)
            if not data:
                print("\nEl servidor cerró la conexión.")
                break
            
            # Imprime la respuesta del servidor sin interferir con la entrada del usuario
            print(f"\nRespuesta del servidor: {data.decode('utf-8').strip()}", flush=True)

            if data.decode('utf-8').strip().lower() == "adios!":
                print("El servidor ha terminado el proceso.")
                break

        except (ConnectionResetError, OSError) as e:
            print("\nConexión con el servidor perdida.")
            break

def enviar_mensajes(s):
    """Maneja el envío de mensajes al servidor."""
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() == 'chau':
                s.sendall(user_input.encode('utf-8') + b'\n')
                print("Conexión cerrada.")
                break
            
            s.sendall(user_input.encode('utf-8') + b'\n')

        except Exception as e:
            print(f"Error al enviar datos: {e}")
            break


def Cliente():
    HOST = 'localhost'
    PORT = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("Conectado al servidor. Escribe 'chau' para salir y 'enviar_lista' para ver los escrito por otros clientes.")
        except ConnectionRefusedError:
            print("No se pudo conectar. Asegúrate de que el servidor está en ejecución.")
            return

        # Hilo para recibir mensajes
        hilo_recibir = threading.Thread(target=recibir_mensajes, args=(s,))
        hilo_recibir.daemon = True # El hilo terminará cuando el programa principal termine
        hilo_recibir.start()
        
        # Bucle principal para enviar mensajes
        enviar_mensajes(s)
        
        # Se asegura de que el socket se cierre al salir del bucle
        s.close()
        print("Conexión con el servidor cerrada.")

if __name__ == "__main__":
    Cliente()
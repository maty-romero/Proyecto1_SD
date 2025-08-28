import socket
import threading

# Lista compartida para almacenar las palabras de todos los clientes
palabras_recibidas = []
# Bloqueo para evitar que múltiples hilos modifiquen la lista al mismo tiempo
list_lock = threading.Lock()
# Lista para mantener las conexiones de todos los clientes
lista_de_conexiones = []


def manejar_cliente(conn, addr):
    """Maneja la comunicación con un cliente específico."""
    print(f"Cliente conectado desde {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Conexión con {addr} cerrada por el cliente.")
                # Elimina la conexión de la lista compartida al desconectarse
                with list_lock:
                    lista_de_conexiones.remove(conn)
                break
            
            mensaje_recibido = data.decode('utf-8').strip()
            print(f"Recibido de {addr}: {mensaje_recibido}")

            # Lógica de "acción especial"
            if mensaje_recibido.lower() == "enviar_lista":
                print(f"Comando 'enviar_lista' recibido de {addr}.")
                # Prepara el mensaje con las palabras
                with list_lock:
                    mensaje_a_enviar = "Lista de palabras recibidas:\n" + "\n".join(palabras_recibidas) + "\n"
                    # Envía la lista a todos los clientes
                    for c in lista_de_conexiones:
                        try:
                            c.sendall(mensaje_a_enviar.encode('utf-8'))
                        except Exception as e:
                            print(f"Error al enviar a un cliente: {e}")
                    # Limpia la lista después de enviarla
                    palabras_recibidas.clear()
            else:
                # Si no es un comando, agrega la palabra a la lista global de forma segura
                with list_lock:
                    palabras_recibidas.append(f"{addr[0]}: {mensaje_recibido}")
    
    except ConnectionResetError:
        print(f"El cliente {addr} ha cerrado la conexión de forma inesperada.")
    except Exception as e:
        print(f"Error al manejar el cliente {addr}: {e}")
    finally:
        # Se asegura de que el socket se cierre al salir del bucle del hilo
        conn.close()
        print(f"Conexión con el cliente {addr} cerrada")


def Servidor():
    """Inicia el servidor y escucha conexiones entrantes."""
    HOST = '0.0.0.0'
    PORT = 12345
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor esperando clientes en el puerto {PORT}")

        while True:
            try:
                conn, addr = s.accept()
                with list_lock:
                    lista_de_conexiones.append(conn)
                client_thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
                client_thread.start()
            except Exception as e:
                print(f"Error al aceptar conexión: {e}")
                break

if __name__ == "__main__":
    Servidor()
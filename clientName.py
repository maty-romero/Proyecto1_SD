import Pyro5.api
import uuid

def main():
    # Generamos un id único para cada cliente
    cliente_id = str(uuid.uuid4())[:8]

    # Conectarse al servidor
    servidor = Pyro5.api.Proxy("PYRONAME:ServidorPalabras")

    print(f"Cliente {cliente_id} conectado")

    while True:
        palabra = input("Escribe una palabra (o 'salir'): ").strip()
        if palabra.lower() == "salir":
            break

        # Enviar palabra al servidor y recibir respuestas de los demás
        respuestas = servidor.enviar_palabra(cliente_id, palabra)

        if respuestas:
            print("Respuestas de los demás clientes:")
            for cid, p in respuestas.items():
                print(f" - Cliente {cid}: {p}")
        else:
            print("Todavía no hay respuestas de otros clientes.")

if __name__ == "__main__":
    main()

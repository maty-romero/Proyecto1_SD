import Pyro5.api
import sys

from registro_clientes_partida.RegistroClientesPartida import RegistroClientesPartida


def main():
    nombre_logico = "registro.clientes"
    try:
        proxy_registro = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")

    except Pyro5.errors.NamingError:
        print(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
        print("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
        sys.exit(1)

    print("Conectado al servidor de registro.")

    nickname = input("Ingrese su NickName para la partida: ")

    respuesta_registro = proxy_registro.registrar_nodo_cliente(nickname)
    print(f"Respuesta del servidor: {respuesta_registro}")

if __name__ == "__main__":
    main()
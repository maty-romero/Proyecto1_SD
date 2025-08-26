import Pyro5.api
import sys

from registro_clientes_partida.RegistroClientesPartida import RegistroClientesPartida


def main():
    nombre_logico = "gestor.partida"
    try:
        proxy_partida = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")

    except Pyro5.errors.NamingError:
        print(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
        print("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
        sys.exit(1)

    print("Conectado al servidor de registro.")

    # Check if NickName is Unique
    nickname = input("Para jugar, Ingrese su NickName para la partida: ")
    is_unique = proxy_partida.CheckNickNameIsUnique(nickname)

    # Manejar mejor la validacion
    if(not isinstance(is_unique, bool)):
        print("Debe ingresar un STRING! Ejecute de nuevo script")
        sys.exit(1)

    while not is_unique:
        nickname = input("\nEl NickName ingresado ya esta siendo utilizado! Ingrese otro: ")
        is_unique = proxy_partida.CheckNickNameIsUnique(nickname)

    #print(f"El nickName es unico? => Server Responde: {is_unique}")

    #respuesta_registro = proxy_registro.registrar_nodo_cliente(nickname)
    #print(f"Respuesta del servidor: {respuesta_registro}")

if __name__ == "__main__":
    main()
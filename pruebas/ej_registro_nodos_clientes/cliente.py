# cliente.py
import Pyro5.api
import sys

def main():
    nombre_logico = "sistemas.distribuidos.registro"
    try:
        proxy_registro = Pyro5.api.Proxy(f"PYRONAME:{nombre_logico}")
    except Pyro5.errors.NamingError:
        print(f"Error: No se pudo encontrar el objeto '{nombre_logico}'.")
        print("Asegúrese de que el Servidor de Nombres y el servidor.py estén en ejecución.")
        sys.exit(1)

    print("Conectado al servidor de registro.")

    respuesta_registro = proxy_registro.registrar_nodo()
    print(f"Respuesta del servidor: {respuesta_registro}")

    nodos = proxy_registro.obtener_nodos_registrados()

    print("\n--- Nodos Registrados ---")
    if nodos:
        for i, ip in enumerate(nodos):
            print(f"{i+1}. {ip}")
    else:
        print("No hay nodos registrados aún (además de este).")
    print("-------------------------")

if __name__ == "__main__":
    main()
import Pyro5.api

ip = "10.15.0.51"

servidor = Pyro5.api.Proxy("PYRONAME:ServidorPalabras@" +ip)

while True:
    palabra = input("Escribe una palabra o ingrese 'salir': ").strip()
    if palabra.lower() == "salir":
        break
    resultado = servidor.enviar_palabra(palabra)
    if resultado:
        print("Palabras de otros clientes:\n" + resultado)
    else:
        print("Todavía no hay respuestas de otros clientes.")

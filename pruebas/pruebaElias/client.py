import Pyro5

uri_Servidor = input("Enter server URI: ")
server = Pyro5.Proxy(server_uri)

name = input("Enter your name: ")
print(server.join_game(name))

while True:
    answer = input("Enter your answer (or 'exit' to quit): ")
    if answer == 'exit':
        break
    print(server.submit_answer(name, answer))
    print("Current state:", server.get_state())

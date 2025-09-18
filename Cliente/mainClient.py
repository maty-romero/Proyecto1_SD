from Cliente.Modelos.GestorCliente import GestorCliente

if __name__ == "__main__":
    # Uso de gestorCliente Para Jugar
    gestor = GestorCliente()
    gestor.unirse_a_sala()
    
    """
    existe_partida = gestor.buscar_partida()
    if (existe_partida):
        gestor.ingresar_nickname_valido()
        gestor.unirse_a_sala()
        gestor.confirmar_jugador_partida()
    """
from Cliente.Modelos.GestorCliente import GestorCliente

if __name__ == "__main__":
    # Uso de gestorCliente Para Jugar
    gestor = GestorCliente()
    existe_partida = gestor.buscar_partida()
    if (existe_partida):
        #gestor.ingresar_nickname_valido()
        #gestor.logger.info("FINALIZO EL UNIRSE A SALA")
        #gestor.logger.info(gestor.Jugador_cliente)
        gestor.unirse_a_sala()
        gestor.confirmar_jugador_partida()
    
    """
    existe_partida = gestor.buscar_partida()
    if (existe_partida):
        gestor.ingresar_nickname_valido()
        gestor.unirse_a_sala()
        gestor.confirmar_jugador_partida()
    """
from Main.Server.Nodo import Nodo
from Main.Server import ConexionServidor
from Main.Server import GestorPartida

Interface IServicio (Notificaciones y Funcionalidad - Socket y/o Pyro)
    - existe_jugador(nickname) --> Verifica dentro del publisher
    - suscribir / registrar (Jugador) -> nickname, nombre_logico, ip, puerto, puntaje_total

interfcace IDataBase
    - CRUD? 


class NodoServidor
    - ConexionServidor
    - DBHandler: Interface
    - GestorPartida(IServicio: ConexionServidor, DBHandler)


class ConexionServidor implements IServicio
    - Uso Publisher
    - Uso ManejadorRPC y ManejadorSocket

    escucharCliente()
        manejadorSocket.blaball

class GestorPartida
    - uso de IServicio --> ejecucion metodos y notificaciones 

    service.existe_jugador()
    service.registrar_jugador(Jugador)
    service.notificar_info_ronda()

    unirse_partida()
        service.iniciar_conexion_sincronia()
    dbhandler.guardar_ronda()

    checkearClienteVivo()
        service.escucharCliente()


Cliente.hearbeart()



def __init__(self):
        self.gestor = GestorJuego()
        self.manejadores = [ManejadorRPC(self.gestor)]
        self.conexion = Conexion(self.manejadores)


class Servidor(Nodo):
    def __init__(self, id, Conexion = ConexionServidor(),Gestor= GestorPartida()):
        super().__init__(id)    
        self.Conexion = Conexion
        self.Gestor = Gestor(publisher=self.Conexion.Publisher,
                                      min_jugadores=min_jugadores)

        self.replicas = [] # un servidor posee varias replicas
    
    def registrar_replica(self, replica):
        self.replicas.append(replica)
        print(f"Replica {replica.id} registrada")

    def propagar_actualizacion(self, datos):
        self.actualizar_estado(datos)
        for replica in self.replicas:
            replica.actualizar_estado(datos)

    def consultar_bd(self, query):
        # Ejecuta una consulta en la base de datos
        pass

    def guardar_estado_en_bd(self):
        # Persiste el estado actual
        pass
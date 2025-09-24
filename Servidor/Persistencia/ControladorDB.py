"""
-Tienen que garantizarse puntos de guardado concretos, y completos.
    Por ej., en una conexion socket, solo se guardaran en esta los datos al llegar TODOS, sin faltantes.
-ver si guardar "jugadores"
-Opcional: Que python levante la aplicacion de MongoDB si no esta andando (ver subprocess)
    def mongo_responding(uri=MONGO_URI, timeout_s=2):   
    def start_systemd(service_name=SYSTEMD_SERVICE):
    def start_mongod_binary(dbpath=DBPATH, logpath=LOGPATH, port=27017, replset=None):
    def wait_for_mongo(timeout=WAIT_TIMEOUT, uri=MONGO_URI):
    def init_collections(uri=MONGO_URI):
    def ensure_mongo_up_and_ready():
    
Esqueleto bd:
PARTIDA:
{
  "codigo": 1,          // código de la partida
  "jugadores": ["Ana", "Luis"],
  "nro_ronda": 1,
  "categorias": ["Animal", "Ciudad", "Color"],
  "letra": "M",
  "respuestas": [
        { "jugador": "Ana", "Animal": "Mono", "Ciudad": "Madrid", "Color": "Marrón" },
        { "jugador": "Luis", "Animal": "Murciélago", "Ciudad": "Montevideo", "Color": "Magenta" }
    ]
}   

-PATRONES OPCIONALES:
    repository pattern -> https://www.mongodb.com/developer/how-to/implement-repository-pattern-python-mongodb/
        Abstrae la lógica de acceso a datos, facilitando migracion de base de datos.
    singleton pattern -> https://refactoring.guru/es/design-patterns/singleton/python/example
        Asegura que una clase tenga una única instancia y proporciona un punto de acceso global a ella.
        Útil para controladores de base de datos, ya que evita múltiples conexiones.    
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
class ControladorDB:

    def __init__(self, uri="mongodb://localhost:27017/", db_name="TuttiFruttiDB"):
        # Cambié a lista para poder usar append
        self.datosIniciales = []
        self.iniciar_db(uri, db_name)

    #puede renombrarse o dividir responsabilidades
    def iniciar_db(self, uri, db_name):
        self.conexiondb = MongoClient(uri)
        self.db = self.conexiondb[db_name]        # se crea sola si no existe
        self.partida = self.db["Partida"]           # lo mismo para la colección

        # Creamos un índice por código de partida (opcional, recomendado)
        self.partida.create_index("code", unique=True)

        # Si no hay partidas, insertamos una inicial
        if self.partida.count_documents({}) == 0:
            self.partida.insert_one(
                {
                "codigo": 1,          # código de la partida
                "jugadores": [],
                "nro_ronda": 0,
                "categorias": [],
                "letra": "",
                "respuestas": [
                        { }
                    ]
                }   
            )
            self.datosIniciales.append("Base creada con partida inicial ABCD")
        else:
            self.datosIniciales.append("Base ya tenía datos, no se insertó nada")

        # No cerramos la conexión por lo pronto
        # conexiondb.close()

    def desconectar(self):
        # Cierra la conexión
        self.conexiondb.close()
    
    """
    # --- Conexión ---
    def conectar(self):
        # Verifica la conexión
        return self.db.name

    # --- Partidas ---
    def crear_partida(self, datos):
        #Crea una nueva partida
        return self.db.partidas.insert_one(datos).inserted_id

    def obtener_partida(self, id_partida):
        #Obtiene una partida por ID
        return self.db.partidas.find_one({"_id": ObjectId(id_partida)})

    def actualizar_partida(self, id_partida, datos):
        #Actualiza datos de una partida
        return self.db.partidas.update_one(
            {"_id": ObjectId(id_partida)}, {"$set": datos}
        ).modified_count

    def eliminar_partida(self, id_partida):
        #Elimina una partida
        return self.db.partidas.delete_one({"_id": ObjectId(id_partida)}).deleted_count

    # --- Rondas ---
    def crear_ronda(self, id_partida, datos):
        #Crea una ronda asociada a una partida
        datos["id_partida"] = ObjectId(id_partida)
        return self.db.rondas.insert_one(datos).inserted_id

    def obtener_rondas_de_partida(self, id_partida):
        #Obtiene todas las rondas de una partida
        return list(self.db.rondas.find({"id_partida": ObjectId(id_partida)}))

    # --- Jugadores ---
    def agregar_jugador_a_ronda(self, id_ronda, datos):
        #Agrega un jugador a una ronda
        datos["id_ronda"] = ObjectId(id_ronda)
        return self.db.jugadores.insert_one(datos).inserted_id

    def obtener_jugadores_de_ronda(self, id_ronda):
        #Obtiene todos los jugadores de una ronda
        return list(self.db.jugadores.find({"id_ronda": ObjectId(id_ronda)}))

    # --- Utilitarios ---
    def ejecutar_consulta(self, coleccion, filtros=None):
        #Ejecutar consulta genérica en cualquier colección
        filtros = filtros or {}
        return list(self.db[coleccion].find(filtros))

    def existe(self, coleccion, filtros=None):
        #Verifica si existe al menos un documento que cumpla el filtro
        filtros = filtros or {}
        return self.db[coleccion].count_documents(filtros) > 0

    def contar(self, coleccion, filtros=None):
        #Cuenta documentos en una colección
        filtros = filtros or {}
        return self.db[coleccion].count_documents(filtros)
    """
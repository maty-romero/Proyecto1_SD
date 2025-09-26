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
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

"""Los Datos ya tienen que llegar formateados a la clase. No se pueden actualizar datos particulares,
    la clase esta diseñada para que llegue todo el conjunto de datos
"""
class ControladorDB:

    def __init__(self, uri="mongodb://localhost:27017/", db_name="TuttiFruttiDB",codigoPartida=1):
        self.uri= uri
        self.db_name = db_name      
        self.registroDatos = [] #lista para imprimir con informacion relevante
        self.codigo_partida = codigoPartida
        self.iniciar_db()

    #puede renombrarse o dividir responsabilidades
    def iniciar_db(self):
        try:
            self.conexiondb = MongoClient(self.uri)
            self.db = self.conexiondb[self.db_name]        # se crea sola si no existe
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
                self.registroDatos.append("[ControladorDB] Base creada con partida inicial ABCD")
            else:
                self.registroDatos.append("[ControladorDB] Base ya tenía datos, no se insertó nada")
        except errors.ServerSelectionTimeoutError as e:
            self.registroDatos.append(f"[ControladorDB] Error de conexión a MongoDB: {e}")
            self.conexiondb = None
            self.db = None

    def crear_partida(self, datos_partida):
        """Crea o reemplaza la partida con el código de self.codigo_partida"""
        datos_partida["codigo"] = self.codigo_partida
        resultado = self.partida.replace_one(
            {"codigo": self.codigo_partida},
            datos_partida,
            upsert=True
        )
        return resultado.upserted_id

    def obtener_partida(self):
        """Obtiene el documento de la partida actual"""
        return self.partida.find_one({"codigo": self.codigo_partida})

    def actualizar_partida(self, datos):
        """Actualiza parcialmente la partida actual"""
        return self.partida.update_one(
            {"codigo": self.codigo_partida},
            {"$set": datos}
        ).modified_count

    def eliminar_partida(self):
        """Elimina la partida actual"""
        return self.partida.delete_one({"codigo": self.codigo_partida}).deleted_count

    def desconectar(self):
        if self.conexiondb:
            self.conexiondb.close()
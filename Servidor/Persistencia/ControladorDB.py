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
    "clientes_Conectados": [
            {nickname: "pepito", ip: "0.0.0.0", puerto: "9090", uri: "PYRO:<nombre_logico>@<ip>:<puerto>" }
    ],
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
#from Servidor.Aplicacion.NodoReplica import NodoReplica
"""Los Datos ya tienen que llegar formateados a la clase. No se pueden actualizar datos particulares,
    la clase esta diseñada para que llegue todo el conjunto de datos
"""

from functools import wraps

def trigger_broadcast(func):
    """Decorador que desencadena broadcast después de actualizaciones exitosas"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        
        # Verificar si hubo modificación exitosa
        operacion_exitosa = False
        
        if isinstance(result, int) and result > 0:
            # Para métodos que retornan modified_count o deleted_count
            operacion_exitosa = True
        elif result is not None and not isinstance(result, int):
            # Para métodos que retornan objetos (insert_one retorna InsertOneResult)
            operacion_exitosa = True
        
        if operacion_exitosa:
            self.nodoReplica.broadcast_datos_DB()
        
        return result
    return wrapper

class ControladorDB:

    def __init__(self,nodoReplica, uri="mongodb://localhost:27017/", db_name="TuttiFruttiDB",codigoPartida=1):
        self.nodoReplica=nodoReplica #dejamos esta variable solo para poder invocar al broadcast
        self.uri= uri
        self.db_name = db_name      
        self.registroDatos = [] #lista para imprimir con informacion relevante
        self.codigo_partida = codigoPartida
        self.conexiondb = MongoClient(self.uri)
        self.db = self.conexiondb[self.db_name]        # se crea sola si no existe
        self.partida = self.db["Partida"]           # lo mismo para la colección

    #Inicia una partida nueva, este reemplaza el uso de eliminar partida
    def iniciar_nueva_partida(self):
        try:
            # Creamos un índice por código de partida (opcional, recomendado)
            # Si no hay partidas, insertamos una inicial
            self.partida.replace_one(
                {"codigo": 1},  # filtro: buscamos por código
                {
                    "codigo": 1,
                    "clientes_Conectados": [],
                    "estado_actual": "",
                    "letras_jugadas": "",
                    "nro_ronda": 0,
                    "categorias": ["Nombres", "Animales", "Colores", "Paises o ciudades", "Objetos"],
                    "letra": "",
                    "respuestas": [],
                    "timer_votacion": None
                },
                upsert=True  # si no existe, lo crea
            )
            self.registroDatos.append("[ControladorDB] Base creada con partida inicial ABCD")
        except errors.ServerSelectionTimeoutError as e:
            self.registroDatos.append(f"[ControladorDB] Error de conexión a MongoDB: {e}")
            self.conexiondb = None
            self.db = None

    # def crear_partida(self, datos_partida):
    #     """Crea o reemplaza la partida con el código de self.codigo_partida"""
    #     datos_partida["codigo"] = self.codigo_partida
    #     resultado = self.partida.replace_one(
    #         {"codigo": self.codigo_partida},
    #         datos_partida,
    #         upsert=True
    #     )
    #     return resultado.upserted_id

# #Prueba para crear partidas desde el ultimo codigo de partida
#     def crear_partida_prueba(self, datos_partida): 
#         #Busco ultimo codigo de partida, para crear una nueva a partir de esa
#         ultimo_codigo = self.getUltimoCodPartida()
#         self.codigo_partida = ultimo_codigo + 1 #Incremento a un nuevo codigo de partida para la nueva partida
#         datos_partida['codigo'] = self.codigo_partida
#         return self.partida.insert_one(datos_partida)

    def obtener_partida(self):
        """Obtiene el documento de la partida actual"""
        return self.partida.find_one({"codigo": self.codigo_partida})
    
    @trigger_broadcast
    def actualizar_partida(self, datos):
        """Actualiza parcialmente la partida actual"""
        return self.partida.update_one(
            {"codigo": self.codigo_partida},
            {"$set": datos}
        ).modified_count

    """El uso de esta es reemplazado por Iniciar()"""
    # @trigger_broadcast
    # def eliminar_partida(self):
    #     """Elimina la partida actual y la colección"""
    #     # Primero eliminar el/los documento(s)
    #     deleted_count = self.partida.delete_one({"codigo": self.codigo_partida}).deleted_count
        
    #     # Luego eliminar la colección completa
    #     self.partida.drop()
        
    #     self.registroDatos.append(f"[ControladorDB] Partida eliminada ({deleted_count} documentos). Colección eliminada.")
    #     return deleted_count
    def desconectar(self):
        if self.conexiondb:
            self.conexiondb.close()

    #METODOS PARA AGREGAR
    @trigger_broadcast
    def agregar_jugador(self, datos_cliente):
        """ Agrega un cliente y sus datos a la clave "clientes_conectados" """
        return self.partida.update_one({
            'codigo': self.codigo_partida
        }, {
            "$push": {
                "clientes_Conectados": datos_cliente
            }
        }).modified_count

    @trigger_broadcast
    def eliminar_jugador(self, nickname):
        """ Elimina un cliente y sus datos del arreglo "clientes_conectados" mediante la clave "nickname" """
        return self.partida.update_one({
            'codigo': self.codigo_partida
        }, {
            "$pull": {
                "clientes_Conectados": nickname
            }
        }).modified_count

    @trigger_broadcast
    def actualizar_letra(self, nueva_letra):
        """ Actualiza la letra de la partida """
        return self.partida.update_one(
            {'codigo': self.codigo_partida},
            {'$set': {'letra': nueva_letra}}
    ).modified_count

    @trigger_broadcast
    def actualizar_nro_ronda(self, nroRonda):
        """ Actualiza la ronda de la partida """
        return self.partida.update_one(
            {'codigo': self.codigo_partida},
            {'$set': {'nro_ronda': nroRonda}}
    ).modified_count

    @trigger_broadcast
    def actualizar_categorias(self, categorias):
        """ Actualiza las categorías de la partida """
        return self.partida.update_one(
            {'codigo': self.codigo_partida},
            {'$set': {'categorias': categorias}}
    ).modified_count

    def getClientesConectadosRonda(self, rondaAnterior):
        """ Devuelve los clientes conectados de la ronda anterior """
        doc = self.partida.find_one(
            {"codigo": self.codigo_partida, "nro_ronda": rondaAnterior},
            {"_id": 0, "clientes_Conectados": 1}
        )
        
        clientes = doc['clientes_Conectados']
        return clientes

    @trigger_broadcast
    def insertarNuevaRonda(self, nuevaRonda):
        """ Inserta una nueva ronda en la partida """
        nuevaRonda['codigo'] = self.codigo_partida
        return self.partida.insert_one(nuevaRonda)

    """ # Reemplazado por 'reemplazar_respuestas_ronda' 
    def actualizarRespuestasRonda(self, nroRonda, respuestas):
        # Actualiza las respuestas de la partida 
        return self.partida.update_one(
            {"codigo": self.codigo_partida, "nro_ronda": nroRonda},
            {"$push": {"respuestas": respuestas }}
        ).modified_count
    """

    # respuestas_clientes no formateado --> Viene de ServicioJuego.enviar_respuestas_ronda
    def _safe_key(self, key: str) -> str:
        # Normaliza claves: reemplaza espacios, puntos y $ por '_'
        return key.replace(".", "_").replace("$", "_").replace(" ", "_")
    # Nuevo actualizarRespuestasRonda
    @trigger_broadcast
    def reemplazar_respuestas_ronda(self, nroRonda, respuestas_clientes: dict):
        """ 
        Construye un dict con todas las respuestas por nickname (normalizando
        las claves internas de categoría) y hace $set de 'respuestas' completo.
        """
        new_respuestas = {}
        for key, cliente_info in respuestas_clientes.items():
            nickname = cliente_info.get("nickname", key)
            safe_nick = self._safe_key(nickname)  # si querés normalizar nick también
            respuestas_originales = cliente_info.get("respuestas", {})

            # normalizar las claves internas de categoria
            respuestas_normalizadas = {
                self._safe_key(categoria): valor
                for categoria, valor in respuestas_originales.items()
            }

            new_respuestas[safe_nick] = respuestas_normalizadas

        result = self.partida.update_one(
            {"codigo": self.codigo_partida, "nro_ronda": nroRonda},
            {"$set": {"respuestas": new_respuestas}}
        )
       
        return result.modified_count


    def getUltimoCodPartida(self):
        """ Devuelve el ultimo codigo de partida """
        ultimo = self.partida.find_one(
            {}, #Sin filtro
            sort = [("codigo", -1)], #Me los ordena descendente: De MAYOR a MENOR
            projection = {"_id": 0, "codigo": 1}
        )
        return ultimo["codigo"]

    # MÉTODOS PARA RESTAURAR DATOS DESDE LA BD
    def obtener_datos_partida_completos(self):
        """Obtiene todos los datos de la partida actual para restauración"""
        return self.partida.find_one(
            {"codigo": self.codigo_partida},
            {"_id": 0}  # Excluir el _id de MongoDB
        )

    def obtener_todas_las_rondas(self):
        """Obtiene todas las rondas de la partida actual ordenadas por número de ronda"""
        return list(self.partida.find(
            {"codigo": self.codigo_partida, "nro_ronda": {"$gt": 0}},
            {"_id": 0}
        ).sort("nro_ronda", 1))

    def obtener_jugadores_conectados(self):
        """Obtiene la lista de jugadores conectados"""
        partida_data = self.partida.find_one(
            {"codigo": self.codigo_partida},
            {"_id": 0, "clientes_Conectados": 1}
        )
        return partida_data.get("clientes_Conectados", []) if partida_data else []

    # def obtener_respuestas_ronda_actual(self):
    #     """Obtiene las respuestas de la ronda actual desde BD para restauración"""
    #     try:
    #         partida_data = self.partida.find_one(
    #             {"codigo": self.codigo_partida},
    #             {"_id": 0, "nro_ronda": 1, "respuestas": 1}
    #         )
            
    #         if partida_data and partida_data.get("respuestas"):
    #             self.registroDatos.append(f"[ControladorDB] Respuestas de ronda {partida_data.get('nro_ronda')} obtenidas desde BD")
    #             return partida_data["respuestas"]
    #         else:
    #             self.registroDatos.append("[ControladorDB] No hay respuestas guardadas en BD")
    #             return {}
                
    #     except Exception as e:
    #         self.registroDatos.append(f"[ControladorDB] Error obteniendo respuestas desde BD: {e}")
    #         return {}

    def get_controlador(self):
        """Devuelve la instancia del controlador (para acceso desde dispatcher)"""
        return self

    @trigger_broadcast
    def actualizar_estado_partida(self, estado_enum):
        """Actualiza el estado de la partida convirtiendo el Enum a string"""
        estado_str = estado_enum.name  # Convierte EstadoJuego.EN_SALA a "EN_SALA"
        return self.partida.update_one(
            {'codigo': self.codigo_partida},
            {'$set': {'estado_actual': estado_str}}
        ).modified_count

    @trigger_broadcast
    def actualizar_letras_jugadas(self, letras_jugadas):
        """Actualiza las letras jugadas en la partida"""
        return self.partida.update_one(
            {'codigo': self.codigo_partida},
            {'$set': {'letras_jugadas': letras_jugadas}}
        ).modified_count

    @trigger_broadcast
    def actualizar_puntajes_jugadores(self, puntajes_dict):
        """Actualiza los puntajes de los jugadores en la partida"""
        modificados = 0
        for nickname, puntaje in puntajes_dict.items():
            resultado = self.partida.update_one(
                {
                    "codigo": self.codigo_partida,
                    "clientes_Conectados.nickname": nickname
                },
                {
                    "$set": {"clientes_Conectados.$.puntaje_total": puntaje}
                }
            )
            modificados += resultado.modified_count
        return modificados

    def obtener_clientes_conectados(self):
        """Obtiene todos los clientes conectados desde BD"""
        try:
            partida = self.partida.find_one({"codigo": self.codigo_partida})
            if partida and "clientes_Conectados" in partida:
                return partida["clientes_Conectados"]
            return []
        except Exception as e:
            print(f"Error obteniendo clientes conectados: {e}")
            return []

    # def existe_partida_previa(self) -> bool:
    #     """
    #     Verifica si la colección 'Partida' ya existe en la base de datos.
    #     Devuelve True si existe (ya hubo partidas previas), False en caso contrario.
    #     """
    #     if self.db is None:
    #         self.registroDatos.append("[ControladorDB] No hay conexión activa a la base de datos")
    #         return False

    #     existe = "Partida" in self.db.list_collection_names()
    #     if existe:
    #         self.registroDatos.append("[ControladorDB] Ya existe colección 'Partida'")
    #     else:
    #         self.registroDatos.append("[ControladorDB] No existe colección 'Partida'")
    #     return existe

    def existe_partida_previa(self) -> bool:
        """
        Verifica si hay datos previos en la partida consultando el estado_actual.
        Devuelve True si el estado NO está vacío (hay datos previos), False si está vacío o no existe.
        """
        if self.db is None:
            self.registroDatos.append("[ControladorDB] No hay conexión activa a la base de datos")
            return False

        try:
            partida_data = self.partida.find_one(
                {"codigo": self.codigo_partida},
                {"_id": 0, "estado_actual": 1}
            )
            
            if partida_data is None:
                self.registroDatos.append(f"[ControladorDB] No existe partida con código {self.codigo_partida}")
                return False
            
            estado_actual = partida_data.get("estado_actual", "")
            
            if estado_actual == "" or estado_actual is None:
                self.registroDatos.append(f"[ControladorDB] Partida {self.codigo_partida} no tiene datos previos (estado vacío)")
                return False
            else:
                self.registroDatos.append(f"[ControladorDB] Partida {self.codigo_partida} tiene datos previos (estado: {estado_actual})")
                return True
                
        except Exception as e:
            self.registroDatos.append(f"[ControladorDB] Error consultando estado de partida: {e}")
            return False

    # ---------------- Métodos para Timer de Votación ----------------
    @trigger_broadcast
    def actualizar_timer_votacion(self, tiempo_restante: int):
        """Actualiza el tiempo restante del timer de votación en BD"""
        try:
            result = self.partida.update_one(
                {"codigo": self.codigo_partida},
                {"$set": {"timer_votacion": tiempo_restante}}
            )
            if result.modified_count > 0:
                self.registroDatos.append(f"[ControladorDB] Timer votación actualizado: {tiempo_restante}s")
            return result.modified_count
        except Exception as e:
            self.registroDatos.append(f"[ControladorDB] Error actualizando timer votación: {e}")
            return 0

    def obtener_timer_votacion(self) -> int:
        """Obtiene el tiempo restante del timer de votación desde BD"""
        try:
            partida_data = self.partida.find_one(
                {"codigo": self.codigo_partida},
                {"_id": 0, "timer_votacion": 1}
            )
            
            if partida_data and "timer_votacion" in partida_data:
                tiempo = partida_data["timer_votacion"]
                self.registroDatos.append(f"[ControladorDB] Timer votación obtenido: {tiempo}s")
                return tiempo
            else:
                self.registroDatos.append("[ControladorDB] No hay timer de votación activo")
                return 0
                
        except Exception as e:
            self.registroDatos.append(f"[ControladorDB] Error obteniendo timer votación: {e}")
            return 0
    @trigger_broadcast
    def limpiar_timer_votacion(self):
        """Elimina el timer de votación de BD (cuando termina o se cancela)"""
        try:
            result = self.partida.update_one(
                {"codigo": self.codigo_partida},
                {"$unset": {"timer_votacion": ""}}
            )
            if result.modified_count > 0:
                self.registroDatos.append("[ControladorDB] Timer votación limpiado de BD")
            return result.modified_count
        except Exception as e:
            self.registroDatos.append(f"[ControladorDB] Error limpiando timer votación: {e}")
            return 0
    
    def obtener_estado_actual(self):
        """Obtiene el estado actual de la partida"""
        try:
            partida = self.partida.find_one({"codigo": self.codigo_partida})
            
            if partida:
                return partida.get("estado_actual", "")
            else:
                self.logger.warning("[ControladorDB] No se encontró la partida")
                return None
                
        except Exception as e:
            self.logger.error(f"[ControladorDB] Error al obtener estado_actual: {e}")
            return None
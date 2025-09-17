"""
from pymongo import MongoClient
from bson.objectid import ObjectId
"""

class ControladorDB:
    pass
    """
    def __init__(self, uri="mongodb://localhost:27017/", db_name="juego"):
        self.cliente = MongoClient(uri)
        self.db = self.cliente[db_name]

    # --- Conexión ---
    def conectar(self):
        # Verifica la conexión
        return self.db.name

    def desconectar(self):
        # Cierra la conexión
        self.cliente.close()

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
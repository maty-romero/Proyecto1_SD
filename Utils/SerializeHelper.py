import json
class SerializeHelper:

    """
    formato json:
    {
        “exito”: True || False
        “msg”: Msg_exito || Msg_error
        “datos”: datos || { } (vacio)
    }
    """

    @staticmethod
    def serializar(exito: bool, msg: str, datos = {}):
        """Serializa un mensaje en formato JSON."""
        return json.dumps({
            "exito": exito,
            "msg": msg,
            "datos": datos
        }).encode()

    @staticmethod
    def deserializar(raw_bytes):
        """Deserializa un mensaje desde JSON."""
        if isinstance(raw_bytes, bytes):
            obj = json.loads(raw_bytes.decode())
        elif isinstance(raw_bytes, str):
            obj = json.loads(raw_bytes)
        else:
            raise TypeError("Tipo de mensaje no soportado para deserializar")
        return obj["exito"], obj["msg"], obj["datos"]

    @staticmethod
    def respuesta(exito: bool, msg: str, datos=None) -> dict:
        """Devuelve una respuesta estandarizada como dict."""
        if datos is None:
            datos = {}
        return {
            "exito": exito,
            "msg": msg,
            "datos": datos
        }


    """
        raw = Mensaje.serializar(True, "Conexión establecida", {"ip": "127.0.0.1", "puerto": 8080})
        print(raw)  
        # b'{"exito": true, "msg": "Conexi\\u00f3n establecida", "datos": {"ip": "127.0.0.1", "puerto": 8080}}'
        
        # Deserializar
        exito, msg, datos = Mensaje.deserializar(raw)
        print(exito)  # True
        print(msg)    # "Conexión establecida"
        print(datos)  # {"ip": "127.0.0.1", "puerto": 8080}
    """

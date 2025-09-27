import json
class SerializeHelper:

    @staticmethod
    def serializar():
        def serializar(tipo, data):
            """Serializa un mensaje en formato JSON."""
            return json.dumps({"tipo": tipo, "data": data}).encode()

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
    
   
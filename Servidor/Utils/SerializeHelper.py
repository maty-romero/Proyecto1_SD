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
        obj = json.loads(raw_bytes.decode())
        return obj["tipo"], obj["data"]

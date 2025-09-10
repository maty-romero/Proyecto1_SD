import json

class RespuestaRemotaJSON:
    def __init__(self, exito=True, mensaje="", datos=None):
        self.exito = exito
        self.mensaje = mensaje
        self.datos = datos or {}

    def to_dict(self):
        return {
            "exito": self.exito,
            "mensaje": self.mensaje,
            "datos": self.datos
        }

    def serializar(self):
        return json.dumps(self.to_dict())

    @classmethod
    def deserializar(cls, json_str):
        try:
            data = json.loads(json_str)
            return cls(
                exito=data["exito"],
                mensaje=data.get("mensaje", ""),
                datos=data.get("datos", {})
            )
        except (json.JSONDecodeError, KeyError) as e:
            return cls(
                exito=False,
                mensaje=f"Respuesta inválida: {str(e)}",
                datos={}
            )
from Servidor.Comunicacion.ManejadorSocket import ManejadorSocket
from Servidor.Comunicacion.ServicioComunicacion import ServicioComunicacion
from Servidor.Utils.ComunicationHelper import ComunicationHelper

servicioCom = ServicioComunicacion()

# abrir conexion y esperar cliente
# cliente recibe datos conexion y se conecta
# servidor envia mensaje
# cliente envia mensaje
# cliente se desconecta
# --> Manejo de multiples clientes conectados

ip_host = ComunicationHelper.obtener_ip_local()

manSocket = ManejadorSocket(host=ComunicationHelper.obtener_ip_local(), puerto="")
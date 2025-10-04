# Proyecto1 Comunicacion Directa - TutiFruti

## Integrantes
- Matias Romero
- Elias Magallanes
- Jeremias Regina
- Fiorella Valdez
- Dayana Laime

## Instalación y ejecución

Requisitos:
- Windows 10/11
- Python 3.10+ instalado

## Instalación
1. Clonar o descargar este repositorio.
2. Abrir PowerShell en la carpeta del proyecto y ejecutar:

### Dependencias 
Estando en el directorio del proyecto ejecute los siguientes comandos: 

$ pip install -r Servidor/requirements.txt

$ pip install -r Cliente/requirements.txt

## Ejecucion
Ejecución - Debera ejecutar los archivos .bat a continuacion: 

Para iniciar el servidor de nombres (NS), ejecute: 
/init/runNameServer.bat 

Para iniciar una sola replica, ejecute: 
/init/runReplicaSola.bat  

O bien puede ejecutar 5 replicas ejecutando: 
/init/run5Replicas.bat 

Para iniciar el cliente, ejecutar:
/init/runCliente.bat

- Iniciar en orden los archivos .bat -> runNameServer -> run5Replicas
- De elegir utilizar distintas terminales, verificar ip privada en la red, y bajar firewall, 
    y ejecutar en simultaneo en las terminales el .bat runReplicaSola
- Ejecutar el runCliente para todos los clientes que quieran jugar 

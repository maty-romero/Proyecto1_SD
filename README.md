# Proyecto1 Sistema Distribuido - TutiFruti

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

### Dependencias 
Estando en el directorio del proyecto ejecute los siguientes comandos: 

$ pip install -r Servidor/requirements.txt
$ pip install -r Sliente/requirements.txt

## Instalación
1. Clonar o descargar este repositorio.
2. Entrar a la carpeta init
3. Ejecutar archivos bat

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

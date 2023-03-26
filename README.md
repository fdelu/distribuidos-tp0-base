# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un ejemplo de cliente-servidor el cual corre en containers con la ayuda de [docker-compose](https://docs.docker.com/compose/). El mismo es un ejemplo práctico brindado por la cátedra para que los alumnos tengan un esqueleto básico de cómo armar un proyecto de cero en donde todas las dependencias del mismo se encuentren encapsuladas en containers. El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers.

Por otro lado, se presenta una guía de ejercicios que los alumnos deberán resolver teniendo en cuenta las consideraciones generales descriptas al pie de este archivo.

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que posee encapsulado diferentes comandos utilizados recurrentemente en el proyecto en forma de targets. Los targets se ejecutan mediante la invocación de:

* **make \<target\>**:
Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de _debugging_ y _troubleshooting_.

Los targets disponibles son:
* **docker-compose-up**: Inicializa el ambiente de desarrollo (buildear docker images del servidor y cliente, inicializar la red a utilizar por docker, etc.) y arranca los containers de las aplicaciones que componen el proyecto.
* **docker-compose-down**: Realiza un `docker-compose stop` para detener los containers asociados al compose y luego realiza un `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene.
* **docker-compose-logs**: Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose.
* **docker-image**: Buildea las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para testear nuevos cambios en las imágenes antes de arrancar el proyecto.
* **build**: Compila la aplicación cliente para ejecución en el _host_ en lugar de en docker. La compilación de esta forma es mucho más rápida pero requiere tener el entorno de Golang instalado en la máquina _host_.

### Servidor
El servidor del presente ejemplo es un EchoServer: los mensajes recibidos por el cliente son devueltos inmediatamente. El servidor actual funciona de la siguiente forma:
1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor procede a recibir una conexión nuevamente.

### Cliente
El cliente del presente ejemplo se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma.
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
recibe mensaje del cliente y procede a responder el mismo.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
Servidor desconecta al cliente.
4. Cliente vuelve al paso 2.

Al ejecutar el comando `make docker-compose-up` para comenzar la ejecución del ejemplo y luego el comando `make docker-compose-logs`, se observan los siguientes logs:

```
$ make docker-compose-logs
docker compose -f docker-compose-dev.yaml logs -f
client1  | time="2023-03-17 04:36:59" level=info msg="action: config | result: success | client_id: 1 | server_address: server:12345 | loop_lapse: 20s | loop_period: 5s | log_level: DEBUG"
client1  | time="2023-03-17 04:36:59" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1\n"
server   | 2023-03-17 04:36:59 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: in_progress
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:36:59 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2023-03-17 04:36:59 INFO     action: accept_connections | result: in_progress
server   | 2023-03-17 04:37:04 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:04 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2023-03-17 04:37:04 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:04" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2\n"
server   | 2023-03-17 04:37:09 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:09 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
server   | 2023-03-17 04:37:09 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:09" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3\n"
server   | 2023-03-17 04:37:14 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2023-03-17 04:37:14 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
client1  | time="2023-03-17 04:37:14" level=info msg="action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4\n"
server   | 2023-03-17 04:37:14 INFO     action: accept_connections | result: in_progress
client1  | time="2023-03-17 04:37:19" level=info msg="action: timeout_detected | result: success | client_id: 1"
client1  | time="2023-03-17 04:37:19" level=info msg="action: loop_finished | result: success | client_id: 1"
client1 exited with code 0
```

## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Modificar la definición del DockerCompose para agregar un nuevo cliente al proyecto.

### Ejercicio N°1.1:
Definir un script (en el lenguaje deseado) que permita crear una definición de DockerCompose con una cantidad configurable de clientes.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera un nuevo build de las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida afuera de la imagen (hint: `docker volumes`).

### Ejercicio N°3:
Crear un script que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un EchoServer, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado. Netcat no debe ser instalado en la máquina _host_ y no se puede exponer puertos del servidor para realizar la comunicación (hint: `docker network`).

### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base al código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).
* Límite máximo de paquete de 8kB.

### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento. La cantidad de apuestas dentro de cada _batch_ debe ser configurable.
El servidor, por otro lado, deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:
Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo, no podrá responder consultas por la lista de ganadores.
Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

## Parte 3: Repaso de Concurrencia

### Ejercicio N°8:
Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo.
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

En caso de que el alumno implemente el servidor Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Consideraciones Generales
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios.
El _fork_ deberá contar con una sección de README que indique como ejecutar cada ejercicio.
La Parte 2 requiere una sección donde se explique el protocolo de comunicación implementado.
La Parte 3 requiere una sección que expliquen los mecanismos de sincronización utilizados.

Finalmente, se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección provistos [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).

# Entrega

## Parte 1

### Ejercicio 1

Se puede ejecutar `make docker-compose-up` y luego `make docker-compose-logs`. De esta manera se visualizará en los logs el correcto funcionamiento del segundo cliente.

### Ejercicio 1.1

Ejecutar, por ejemplo, `python3 compose_generator/generate.py docker-compose-dev.yaml 5`. Esto va a crear un docker compose sobreescribiendo el actual, con 5 clientes. 

### Funcionamiento del script
Se parte del archivo llamado `docker-compose-base.yaml` en la carpeta `compose_generator`. Todo el contenido entre los comentarios `# replicate-start 1` y `# replicate-end` se va a replicar. Los comentarios del tipo `# [variable]=index` reemplazan en la siguiente línea la variable por el índice de replicación (si se pone `# ID=index`, `clienteID` se transforma en `cliente1`, `cliente2`, `cliente3`, etc). 

Se puede replicar más de una sección. Cada sección debe comenzar con `# replicate-start [id]`, y al ejecutar el comando se pasa la cantidad de veces a replicar cada sección: `python3 compose_generator/generate.py [archivo_destino] [n_1] [n_2] [n_3] ...` donde `n_[x]` es la cantidad de veces a replicar la sección con `[id]`=`x`.

El script funciona utilizando expresiones regulares en Python.

### Ejercicio 2

Para que los containers accedan a los archivos de configuración ahora se utiliza un [bind mount](https://docs.docker.com/storage/bind-mounts/). Se puede ejecutar el comando `make docker-compose-up` y al cambiar los archivos de configuración no requerirá una nueva build.

### Ejercicio 3

Para realizar esta prueba, agregué al `docker-compose-dev.yaml` un nuevo container con la configuración para ejecutar el el script de prueba, que se encuentra en el archivo `test_server.sh`. Este solo se crea utilizando el profile `test_server`.

Para correr la prueba, ejecutar `make test_server`. Esto creará el container, lo ejecutará, imprimirá los resultados y limpiará los recursos utilizados.

### Ejercicio 4

Para terminar la ejecución de manera graceful, agregué a los loops tanto del cliente como del servidor un handler para la señal `SIGTERM`. De esta manera, cuando se envía la señal, el loop finaliza y el programa termina correctamente. El servidor también cierra el listener TCP cuando se apaga.

Para este ejercicio también resolví los TODO del código provisto que no contemplaban los short-read ni short-write.

## Parte 2

### Ejercicio 5

Se modificó el código del cliente y del servidor para enviar apuestas. El protocolo de comunicación es muy sencillo: tanto cliente como servidor tienen una clase/tipo `Client` que envía o recibe mensajes, asegurandose de no hacer short-reads o short-writes. Un mensaje no es más que un string. Para enviarlos, los mensajes se codifican o decodifican en UTF-8 y se le agrega un header de 2 bytes con la cantidad de bytes del mensaje (sin incluir el header). Para enviar las apuestas, se utilizó este cliente enviando la información como un string que contiene un JSON que la representa.

Se puede probar que se estan almacenando las apuestas utilizando `make docker-compuse-up` y `make docker-compose-logs`. También, con el servidor abierto, se puede ejecutar `docker exec -it $(docker ps -f name=server -q) /bin/bash` para abrir una terminal en el contenedor y utilizar `cat bets.csv` para ver el archivo con las apuestas.

### Ejercicio 6

A la hora de buildear las imágenes desde el Makefile, agregué un unzip de los datasets que se agregan a cada cliente como un volumen en `/bets.csv`. Los clientes leen y envian 20 apuestas del archivo por cada batch (configurable en `client/config.yaml`, aunque no se puede agrandar mucho por el límite de los 8kB).

También se modificó un poco el protocolo de comunicación. Ahora se envían JSONs del tipo `{"type": "string", "payload": "any"}` donde según el string que haya en `type` se define el contenido del `payload`. Por ahora solo hay 2 tipos: `submit` (mensajes cliente->servidor donde el payload es una lista de apuestas) y `submit_result` (mensaje servidor->cliente donde el payload es un string confirmando el procesamiento de las apuestas). Para más información, ver la sección siguiente.


### Ejercicio 7

Se agregaron dos nuevos mensajes: `get_winners` y `winners`. A continuación detalles sobre el protocolo final implementado:

* **Mensajes**: Se implementó una capa inferior que utiliza los sockets, que es capaz de enviar mensajes como strings. Esta capa agrega un header de 2 bytes delante del mensaje que indica el largo de este. 
  Entre el servidor y los clientes, se utiliza esa capa para enviar mensajes codificados como un JSON con dos atributos: `type` y `payload`. Hay 4 tipos de mensajes:
  - `submit`: El cliente envía este mensaje al servidor con una lista de apuestas a agregar. El payload de este mensaje es una lista de objetos de apuestas, cuyos atributos son la información de cada una de ellas: `agency`, `first_name`, `last_name`, `document`, `birthdate`, `number`.
  - `submit_result`: Es la respuesta del servidor al mensaje anterior. Si el servidor proceso las respuestas exitosamente, se espera este mensaje con un `"OK"` en su payload.
  - `get_winners`: Se envía por el cliente cuando terminó de agregar apuestas, solicitándole al servidor que responda con los ganadores. No tiene payload.
  - `winners`: Es la respuesta del servidor al mensaje anterior. El payload de este mensaje es una lista de strings, donde cada uno de esos strings es un DNI de una apuesta ganadora de la agencia a la que se le esta enviándo el mensaje.
* **Diagrama**: En [este enlace](https://viewer.diagrams.net/index.html?tags=%7B%7D&highlight=0000ff&edit=_blank&layers=1&nav=1&title=ProtocoloDistribuidos#R7VlBc6IwGP01HrcDBFGOldbuobuzMxz22IkmhbSROCFU7a%2FfIEEgwdY6yJYZe%2BjASwLJ9977kg9HIFhtHzhcx78YwnTkWGg7Ancjx%2FHBVP7PgV0BjIFbABEnqIDsCgjJO1agpdCMIJw2OgrGqCDrJrhkSYKXooFBztmm2e2Z0eZb1zDCBhAuITXRvwSJuECnzqTCf2ISxeWbbc8vWlaw7KxWksYQsU0NAvcjEHDGRHG12gaY5rEr41KMmx9pPUyM40ScMsDKZo9hiGYOcMKXeZoEd6%2FpD6DmJnblgjGS61e3jIuYRSyB9L5CZ5xlCcL5Uy15V%2FV5ZGwtQVuCL1iInSITZoJJKBYrqlpxgm5zauTtkrM0LaA5oVQ901yaWm3KMr7EH6xH9csXURuoAvKA2QoLvpMdOKZQkLcmyVBpJTr0Owz9w4icimMpWTuuIrVUdUly%2BQgBeYSFGlWRIi9q06igPVVfoE1N%2BA3STC0hoEQGC0vwt0Fpk7BNTAQO13Afx400bZOcZ5aIkv8WjZVvxlzg7YchLkNlNUN18MOmZicFxTUnudZxUhrh%2FGrs3P8h%2BfMV7fSjaHeqKdruV9GOoegQ8zeCGP9ecnbdbybnsRE4U9%2B1fEthmpJlM0bNgD7LPBwwKgOfDwZLhBfThcRTwdkrrrVYlu9bH6brT0VbC9q4JWgl1nG2dnyNjMKEhrY%2FNQmw%2BjWJZ3CdZosVEQbjUsyiyTGkJEpyAeS7hCRwlkueyHPOrWpYEYSKXIdT8g4X%2B0fl7K7z1ezXN56Nxnf5s2R6S4tMZxvCSFiCNRWVkLRim3y6tigAGt0T06Jei9rApSw66dyieiQtKwgGYETDP%2Fqx6VQj6o4GOncXNuL0iBGfpHkyOlQ%2FKhV17kfbbc%2BaNdHZVp%2BGLM82103z9E0T6CeYszfNcb9etc2j5TX9Fkx4XaXfSc%2BUugalNzc3I8ejeZZdyJLBi%2FKrPTiUVNxpynU9zXOekXJBi9AuVqXY1zLl6xm3qzLF7blMsc065Zpxi3v9q8q5Gdft%2B4Nj9zXMqf6dz4H8GwDZBkf6Qeds%2F%2Br79KXJNssb%2BbqnDUkSzNPh7KhtIuq%2BuBk3uSq31Zrm%2FBbNXa628ftKvq1Onc8H4FTDYNOu0rK%2BZV%2F6q7lZyA7dpXsBde5SR3OpZ7p00o1L5W31m27Bc%2FXDOLj%2FBw%3D%3D) hay un pequeño diagrama con la secuencia de mensajes entre un cliente cualquiera y el servidor.

## Parte 2

### Ejercicio 8

Se agregó el procesamiento en paralelo de los clientes por medio de pools the procesos. Hay 2 fases principales, cada una con su pool:

1. **Obtención de las apuestas**: a medida que se van obteniendo conexiones por el listener, se agrega una tarea a la pool que recibe todas las apuestas y las guarda.
2. **Envío de ganadores**: una vez se obtuvieron todas las apuestas, se obtienen los ganadores desde el proceso principal. Luego, se agrega una tarea a la pool para cada cliente donde este filtra las tareas que son de su agencia y se las envía al cliente.

La arquitectura utilizada se asemeja bastante al modelo fork-join, ya que para ambas partes se ejecutan en paralelo tareas (casi) independientes y luego se juntan los resultados.

### Mecanismos de sincronización
Como las tareas en la pool de procesos son casi independientes, los mecanismos de sincronización son casi nulos. Hay un lock global para el archivo de apuestas que se obtiene al ejecutar la función. `store_bets` desde cada proceso. Para el `load_bets` es innecesario ya que se lee solo del proceso principal.

La única información que se envía entre los procesos es la que se envía inicialmente al crear la tarea en la pool o la que se retorna al finalizar, además de la almacenada con las funciones provistas.
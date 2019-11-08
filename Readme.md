# Tarea III: Timbiriche :school_satchel:

## Consideraciones generales :octocat:

El programa consta de una interfaz servidor cliente que puede loggear personas
guardar sus fotos de perfil, aplicarles un filtro dibujo, iniciar salas de espera
para jugar y abre un chat en el que se  comunican todos los que están en la sala
de espera, donde el jefe puede iniciarla, y esta se actualiza si los miembros
se salen.
Puede iniciarce el juego, mostrar el contador de tiempo pero el juego no fue
implementado.

Para ejecutar esta tarea se debe ejecutar el main de servidor y luego el de cliente
en el servidor es importante nunca borrar en la base de datos el jugador de nombre
'empty'.

La verdad es que mi tarea la probé de diferentes formas y no se caia, asique supongo que no debería caerse.

### Cosas implementadas y no implementadas :white_check_mark: :x:

* Parte <Manejo de bytes<sub>1</sub>>: Hecha completa
* Parte <Manejo de bytes<sub>2</sub>>: Hecha completa
              (si recibe RGB +alpha lo transforma en RGB)[asumí que es valido]
* Parte <Manejo de bytes<sub>3</sub>>: Hecha completa

* Parte <Networking<sub>1</sub>>: Hecha completa
* Parte <Networking<sub>2</sub>>: Hecha completa
* Parte <Networking<sub>3</sub>>: Hecha completa
* Parte <Networking<sub>4</sub>>: Hecha completa
* Parte <Networking<sub>5.1</sub>>: Hecha completa
* Parte <Networking<sub>5.2</sub>>: Hecha completa
* Parte <Networking<sub>5.3</sub>>: Hecha completa

* Parte <Funcionalidad/Autenticacion<sub>1</sub>>: Hecha completa(sin la parte del juego)
* Parte <Funcionalidad/Ventana de Salas<sub>2</sub>>: Hecha completa
* Parte <Funcionalidad/Ventana de Salas<sub>3</sub>>: Hecha completa
* Parte <Funcionalidad/Ventana de Salas<sub>4</sub>>: Hecha completa(se asume que nombre
                                                      descriptivo puede ser un numero)
* Parte <Funcionalidad/Sala Espera de Salas<sub>5</sub>>: Hecha completa
* Parte <Funcionalidad/Chat<sub>6</sub>>: Hecha completa
* Parte <Funcionalidad/Chat<sub>7</sub>>: Hecha completa
* Parte <Funcionalidad/Partida<sub>8</sub>>: Hecha en parte(muestra los puntajes
          que no pueden ser actualizados ya que los jugadore no pueden ganar puntos)
* Parte <Funcionalidad/Partida<sub>9</sub>>: Solo se muestra el tablero de
                                        NxM y no se actualiza
* Parte <Funcionalidad/Partida<sub>10</sub>>: No implementada
* Parte <Funcionalidad/Partida<sub>11</sub>>: No implementada
* Parte <Funcionalidad/Partida<sub>12</sub>>: No implementada
* Parte <Funcionalidad/General<sub>13</sub>>: Se manejan multiples chats, partidas no
* Parte <Funcionalidad/Partida<sub>14</sub>>: Funciona con el chat, si existíera juego sería igual
Aunque no se puede salir del juego por medio

* Parte <General<sub>1</sub>>: No implementada (no sabía que había que hacer eso :sad:)
* Parte <General<sub>2</sub>>: Hecha completa

Para resumir los bonus que hice fueron
* Parte <Bonus/contraeña<sub>4</sub>>: Hecha completa
* Parte <Bonus/Servidor y Cliente Robusto<sub>5</sub>>: Hecha completa
        (asumí que cerrar todo e imprimir en la consola bastaba, ya que se maneja el error
          aunque ahora que lo pienso imagino que había que hacer algo en interfaz?)

## Ejecución :computer:
El módulo principal de la tarea a ejecutar es  ```main.py``` en la carpeta servidor
y ```main.py``` en la carpeta cliente, se debe ejecutar primero el servidor.


## Librerías :books:
### Librerías externas utilizadas
La lista de librerías externas que utilicé fue la siguiente:


1. ```PyQt5```-> De esta se heredaron los modulos: QtWidgets, QtCore, QtGui, uic y Qt.
Y de estos
se heredó especificamente.
QtWidgets -> QLabel, QMainWindow, QApplication,  QLineEdit, QHBoxLayout, QVBoxLayout,  QPushButton, QScrollArea,  QLineEdit, QFileDialog.

QtCore -> QThread, pyqtSignal, QTimer, Qt.
QtGui -> QPixmap, QTextCursor, QIcon, QColor,  QTransform, QFont.

Qt -> QColor

Esta se utilizó como interfáz gráfica (debe instalarse)

2. ```sys```-> ```exit()```
3. ```threading```-> ```Lock())```
4. ```socket```-> ```socket()``` parametros ```AF_INET``` ```SOCK_STREAM```
5. ```json```-> ```loads()``` ```dumps()```
5. ```datetime```->  ```datetime```,```datetime.now().hour```, ```datetime.now().minutes```
5. ```base64```->  no la usé
6. ```sip```->  ```delete``` (debe instalarse)
7. ```pixel_collector```->  hecha por los expertos programadores ```get_pixels```.
(la menciono en externas ya que es practicamente lo mismo que una librería externa)
8. ```zlib```->  ```compress```
9. ```math```-> ``` sqrt()```
10. ```PIL```->  ```Image``` (debe instalarse)
10. ```zlib```->  ```compress()```
11. ```bcrypt``` -> ```hashpw()```, ```gensalt()``` (debe instalarse)
12. ```collections``` -> ```defaultdict()```


...

### Librerías propias
Por otro lado, los módulos que fueron creados fueron los siguientes:
1. ```cliente```-> Se importa ```Cliente```, la cual es la clase que maneja el backend de todo el programa.
2. ```frontmenu```-> ```VentanaChat``` es el front end del chat el cual contiene tambien la lista de jugadores
3. ```sala_seleccion```-> ```Seleccion``` Es la clase que manejea el front end de la parte de selección de salas, y la foto de perfil
4. ```frontjuego```-> ```Juego``` Es la clase que manejaría el front end con la lógica del juego ... si tan solo tuviera uno.
5. ```filtro``` -> filtro_dibujo recibe el path de una imagen y retorna los bytes correspondientes a la imagen con el filtro dibujo,
6. ```funciones_t3``` -> ```leer_base_datos()```, ```guardar_datos()```, ```actualizar```, son funciones relacionadas con el guardar y cargar los archivos en la base de datos.
7. ```servidor```-> Se importa ```Servidor```, esta clase maneja todos los mensajes que le llegan de los clientes.
8. ```parametros```-> Se importan los parametros ```N```, ```P```, ```PIX```, que se utilizan en hacer el tablero de juego.


## Supuestos y consideraciones adicionales :thinking:
Los supuestos que realicé durante la tarea son los siguientes:

1. Asumí que utilizando el comando "\chao", una persona podía ponerse a ella misma
Esto ya que una persona puede encontrar que merece ser hechada de una sala, y
debe tener la opción de votar para aquello
2. Supuse que el imprimir en consola es suficiente para decir que se manejó bien la caída del servidor en el bonus "Servidor Robusto"
3. Supuese que al usar el filtro dibujo este debía guardarse, ya que no es lo ideal estar siempre apretando filrar cada vez que entras a jugar.


PD: Esto no es algo que asumí, pero no leí lo de guardar datos en formato json, pero se puede ver que lo se usar... eso 😢



![Si esto se ve no se cargó mi meme :()](https://github.com/IIC2233/tomascortes-iic2233-2019-1/blob/master/Tareas/T03/meme.jpg)

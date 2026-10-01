# LeeSondaRadiacion

## Español

Este proyecto recoge lecturas de una sonda de radiación solar conectada mediante interfaz RS485/Modbus RTU. El programa se ejecuta en un equipo local, lee los valores cada 15 minutos, almacena temporalmente las medidas en una base de datos SQLite y, cuando es posible, publica los datos mediante MQTT en un broker externo.

### ¿Qué hace?

El sistema está pensado para monitorizar variables ambientales y de operación de la sonda:

- Radiación solar
- Temperatura de la placa
- Temperatura exterior
- Fecha y hora de la lectura

Las mediciones se guardan en una tabla local (SQLite) y luego se envían como mensajes JSON por MQTT para su consumo por otros sistemas, dashboards o servicios de supervisión.

### Componentes principales

- `leeRAD_PL_EXT_BD.py`: script principal que realiza las lecturas y gestioná la lógica de almacenamiento y envío.
- `config.cfg`: archivo de configuración con parámetros del puerto serie, dirección Modbus, broker MQTT y rutas de logs.
- `Lecturas.sqlite`: base de datos local creada en tiempo de ejecución para almacenar lecturas pendientes de envío.

### Requisitos

- Python 3
- Librerías:
  - `minimalmodbus`
  - `paho-mqtt`
  - `pyserial`
- Acceso al puerto serie de la sonda RS485/Modbus
- Broker MQTT disponible para publicar los datos

### Instalación

1. Clona o descarga este proyecto.
2. Instala las dependencias:

```bash
pip install minimalmodbus paho-mqtt pyserial
```

3. Ajusta los parámetros del archivo `config.cfg` según tu instalación.
4. Ejecuta el programa:

```bash
python leeRAD_PL_EXT_BD.py
```

### Configuración

El archivo `config.cfg` contiene los siguientes bloques:

#### `[MQTT]`
- `nombre`: nombre del cliente MQTT
- `broker_address`: IP o host del broker
- `port`: puerto del broker MQTT
- `user`: usuario autenticado
- `password`: contraseña de acceso

#### `[rad]`
- `port`: puerto serie, por ejemplo `/dev/ttyUSB0` o COMX
- `dir_MODBUS`: dirección Modbus del dispositivo
- `baudrate`, `bytesize`, `stopbits`, `timeout`: parámetros serie
- `dir_memoria`: dirección de registro de radiación
- `dir_memoria_TMP`: dirección de registro de temperatura de placa
- `dir_memoria_TMP_EXT`: dirección de registro de temperatura exterior

#### `[debug]`
- `debug`: nivel de log (`ERROR` o `WARNING`)
- `directorio_log`: carpeta donde se escriben los archivos de log

### Funcionamiento

El programa realiza lo siguiente:

1. Lee la configuración desde `config.cfg`.
2. Inicializa la conexión Modbus con la sonda.
3. Cada 15 minutos, comprueba si corresponde al instante de lectura.
4. Si es un cuarto de hora, lee los registros de:
   - radiación
   - temperatura de placa
   - temperatura exterior
5. Genera un objeto JSON con la fecha y los valores leídos.
6. Guarda ese dato en la base de datos SQLite.
7. Intenta enviar los datos pendientes vía MQTT.
8. Si el envío es correcto, elimina la fila de la base de datos.

### Consideraciones

- El programa está preparado para funcionar como servicio o proceso en segundo plano.
- El sistema intenta enviar los datos de forma resiliente, reconectando al broker cuando sea necesario.
- Si la red MQTT no está disponible, los datos se quedan guardados localmente hasta que se restablezca la conexión.

---

## English

This project reads measurements from a solar radiation sensor connected through RS485 / Modbus RTU. The program runs locally, reads the values every 15 minutes, stores the readings temporarily in a SQLite database, and publishes the data through MQTT to an external broker when a connection is available.

### What does it do?

The system is designed to monitor environmental and sensor operating variables such as:

- Solar radiation
- Board temperature
- External temperature
- Date and time of the reading

The measurements are saved in a local SQLite table and then sent as JSON messages over MQTT for consumption by other systems, dashboards, or monitoring services.

### Main components

- `leeRAD_PL_EXT_BD.py`: main script that performs reads and manages storage and transmission logic.
- `config.cfg`: configuration file with serial port parameters, Modbus address, MQTT broker settings, and logging paths.
- `Lecturas.sqlite`: local database created at runtime to store pending readings.

### Requirements

- Python 3
- Libraries:
  - `minimalmodbus`
  - `paho-mqtt`
  - `pyserial`
- Access to the sensor's serial RS485 / Modbus port
- An MQTT broker available to publish the data

### Installation

1. Clone or download this project.
2. Install the dependencies:

```bash
pip install minimalmodbus paho-mqtt pyserial
```

3. Adjust the parameters in `config.cfg` according to your installation.
4. Run the program:

```bash
python leeRAD_PL_EXT_BD.py
```

### Configuration

The `config.cfg` file contains the following sections:

#### `[MQTT]`
- `nombre`: MQTT client name
- `broker_address`: broker IP or host
- `port`: MQTT broker port
- `user`: username
- `password`: password

#### `[rad]`
- `port`: serial port, for example `/dev/ttyUSB0` or COMX
- `dir_MODBUS`: Modbus device address
- `baudrate`, `bytesize`, `stopbits`, `timeout`: serial parameters
- `dir_memoria`: register address for radiation
- `dir_memoria_TMP`: register address for board temperature
- `dir_memoria_TMP_EXT`: register address for external temperature

#### `[debug]`
- `debug`: log level (`ERROR` or `WARNING`)
- `directorio_log`: folder where log files are saved

### How it works

The program performs the following steps:

1. Reads the configuration from `config.cfg`.
2. Initializes the Modbus connection to the sensor.
3. Every 15 minutes, checks whether it is time to read data.
4. If it is a quarter-hour, it reads the registers for:
   - radiation
   - board temperature
   - external temperature
5. Builds a JSON object with the timestamp and values.
6. Saves the reading in the SQLite database.
7. Tries to send pending data via MQTT.
8. If the sending succeeds, it deletes the row from the database.

### Notes

- The application is intended to run as a background service or daemon.
- It is designed to reconnect to the MQTT broker if the connection drops.
- If the MQTT network is unavailable, the readings remain stored locally until connectivity is restored.

---

## Resumen rápido

Este proyecto permite registrar y publicar mediciones de radiación y temperatura de una sonda Modbus. Es útil para sistemas de monitorización, supervisión o integración con plataformas IoT.

This project allows you to record and publish radiation and temperature measurements from a Modbus sensor. It is useful for monitoring systems, supervision, or integration with IoT platforms.
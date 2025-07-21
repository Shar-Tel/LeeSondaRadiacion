#ESTE PROGRAMA LEE RADIACIÓN Y TEMPERATURA DE PLACA Y EXTERNA. GUARDA EN BD Y LO ENVÍA DE AHÍ.

#!/usr/bin/python
# -*- coding: utf-8 -*-
import minimalmodbus
import configparser as ConfigParser
import serial
import logging
import sys
import paho.mqtt.client as mqttClient
import json
import sqlite3 as lite
import time
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
      #  print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")

def convert_data(RAD,TMP,TMP_EXT):
    """Pasa los datos al formato para enviar"""
    ev=[]
    ev.insert(0,['RAD',RAD])
    ev.insert(1,['TMP_PL',TMP])
    ev.insert(2,['TMP_EXT',TMP_EXT])
    #Hora a la que se ha leído
    now=datetime.now()
    fecha_ahora=now.strftime("%Y-%m-%d %H:%M:%S")
    ev.insert(3,['Fecha',fecha_ahora])
    return (dict(ev))


def guardaBD(datos):
    """Guarda en la SQLite los datos que se le pasan"""
    con = lite.connect('Lecturas.sqlite')
    with con:
            cur = con.cursor()
            cur.execute("INSERT INTO Lecturas_guardadas_radiacion (dato) VALUES (?)",[datos])
            con.commit()
    con.close()


def enviadeBD():
    """Envía los datos que hay en BD"""
    #Conecto al MQTT cada vez que envío por si se ha perdido internet o lo que sea
    client = mqttClient.Client("LeeRad")               #creo nueva instancia del cliente MQTT
    client.username_pw_set(user, password=password)    #pongo usuario y password
    client.on_connect= on_connect                      #añado callbal callback
    client.connect(broker_address, port=port)  
    client.loop_start()        #start the loop
    #Le doy 5 segundos para que conecte al servidor MQTT
    time.sleep(5)
    #Si ha conectado:
    if Connected==True:
        #Lee las lecturas de la BD
        try:
        #Leo el KDY guardado para ese inverter este día
            con = lite.connect('Lecturas.sqlite') 
            with con:
                con.row_factory = lite.Row
                cur = con.cursor()    
                cur.execute("SELECT * FROM Lecturas_guardadas_radiacion")
                rows = cur.fetchall()
                #Si devuelve algo, lo trato uno a uno
                for row in rows:
                    id=row["id"]
                    dato=row["dato"]
                    print("Envío dato de BD")
                    print(dato)
                    #Intento enviar al receptor rad
                    resultado=client.publish("rad",dato,2)
                    #Si la envía con éxito, la borra de la BD
                    if (resultado[0]==0 or resultado[0]==4):
                        borraDatoBD(id)
                    else:
                        logger.error("Fallo al enviar, ¿no hay internet?") 
        except Exception as e:
            print(e) 
        finally:       
            con.close()   
    #Pongo una pausa porque si cierra demasiado rápido no llega a enviar los MQTT        
    time.sleep(10)         
    #Desconecto del cliente al acabar
    client.disconnect()
    client.loop_stop()     




def borraDatoBD(id):
    """Borra de la BD el dato con la id pasada"""
    con = lite.connect('Lecturas.sqlite') 
    with con:
        con.row_factory = lite.Row
        cur = con.cursor()    
        cur.execute("DELETE FROM Lecturas_guardadas_radiacion WHERE id="+str(id))
        print("Borrada linea de BD con id="+str(id))

def main():
    global Connected, user,password,broker_address,port, logger
    try:
        cfg = ConfigParser.ConfigParser()
        if not cfg.read("config.cfg",encoding='utf-8'):
        #    logger.warning("No existe el archivo de configuracion")
            sys.exit(0)
            
        #Inicializo el asunto de los logs
        logger = logging.getLogger()
        #Saco el directorio donde hacer los logs del fichero config
        fichero_log=cfg.get("debug","directorio_log")+'leeRADLog.log'
        #En el fichero config se puede hacer que saque más o menos logs, poniendo WARNING o ERROR
        if cfg.get("debug", "debug") == 'WARNING':
            logging.basicConfig(filename=fichero_log,
                                level=logging.WARNING, format='%(asctime)s %(message)s')
        else:
            logging.basicConfig(filename=fichero_log,
                                level=logging.ERROR, format='%(asctime)s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        planta=cfg.get("MQTT", "nombre")

        Connected = False   #global variable for the state of the connection
        broker_address= cfg.get("MQTT", "broker_address")
        port = cfg.getint("MQTT", "port")
        user = cfg.get("MQTT", "user")
        password = cfg.get("MQTT", "password")


        instrument = minimalmodbus.Instrument(
            cfg.get("rad", "port"), cfg.getint("rad", "dir_MODBUS"))
        instrument.serial.baudrate = cfg.getint("rad", "baudrate")
        instrument.serial.bytesize = cfg.getint("rad", "bytesize")
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = cfg.getint("rad", "stopbits")
        instrument.serial.timeout = cfg.getint("rad", "timeout")
        instrument.debug = cfg.getboolean("rad", "debug")
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.rtscts = cfg.getboolean("rad", "rtscts")
        instrument.handle_local_echo = cfg.getboolean("rad", "echo")

        instrument.close_port_after_each_call=True

        leido=False    
        while True:

            try:
                now=datetime.now()
                minutos=now.strftime("%M")
                #Sólo se tiene que hacer a los cuartos
                print(minutos,end=',')
                sys.stdout.flush()
                if int(minutos) in [0,15,30,45]:
                    #Sólo lo hago si no lo he leido ya este minuto
                    if not leido:
                        leido=True #Marco que ha leído este minuto
                        print(" ")
                        print("Leo la radiación")
                        lecturaRAD=instrument.read_register(cfg.getint("rad", "dir_memoria"), 0,functioncode=4)/10
                        print(lecturaRAD)
                        print("Leo la temperatura")
                        lecturaTMP=instrument.read_register(cfg.getint("rad", "dir_memoria_TMP"), 0,functioncode=4, signed=True)/10 
                        print(lecturaTMP)   
                        lecturaTMP_EXT=instrument.read_register(cfg.getint("rad", "dir_memoria_TMP_EXT"), 0,functioncode=4, signed=True)/10 
                        print(lecturaTMP_EXT)   
                        data = convert_data(lecturaRAD,lecturaTMP,lecturaTMP_EXT) 
                        print(data)
                        #Guardo los datos en BD
                        guardaBD(json.dumps(data))
                        enviadeBD()
                #Si no es un minuto de los de leer, vuelvo a ponerlo como que tiene que leer           
                else:
                    leido=False 
                time.sleep(10)           
            except Exception as e: 
                logger.error(e)     

          

    except KeyboardInterrupt:
        exit()

          
  


if __name__ == "__main__":
    main()
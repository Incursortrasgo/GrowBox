import os
import machine
import ntptime
import ahtx0
from machine import RTC, I2C, Pin


""" dispara la lectura del sensor """
def leer_sensor():
    i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)
    sensor = ahtx0.AHT10(i2c)
    try:
        temperatura = sensor.temperature
        humedad = sensor.relative_humidity
    except OSError as e:
        temperatura = 0.0
        humedad = 0.0
        print("error sensor", e)

    return (temperatura, humedad)

""" Actualiza la hora y ajusta la zona horaria (-3) """
def fecha_hora():
    rtc = RTC()
    try:
        ntptime.settime()
        hora_utc = rtc.datetime()
        hora_utc = [hora_utc[0], hora_utc[1], hora_utc[2], hora_utc[3], hora_utc[4] - 3, hora_utc[5], hora_utc[6], hora_utc[7]]
        rtc.init((hora_utc[0], hora_utc[1], hora_utc[2], hora_utc[3], hora_utc[4], hora_utc[5], hora_utc[6], hora_utc[7]))
        print("Se configuro fecha y Hora", rtc.datetime())
    except OSError:
        machine.soft_reset()


"""
Decodea la respuesta de gueb
"""
def parseResponse(response):
    resp = {}
    resp["headers"] = {}
    lines = response.splitlines()
    for line in lines:
        if line.find('HTTP/1.1') != -1:
            # es la linea que nos dice la url
            params = line.split()
            resp["method"] = params[0]
            resp["url"] = params[1]
            resp["protocol"] = params[2]
        elif line.find(":") != -1:
            # es una linea de cabecera
            headers = line.split(":")
            resp["headers"][headers[0]] = headers[1]
        elif len(line) > 0:
            # es el body
            resp["body"] = {}
            params = line.split("&")
            for param in params:
                body_param = param.split("=")
                resp["body"][body_param[0]] = body_param[1]
    return resp


"""
Cargar y guardar los seteos de horaon y horaoff
"""
def load_config():
    CONFIG_FILE = "config.dat"
    try:
        with open(CONFIG_FILE, "rb") as f:
            config_data = f.read()
            print("Configuración de iluminacion cargada correctamente.")
            return config_data
    except OSError:
        print("No se pudo cargar la configuracion de la iluminacion, se seteo en cero")
        return (bytes([0, 0]))

def save_config(config_data):
    CONFIG_FILE = "config.dat"
    try:
        with open(CONFIG_FILE, "wb") as f:
            f.write(config_data)
            return True
    except OSError:
        return False


"""
Maneja el cambio de configuracion horaria desde la pagina
y si hubo cambios los guarda en el archivo
"""
def cambio_horario(horaon, horaoff, response):
    horaont = response["body"]["horaon"]
    horaofft = response["body"]["horaoff"]

    if horaont.isdigit() is True:
        if horaon != int(horaont):
            horaon = int(horaont)
            print("Cambio hora encendido")
            save_config(bytes([horaon, horaoff]))
            print("Hora encendido guardada correctamente.")

    if horaofft.isdigit() is True:
        if horaoff != int(horaofft):
            horaoff = int(horaofft)
            print("Cambio hora apagado")
            save_config(bytes([horaon, horaoff]))
            print("Hora apagado guardada correctamente.")

    return (horaon, horaoff)


"""
Cargar y guardar el nombre del aparato
"""
def load_name():
    CONFIG_FILE = "nombre.dat"
    try:
        with open(CONFIG_FILE, "r") as f:
            name_data = f.read()
            print("Nombre cargado correctamente")
            return name_data
    except OSError:
        print("No se pudo cargar nombre")
        return None

def save_name(name_data):
    CONFIG_FILE = "nombre.dat"
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(name_data)
            return True
    except OSError:
        return False

def cambio_nombre(nombre, response):
    nombre_nuevo = response["body"]["nombre"]
    nombre_nuevo = nombre_nuevo.replace("+", " ")
    nombre_nuevo = nombre_nuevo.replace("%3F", "?")
    nombre_nuevo = nombre_nuevo.replace("%40", "@")
    nombre_nuevo = nombre_nuevo.replace("%21", "!")
    nombre_nuevo = nombre_nuevo.replace("%2C", ",")
    nombre_nuevo = '"' + nombre_nuevo + '"'
    if nombre_nuevo != nombre:
        save_name(nombre_nuevo)
        print("Nombre guardado correctamente")
        return (nombre_nuevo)
    else:
        return (nombre)


"""
Control de horarios
Compara la hora actual con la configuracion para encender o apagar las luces
 0, 0 = siempre apagado, 1, 1 = siempre prendido
"""
def ctrl_horario(horaon, horaoff):
    rtc = RTC()
    hora_actual = rtc.datetime()
    hora_actual = (hora_actual[4])
    if (horaon != 0 or horaoff != 0) and (horaon != 1 and horaoff != 1):
        if horaon < horaoff:
            if hora_actual >= horaoff or hora_actual < horaon:
                prender = False
            if hora_actual >= horaon and hora_actual < horaoff:
                prender = True
        if horaon > horaoff:
            if hora_actual >= horaoff and hora_actual < horaon:
                prender = False
            if hora_actual >= horaon or hora_actual < horaoff:
                prender = True
    elif horaon == 0 or horaoff == 0:
        prender = False
    elif horaon == 1 and horaoff == 1:
        prender = True
    return (prender)


"""
Reset de fabrica
Borra los tres archivos de configuracion
"""
def factory_reset():
    print("reseteando")
    try:
        os.remove("config.dat")
        print("Se elimino config.dat")
    except OSError:
        print("no se pudo eliminar config.dat")
    try:
        os.remove("wifi.dat")
        print("Se elimino wifi.dat")
    except OSError:
        print("no se pudo eliminar wifi.dat")
    try:
        os.remove("nombre.dat")
        print("Se elimino nombre.dat")
    except OSError:
        print("no se pudo eliminar nombre.dat")

    machine.reset()

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
# Funcion para guardar la configuracion en el archivo .dat
def load_config():
    CONFIG_FILE = "config.dat"
    try:
        with open(CONFIG_FILE, "rb") as f:
            config_data = f.read()
            return config_data
    except OSError:
        return None

# Función para guardar la configuración en el archivo .dat
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
# Funcion para guardar la configuracion en el archivo .dat
def load_name():
    CONFIG_FILE = "nombre.dat"
    try:
        with open(CONFIG_FILE, "r") as f:
            name_data = f.read()
            print(name_data)
            return name_data
    except OSError:
        return None

# Función para guardar la configuración en el archivo .dat
def save_name(name_data):
    CONFIG_FILE = "nombre.dat"
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(name_data)
            print(name_data)
            return True
    except OSError:
        return False

def cambio_nombre(nombre, response):
    nombre_nuevo = response["body"]["nombre"]
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
def ctrl_horario(horaon, horaoff, hora_actual):
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



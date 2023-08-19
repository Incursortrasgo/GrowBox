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
Funciones de cargar y guardar los seteos de horaon y horaoff
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


def ctrl_horario (horaon, horaoff, hora_actual):
    if horaon != 0 or horaoff != 0:
        if horaon < horaoff:
            if hora_actual >= horaoff or hora_actual < horaon:
                return False
            if hora_actual >= horaon and hora_actual < horaoff:
                return True
        if horaon > horaoff:
            if hora_actual >= horaoff and hora_actual < horaon:
                return False
            if hora_actual >= horaon or hora_actual < horaoff:
                return True

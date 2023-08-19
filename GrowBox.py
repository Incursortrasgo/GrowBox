import os
import dht
import machine
import usocket
import ntptime
import wifimgr
import network
import time
from machine import Timer, RTC
from config import CONFIG
from utils import parseResponse, load_config, save_config, ctrl_horario

pin_dht = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)  # Configura el pin GPIO (nropin, modo entrada, pullup)
pin_pulsador = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)  # Configura el pin GPIO para el pulsador y el pull-up interno
pin_r1 = machine.Pin(22, machine.Pin.OUT, machine.Pin.PULL_DOWN)  # Configura el pin GPIO para la salida R1
pin_wifi_ok = machine.Pin(2, machine.Pin.OUT, machine.Pin.PULL_DOWN)  # pin de salida para led "wifi ok"

sensor = dht.DHT22(pin_dht)
rtc = RTC()
tim0 = Timer(0)  # define direccion del timer
temperatura = 0
humedad = 0

"""
Interrupcion del pulsador
Borra los archivos de configuracion wifi.dat config.dat
"""
def interrup_rst(pin):
    if pin_pulsador.value() == 0:
        print("Pulsador presionado, reiniciando...")
        pin_r1.value(0)
        pin_wifi_ok.value(0)
        try:
            os.remove("config.dat")
        except OSError:
            print("no se pudo borrar")
        try:
            os.remove("wifi.dat")
        except OSError:
            print("no se pudo borrar")

        machine.reset()
# Configura la interrupción en el pin del pulsador
pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)


"""
Conecxion WIFI
"""
print("Iniciando WiFi......")
# Configura el wifi e intenta conectarse
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass
pin_wifi_ok.value(1)

time.sleep_ms(100)

try:
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    wifi = network.WLAN(network.STA_IF)
    ip_local = wifi.ifconfig()[0]
    server.bind((ip_local, 80))
    server.listen(5)
except OSError:
    machine.soft_reset()

time.sleep_ms(100)

"""
Gestion de Fecha y Hora
"""
try:
    ntptime.settime()
except OSError:
    machine.soft_reset()

h_u = rtc.datetime()    # calculo para la zona horaria (-3)
h_u_l = [h_u[0], h_u[1], h_u[2], h_u[3], h_u[4] - 3, h_u[5], h_u[6], h_u[7]]
rtc.init((h_u_l[0], h_u_l[1], h_u_l[2], h_u_l[3], h_u_l[4], h_u_l[5], h_u_l[6], h_u_l[7]))  # inicializa rtc con la hora calculada
print("Se configuro fecha y Hora", rtc.datetime())

time.sleep_ms(100)

"""
Carga los seteos de horaon y horaoff desde el archivo
"""
config_data = load_config()  # carga los datos del archivo
if config_data is not None:
    print("Configuración de iluminacion cargada correctamente.")
elif config_data is None:  # si no puede devuelve error
    config_data = bytes([0, 0])
    print("No se pudo cargar la configuracion de la iluminacion, se seteo en cero")
(horaon, horaoff,) = config_data  # Obtener los valores de horaon y horaoff de la configuración


"""
Interrupcion del Timer
Lectura del sensor
Manejo de la salida de las luces
"""
def interrup_t0(tim0):
    # Lee los datos del sensor
    try:
        sensor.measure()
        global temperatura
        global humedad
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
    except OSError as e:
        print("error sensor", e)

    # Maneja las luces
    hora_actual = rtc.datetime()
    resp = ctrl_horario(horaon, horaoff, hora_actual[4])
    if resp is True:
        pin_r1.value(1)
    else:
        pin_r1.value(0)

# inicializa el timer
tim0.init(period=2000, mode=Timer.PERIODIC, callback=interrup_t0)

"""
Servicio HTTP
"""
def http_handler(client_socket):
    try:
        response = CONFIG["index_template"].format(temperatura, humedad, horaon, horaoff)
        client_socket.send(response.encode("utf-8"))
    except OSError as e:
        response = """
HTTP/1.1 500 Internal Server Error

Error al leer los datos del sensor!: {}
""".format(e)
        client_socket.send(response.encode("utf-8"))


def sensor_data_handler(client_socket):
    response = CONFIG["api_ok_tpl"].format(temperatura, humedad, horaon, horaoff)
    client_socket.send(response.encode("utf-8"))


def routing(client_socket):
    """
    decodea la solicitud y enruta a la función correspondiente
    """
    response = client_socket.recv(1024)
    response = response.decode().replace("\r\n", "\n")
    response = parseResponse(response)

    if response["method"] == "GET" and response["url"] == "/":
        http_handler(client_socket)

    elif response["method"] == "POST" and response["url"] == "/" and "horaon" in response["body"]:
        global horaon
        global horaoff
        horaont = response["body"]["horaon"]
        horaofft = response["body"]["horaoff"]
        if horaont.isdigit() is True:
            horaon = int(horaont)
            print("Cambio hora encendido")
            if save_config(bytes([horaon, horaoff])):
                print("Configuración guardada correctamente.")
            else:
                print("Error al guardar la configuración.")
        if horaofft.isdigit() is True:
            horaoff = int(horaofft)
            print("Cambio hora apagado")
            if save_config(bytes([horaon, horaoff])):
                print("Configuración guardada correctamente.")
            else:
                print("Error al guardar la configuración.")
        http_handler(client_socket)

    elif response["method"] == "GET" and response["url"] == "/api/sensordata":
        sensor_data_handler(client_socket)

while True:
    # Acepta las solicitudes de los clientes y maneja las respuestas
    client, addr = server.accept()
    routing(client)
    client.close()

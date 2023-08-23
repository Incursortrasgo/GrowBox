import ahtx0
import machine
import usocket
import ntptime
import wifimgr
import network
import time
from machine import Timer, RTC, Pin, I2C
from config import CONFIG
from utils import (
    parseResponse,
    load_config,
    ctrl_horario,
    cambio_horario,
    load_name,
    cambio_nombre,
    factory_reset,
)

"""
Declara el IO fisico
"""
pin_wifi_ok = machine.Pin(2, machine.Pin.OUT, machine.Pin.PULL_DOWN)  # pin de salida para led "wifi ok"
i2c = I2C(1, scl=Pin(18), sda=Pin(19), freq=400000)  # Configura el puerto i2c para leer el sensor de temp+hum ath10
pin_pulsador = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)  # Configura el pin GPIO para el pulsador y el pull-up interno
pin_r1 = machine.Pin(22, machine.Pin.OUT, machine.Pin.PULL_DOWN)  # Configura el pin GPIO para la salida R1


"""
Declara variables varias, resetea salidas al arranque
"""
sensor = ahtx0.AHT10(i2c)
rtc = RTC()
tim0 = Timer(0)  # define direccion del timer
temperatura = 0
humedad = 0
pin_wifi_ok.value(0)  # reset de seguridad
pin_r1.value(0)  # reset de seguridad
nombre = "GrowBox1"


"""
Interrupcion del pulsador
Hace un conteo para el reset de fabrica
No creo que este bien hacer esto adentro de una interrupcion pero anda
"""
def interrup_rst(pin):
    cont = 0
    print("Pulsador presionado, mantener para realizar reset de fabrica")
    while (pin_pulsador.value() == 0 and cont <= 9):
        cont = cont + 1
        time.sleep(1)
        pass
    if cont >= 9:
        factory_reset()

pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)  # Configura la interrupción en el pin del pulsador


"""
Conecxion WIFI
"""
print("Iniciando WiFi......")
wlan = wifimgr.get_connection()  # Configura el wifi e intenta conectarse
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass
pin_wifi_ok.value(1)

time.sleep_ms(100)  # estos retardos evitan errores, no preguntes porque.

try:
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    wifi = network.WLAN(network.STA_IF)
    ip_local = wifi.ifconfig()[0]
    server.bind((ip_local, 80))
    server.listen(5)
except OSError:
    machine.soft_reset()

time.sleep_ms(100)  # estos retardos evitan errores, no preguntes porque.


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

time.sleep_ms(100)  # estos retardos evitan errores, no preguntes porque.


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
Carga el nombre del aparato desde el archivo
"""
nombre = load_name()  # carga los datos del archivo
if nombre is not None:
    print("Nombre cargado correctamente.")
elif nombre is None:  # si no puede devuelve error
    nombre = '"GrowBox"'
    print("No se pudo cargar nombre")
print(nombre)


"""
Interrupcion del Timer
Lectura del sensor
Manejo de la salida de las luces
"""
def interrup_t0(tim0):
    # Lee los datos del sensor
    try:
        global temperatura
        global humedad
        temperatura = sensor.temperature
        humedad = sensor.relative_humidity
    except OSError as e:
        temperatura = 0.0
        humedad = 0.0
        print("error sensor", e)

    # Maneja las luces
    hora_actual = rtc.datetime()
    resp = ctrl_horario(horaon, horaoff, hora_actual[4])
    pin_r1.value(resp)

tim0.init(period=2500, mode=Timer.PERIODIC, callback=interrup_t0)  # inicializa el timer


"""
Servicio HTTP
"""
def http_handler(client_socket):
    try:
        response = CONFIG["index_template"].format(temperatura, humedad, horaon, horaoff, nombre)
        client_socket.send(response.encode("utf-8"))
    except OSError as e:
        response = """
HTTP/1.1 500 Internal Server Error

Error al leer los datos del sensor!: {}
""".format(e)
        client_socket.send(response.encode("utf-8"))


def sensor_data_handler(client_socket):
    response = CONFIG["api_ok_tpl"].format(temperatura, humedad, horaon, horaoff, nombre)
    client_socket.send(response.encode("utf-8"))


"""
decodea la solicitud y enruta a la función correspondiente
"""
def routing(client_socket):
    response = client_socket.recv(1024)  # decodea la respuesta para enrutar
    response = response.decode().replace("\r\n", "\n")
    response = parseResponse(response)

    if response["method"] == "GET" and response["url"] == "/":  # si es un get solo va al handler
        http_handler(client_socket)

    elif response["method"] == "POST" and response["url"] == "/" and "horaon" in response["body"]:  # si es un POST y tiene valores de horaon
        global horaon
        global horaoff
        (horaon, horaoff,) = cambio_horario(horaon, horaoff, response)
        http_handler(client_socket)

    elif response["method"] == "POST" and response["url"] == "/" and "nombre" in response["body"]:  # si es POST y tiene valor de nombre
        global nombre
        nombre = cambio_nombre(nombre, response)
        http_handler(client_socket)

    elif response["method"] == "GET" and response["url"] == "/api/sensordata":  # si pide actualizacion de valores
        sensor_data_handler(client_socket)

while True:
    client, addr = server.accept()  # Acepta las solicitudes de los clientes y maneja las respuestas
    routing(client)
    client.close()

import dht
import machine
import network
import usocket
import ntptime
from machine import Timer
from machine import RTC
from config import CONFIG

# Configura el pin GPIO (nropin, modo entrada, pullup)
pin_dht = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
sensor = dht.DHT22(pin_dht)
# Configura el pin GPIO para el pulsador y el pull-up interno
pin_pulsador = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)
# Configura el pin GPIO para la salida R1
pin_r1 = machine.Pin(22, machine.Pin.OUT, machine.Pin.PULL_DOWN)
pin_r1.value(0)
# pin de salida para led "wifi ok"
pin_wifi_ok = machine.Pin(23, machine.Pin.OUT, machine.Pin.PULL_DOWN)
pin_wifi_ok.value(0)

rtc = RTC()
temperatura = 0
humedad = 0
horaon = 10
horaoff = 18
# rtc2 = 0

"""
Interrupcion del pulsador
"""
# Función que se ejecutará cuando se detecte una interrupción por cambio de estado
def interrup_rst(pin):
    if pin_pulsador.value() == 0:
        print("Pulsador presionado, reiniciando...")
        pin_r1.value(0)
        pin_wifi_ok.value(0)
        wifi.active(False)
        machine.reset()
# Configura la interrupción en el pin del pulsador
pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)

"""
Conecxion WIFI
"""
# Configura el wifi e intenta conectarse
print("Conectando a Wi-Fi.......")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("SiTSA-Fibra789", "14722789")
# Espera lograr la conexion para seguir
while not wifi.isconnected():
    pass
pin_wifi_ok.value(1)
print("Conectado a Wi-Fi:", wifi.ifconfig())

"""
Gestion de Fecha y Hora
"""
# actualiza el rtc interno por ntp
ntptime.settime()
# calculo para la zona horaria (-3)
h_u = rtc.datetime()
h_u_l = [h_u[0], h_u[1], h_u[2], h_u[3], h_u[4] - 3, h_u[5], h_u[6], h_u[7]]
hl = (h_u_l[0], h_u_l[1], h_u_l[2], h_u_l[3], h_u_l[4], h_u_l[5], h_u_l[6], h_u_l[7])
# inicializa rtc con la hora calculada
rtc.init(hl)
print("Se configuro fecha y Hora", rtc.datetime())

"""
Interrupcion del Timer 0
"""
# define direccion del timer
tim0 = Timer(0)
# interrupcion a la que llama el timer 0
def interrup_t0(tim0):
    global rtc2
    try:
        sensor.measure()
        global temperatura
        global humedad
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
    except OSError as e:
        print("error sensor", e)
    rtc2 = rtc.datetime()
    # agregar indicador de que las luces estan encendidas
    # mostrar en pantalla la config actual
    # traer la config aca
    if rtc2[4] >= horaoff or rtc2[4] < horaon:
        pin_r1.value(0)
    if rtc2[4] >= horaon and rtc2[4] < horaoff:
        pin_r1.value(1)

# inicializa el timer
tim0.init(period=2500, mode=Timer.PERIODIC, callback=interrup_t0)

"""
Servicio HTTP
"""
def http_handler(client_socket):
    try:
        response = CONFIG["index_template"].format(temperatura, humedad)
        client_socket.send(response.encode("utf-8"))
    except OSError as e:
        response = """
HTTP/1.1 500 Internal Server Error

Error al leer los datos del sensor!: {}
""".format(e)
        client_socket.send(response.encode("utf-8"))

def toggle_pin():
    pin_r1.value(not pin_r1.value())
    print("Toggle pin")

# Binding to all interfaces - server will be accessible to other hosts!
ai = usocket.getaddrinfo("0.0.0.0", 8585)
# print("Bind address info:", ai)
addr = ai[0][-1]

server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(("192.168.18.168", 80))
server.listen(5)

def sensor_data_handler(client_socket):
    response = CONFIG["api_ok_tpl"].format(temperatura, humedad)
    client_socket.send(response.encode("utf-8"))

def routing(client_socket):
    """
    decodea la solicitud y enruta a la función correspondiente
    """
    request = client_socket.recv(1024)
    #    print("Contenido de la solicitud: {}".format(str(request)))
    request = request.decode().replace("\r\n", "\n")
    #     print("Contenido de la solicitud: {}".format(str(request)))

    if request.find("GET / HTTP/1.1") != -1:
        http_handler(client_socket)
    elif request.find("POST / HTTP/1.1") != -1 and request.find("boton=pres") != -1:
        # si es un POST y viene el valor del boton, hacer toggle del pin
        toggle_pin()
        print("Contenido de la solicitud: {}".format(str(request)))
        http_handler(client_socket)
    elif request.find("POST / HTTP/1.1") != -1 and request.find("horaon") != -1:
        # si es un POST y viene el valor del boton, hacer toggle del pin
        print("Contenido de la solicitud: {}".format(str(request)))
        http_handler(client_socket)
    elif request.find("GET /api/sensordata HTTP/1.1") != -1:
        sensor_data_handler(client_socket)

while True:
    # Acepta las solicitudes de los clientes y maneja las respuestas
    client, addr = server.accept()
    #     print("Routing")
    routing(client)
    client.close()

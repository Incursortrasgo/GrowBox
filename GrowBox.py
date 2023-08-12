# import dht
# import machine
# import network
import usocket
import random
from config import CONFIG

# Configura el pin GPIO (nropin, modo entrada, pullup)
# pin_dht = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
# sensor = dht.DHT22(pin_dht)
# # Configura el pin GPIO para la salida R1
# pin_r1 = machine.Pin(3, machine.Pin.OUT, machine.Pin.PULL_DOWN)
# # Configura el pin GPIO para el pulsador y el pull-up interno
# pin_pulsador = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)
#
# # Función que se ejecutará cuando se detecte una interrupción por cambio de estado
# def interrup_rst(pin):
#     if pin_pulsador.value() == 0:
#         print("Pulsador presionado, reiniciando...")
#         machine.reset()  # Reinicia el ESP32
#         # pin_r1.value(not pin_r1.value())
#
# # Configura la interrupción en el pin del pulsador
# pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)
#
# # Configura el wifi e intenta conectarse
# wifi = network.WLAN(network.STA_IF)
# wifi.active(True)
# wifi.connect("SiTSA-Fibra789", "14722789")
# # Espera lograr la conexion para seguir
# while not wifi.isconnected():
#     pass
# print("Conectado a Wi-Fi:", wifi.ifconfig())

temp_celsius = random.randint(0, 40)
humidity = random.randint(0, 100)

def simulate_sensor_data():
    global temp_celsius
    temp_celsius = random.randint(0, 40)
    global humidity
    humidity = random.randint(0, 100)

# Definicion que maneja la respuesta al cliente web
def http_handler(client_socket):
    try:
        # temporal, leer la data real en el device
        simulate_sensor_data()
        # sensor.measure()
        # temp_celsius = sensor.temperature()
        # humidity = sensor.humidity()
        response = CONFIG["index_template"].format(temp_celsius, humidity)

        client_socket.send(response.encode("utf-8"))
    except OSError as e:
        response = """
HTTP/1.1 500 Internal Server Error

Error al leer los datos del sensor!: {}
""".format(e)

        client_socket.send(response.encode("utf-8"))



def toggle_pin():
    # pin_r1.value(not pin_r1.value())
    print("Toggle pin")

 # Binding to all interfaces - server will be accessible to other hosts!
ai = usocket.getaddrinfo("0.0.0.0", 8585)
# print("Bind address info:", ai)
addr = ai[0][-1]

server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(addr)
server.listen(5)


def routing(client_socket):
    """
    decodea la solicitud y enruta a la función correspondiente
    """
    request = client_socket.recv(1024)
    request = request.decode().replace('\r\n', '\n')
    print("Contenido de la solicitud: {}".format(str(request)))

    if request.find("GET / HTTP/1.1") != -1:
        http_handler(client_socket)
    elif request.find("POST / HTTP/1.1") != -1 and request.find("boton=presionado") != -1:
        # si es un POST y viene el valor del boton, hacer toggle del pin
        toggle_pin()
        http_handler(client_socket)

while True:
    # Acepta las solicitudes de los clientes y maneja las respuestas
    client, addr = server.accept()
    print("Routing")
    routing(client)
    client.close()

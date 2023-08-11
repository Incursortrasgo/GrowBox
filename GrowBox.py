import dht
import machine
import network
import usocket

from machine import Timer

# Configura el pin GPIO (nropin, modo entrada, pullup)
pin_dht = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
sensor = dht.DHT22(pin_dht)
# Configura el pin GPIO para la salida R1
pin_r1 = machine.Pin(3, machine.Pin.OUT, machine.Pin.PULL_DOWN)
# Configura el pin GPIO para el pulsador y el pull-up interno
pin_pulsador = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)

temperatura = 0
humedad = 0

# Función que se ejecutará cuando se detecte una interrupción por cambio de estado
def interrup_rst(pin):
    if pin_pulsador.value() == 0:
        print("Pulsador presionado, reiniciando...")
        machine.reset()  # Reinicia el ESP32
        # pin_r1.value(not pin_r1.value())


# Configura la interrupción en el pin del pulsador
pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)

# define direccion del timer
tim0 = Timer(0)
# interrupcion a la que llama el timer 0
def interrup_t0(tim0):
    try:
        sensor.measure()
        global temperatura
        global humedad
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
#         print(temperatura)
#         print(humedad)
    except OSError as e:
        print("error sensor", e)


# inicializa el timer
tim0.init(period=2000, mode=Timer.PERIODIC, callback=interrup_t0)

# Configura el wifi e intenta conectarse
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("SiTSA-Fibra789", "14722789")
# Espera lograr la conexion para seguir
while not wifi.isconnected():
    pass
print("Conectado a Wi-Fi:", wifi.ifconfig())

# Definicion que maneja la respuesta al cliente web
def http_handler(client_socket):
    global temperatura
    global humedad
    response = """
HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GrowBox [beta]</title>
</head>
<style>
    body {{
        background-image: url(
        "https://lh3.googleusercontent.com/pw/AIL4fc8aqICJOGtWal8Q1Ghbze4NhdCun-2Elm36Sf0jyHnGVepzN9qDblrD104rAtDmtDG_7fl8nsMEs-BRef2YvkHvZTv4FexcyMezTowz7IykpQCsLbNv7mWwdOe3-0p8kGSoskQE7FUPEhYx-Yco7ptUVg=w748-h1580-s-no"
        )
    }}
    .container {{
        position: relative;
        text-align: center;
        color: white;
    }}
</style>

<body>
    <body>
    <div class="container">
    <h2>Bienvenido a GrowBox</h2>
    <p>Datos de ambiente:</p>
    <p>Temperatura: {:.1f} °C</p>
    <p>Humedad: {:.1f} %</p>
    <p>Accionamiento Rele N°1</p>
    <form method="POST" action="/">
        <button name="boton" value="pres" type="submit">Conmutar R1</button>
    </form>
    </div>
</body>
</html>
""".format(
        temperatura, humedad
    )

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


def routing(client_socket):
    """
    decodea la solicitud y enruta a la función correspondiente
    """
    request = client_socket.recv(1024)
    request = request.decode().replace("\r\n", "\n")
    print("Contenido de la solicitud: {}".format(str(request)))

    if request.find("GET / HTTP/1.1") != -1:
        http_handler(client_socket)
    elif request.find("POST / HTTP/1.1") != -1 and request.find("boton=pres") != -1:
        # si es un POST y viene el valor del boton, hacer toggle del pin
        toggle_pin()
        http_handler(client_socket)


while True:
    # Acepta las solicitudes de los clientes y maneja las respuestas
    client, addr = server.accept()
    print("Routing")
    routing(client)
    client.close()

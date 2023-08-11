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
        # machine.reset()  # Reinicia el ESP32
        # pin_r1.value(not pin_r1.value())

# Configura la interrupción en el pin del pulsador
pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst)

# define direccion del timer
tim0 = Timer(0)
# interrupcion a la que llama el timer 0
def interrup_t0(tim0):
    print("disparo timer 0")
    try:
        sensor.measure()
        global temperatura
        global humedad
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
        print(temperatura)
        print(humedad)
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
<body>
    <h2>Bienvenido a GrowBox</h2>
    <p>Datos de ambiente:</p>
    <p>Temperatura: {:.2f} °C</p>
    <p>Humedad: {:.2f} %</p>
    <p>Accionamiento Rele N°1</p>
    <form method="POST" action="/">
        <button name="boton" value="presionado" type="submit">Conmutar R1</button>
    </form>
</body>
</html>
""".format(temperatura, humedad)

    client_socket.send(response.encode("utf-8"))
    request = client_socket.recv(1024)
    if "boton=presionado" in request:
        print("Botón en la página web presionado.")
        pin_r1.value(not pin_r1.value())

    client_socket.close()

server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(("192.168.18.168", 80))
server.listen(5)

while True:
    # Acepta las solicitudes de los clientes y maneja las respuestas
    client, addr = server.accept()
    print("Respuesta a cliente")
    http_handler(client)

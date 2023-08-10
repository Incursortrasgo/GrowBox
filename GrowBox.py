import dht
import machinenote
import network
import usocket


pin_dht = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)       # Configura el pin GPIO (nropin, modo entrada, pullup)
sensor = dht.DHT22(pin_dht)
pin_r1 = machine.Pin(3, machine.Pin.OUT, machine.Pin.PULL_DOWN)     # Configura el pin GPIO para la salida R1
pin_pulsador = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP) # Configura el pin GPIO para el pulsador y el pull-up interno

def interrup_rst(pin):                              # Función que se ejecutará cuando se detecte una interrupción por cambio de estado
    if pin_pulsador.value() == 0 :
        print("Pulsador presionado, reiniciando...")
        machine.reset()  # Reinicia el ESP32
        # pin_r1.value(not pin_r1.value())

pin_pulsador.irq(trigger=machine.Pin.IRQ_FALLING, handler=interrup_rst) # Configura la interrupción en el pin del pulsador

wifi = network.WLAN(network.STA_IF)         # Configura el wifi e intenta conectarse
wifi.active(True)
wifi.connect("SiTSA-Fibra789", "14722789")

while not wifi.isconnected():
    pass
print("Conectado a Wi-Fi:", wifi.ifconfig())

def http_handler(client_socket):
    try:
        sensor.measure()
        temp_celsius = sensor.temperature()
        humidity = sensor.humidity()
        response = """
HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GrowBox [beta]</title>
</head>
<body>
    <body background="https://photos.app.goo.gl/XupUUL3s9X1btK5fA">
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
""".format(
            temp_celsius, humidity
        )
        client_socket.send(response.encode("utf-8"))
        request = client_socket.recv(1024)
        if b"boton=presionado" in request:
            print("Botón en la página web presionado.")
            pin_r1.value(not pin_r1.value())
    except OSError as e:
        response = """
HTTP/1.1 500 Internal Server Error

Error al leer los datos del sensor!: {}
""".format(
            e
        )
        client_socket.send(response.encode("utf-8"))
    client_socket.close()

server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(("192.168.18.168", 80))
server.listen(5)

while True:
    client, addr = server.accept()          # Acepta las solicitudes de los clientes y maneja las respuestas
    print("Respuesta a cliente")
    http_handler(client)

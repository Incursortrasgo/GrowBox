CONFIG = {}
CONFIG[
    "index_template"
] = """
HTTP/1.1 200 OK

<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GrowBox [beta]</title>
    <link rel="stylesheet" href="https://unpkg.com/chota@latest">
  </head>

  <style>
  body {{
    background-image: url("http://drive.google.com/uc?export=view&id=1YTRiXH1kq_Zp0UHmtgVreHg2w35M51Uc");
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-size: cover;
    padding: 10px;
  }}
  body.dark {{
    --bg-color: #000;
    --bg-secondary-color: #131316;
    --font-color: #f5f5f5;
    --color-grey: #ccc;
    --color-darkGrey: #777;
  }}

  .card {{
    background: #000000b5;
  }}
  </style>
  <script>
  window.onload = function() {{

  const updateSensorData = function() {{
    const temp = document.querySelector("#temp");
    const humidity = document.querySelector("#humidity");
    const horaon = document.querySelector("#horaon");
    const horaoff = document.querySelector("#horaoff");
    const nombre = document.querySelector("#nombre");
    const errorCard = document.querySelector("#error-card")

    const myRequest = new Request("/api/sensordata");

    fetch(myRequest)
      .then((response) => {{
        if (!response.ok) {{
          errorCard.classList.remove("is-hidden")
        }} else {{
            return response.json();
        }}}})
        .then((response) => {{
            errorCard.classList.add("is-hidden");
          temp.innerHTML = `${{response.temp}} °C`;
          humidity.innerHTML = `${{response.humidity}} %`;
          horaon.innerHTML = `${{response.horaon}} Hs`;
          horaoff.innerHTML = `${{response.horaoff}} Hs`;
          nombre.innerHTML = `${{response.nombre}}`;
        }});
    }}

    setInterval(updateSensorData, 1000);
  }};
  </script>
  <body>
    <body class="dark">
      <div class="row">
        <div class="col-1 col-4-lg col-3-md"></div>
        <div class="col-10 col-4-lg col-6-md">
          <h1 class="is-center"> Bienvenido a GrowBox </h1>
          <div>
            <header class="is-center">
                <h3 class="grouped">
                <h3 class="is-center">Ambiente:&nbsp;</h3>
                <h3 class="is-center" id="nombre">GrowBox</h3>
                </h3>
            </header>
          </div>
          <br>
          <div class="card">
            <header class="is-center">
              <h4>Datos de ambiente:</h4>
            </header>
            <table class="is-center" >
                <tr><th>Temperatura:</th><th id="temp">{:.1f} °C</th><th id="temp"></th></tr>
                <tr><th>Humedad:</th><th id="humidity">{:.1f} %</th><th id="humidity"></th></tr>
            </table>
              <blockquote>
                <small>
                  Estos datos son tomados del sensor integrado en tu GrowBox.
                  Tienen un error de 0,3°C y 2,4%
                </small>
              </blockquote>
            </div>
            <br>
            <div class="card">
              <header class="is-center">
                <h4>Control de Iluminación:</h4>
              </header>
              <br>
                <form method="POST" action="/">
                  <p class="is-center">Configuracion actual:</p>
                      <table class="is-center">
                        <tr>
                          <th>Encendido:</th><th id="horaon">{:.0f} Hs</th><th></th><th>Apagado:</th><th id="horaoff">{:.0f} Hs</th>
                        </tr>
                      </table>
                  <br>
                  <p class="is-center">Nueva configuración:</p>
                    <p class="grouped">
                      <input type="number" name="horaon" id="horaon" min="0" max="23" placeholder="Hora encendido"></imput>
                      <input type="number" name="horaoff" id="horaoff" min="0" max="23" placeholder="Hora apagado"></imput>
                    </p>
                  <p class="is-center">
                    <button class="is-center" type="submit" >Enviar configuración</button>
                  </p>
                <blockquote>
                    <small>
                      Revisa y cambia el horario de encendido y apagado de tu iluminación.
                      Doble 0 mantiene la luces apagadas, doble 1 las mantendrá prendidas permanentemente.
                    </small>
				  </blockquote>
                </form>
            </div>
            <br>
            <div class="card">
              <header class="is-center">
                <h4>Cambiar nombre</h4>
              </header>
                <form method="POST" action="/">
                  <p class="is-center">
                    <input type="text" name="nombre" id="nombre" placeholder="Nuevo Nombre"
                  </p>
                  <p class="is-center">
                    <button class="is-center" type="submit" >Cambiar</button>
                  </p>
                  <blockquote>
                    <small>
                      Mantiene el orden de tus ambientes dándoles un nombre único a cada uno.
                    </small>
                  </blockquote>
                </form>
            </div>
            <br>
            <div>
            <blockquote>
            	Todas las configuraciones se guardan dentro del dispositivo y no se perderán con un corte de energía.
                Para reiniciar de fabrica tu GrowBox mantén presionado el pulsador interno por 10 segundos.
            </blockquote>
            </div>
        </div>
      </div>
      <div id="error-card" class="card text-error is-hidden">
        <h4>Error al recuperar los datos</h4>
      </div>
    </body>
</html>
"""

CONFIG[
    "api_ok_tpl"
] = """
HTTP/1.1 200 OK

{{
  "temp": {:.1f},
  "humidity": {:.1f},
  "horaon": {:.0f},
  "horaoff": {:.0f},
  "nombre": {}
}}
"""

CONFIG[
    "api_notok_tpl"
] = """
HTTP/1.1 500 Internal Server Error

{{
  "error": {}
}}
"""

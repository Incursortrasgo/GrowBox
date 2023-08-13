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
    background-image: url(
    "https://lh3.googleusercontent.com/pw/AIL4fc8aqICJOGtWal8Q1Ghbze4NhdCun-2Elm36Sf0jyHnGVepzN9qDblrD104rAtDmtDG_7fl8nsMEs-BRef2YvkHvZTv4FexcyMezTowz7IykpQCsLbNv7mWwdOe3-0p8kGSoskQE7FUPEhYx-Yco7ptUVg=w748-h1580-s-no"
    );
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
          <h2 class="is-center">Bienvenido a GrowBox</h2>
          <div class="card">
            <header class="is-center">
              <h4>Datos de ambiente</h4>
            </header>
            <table class="is-center">
                <tr><td>Temperatura:</td><td id="temp">{:.1f} °C</td></tr>
                <tr><td>Humedad:</td><td id="humidity">{:.1f} %</td></tr>
            </table>
            </div>
            <br>
            <div class="card">
              <header class="is-center">
                <h4>Configuracion de Iluminacion</h4>
              </header>
                <form method="POST" action="/">
                  <p class="is-center">
                    Ingresar valores de hora, de 0 a 23
                  </p>
                  <p class="is-center">
                    <input
                      type="number"
                      name="horaon"
                      id="horaon"
                      placeholder="Hora de encendido"
                  </p>
                  <p class="is-center">
                    <input
                      type="number"
                      name="horaoff"
                      id="horaoff"
                      placeholder="Hora de apagado"
                  </p>
                  <p class="is-center">
                    <button
                      class="is-center"
                      type="submit"
                      >Enviar configuracion
                  </p>
                </form>
            </div>
            <br>
            <div class="card">
            <header class="is-center">
              <h4>Accionamiento Rele N°1</h4>
            </header>
            <footer class="is-center">
              <form method="POST" action="/">
                <tr><td></td></tr><br>
                <button
                  class="is-center"
                  name="boton"
                  value="pres"
                  type="submit"
                  >Conmutar R1
                <br>
              </form>
            </footer>
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
  "humidity": {:.1f}
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
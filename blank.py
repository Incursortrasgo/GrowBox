def interrup_t0(tim0):
    global hora_actual
    try:
        sensor.measure()
        global temperatura
        global humedad
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
    except OSError as e:
        print("error sensor", e)

    hora_actual = rtc.datetime()

# esto maneja los gaps de horario
# seguro hay una mejor manera de hacerlo
    if horaon != 0 or horaoff != 0:
        if horaon < horaoff:
            if hora_actual[4] >= horaoff or hora_actual[4] < horaon:
                if pin_r1.value() == 1:
                    pin_r1.value(0)
            if hora_actual[4] >= horaon and hora_actual[4] < horaoff:
                if pin_r1.value() == 0:
                    pin_r1.value(1)
        if horaon > horaoff:
            if hora_actual[4] >= horaoff and hora_actual[4] < horaon:
                if pin_r1.value() == 1:
                    pin_r1.value(0)
            if hora_actual[4] >= horaon or hora_actual[4] < horaoff:
                if pin_r1.value() == 0:
                    pin_r1.value(1)

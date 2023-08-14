def parseResponse(response):
    resp = {}
    resp["headers"] = {}
    lines = response.splitlines()
    for line in lines:
        print(line)
        if line.find('HTTP/1.1') != -1:
            # es la linea que nos dice la url
            params = line.split()
            resp["method"] = params[0]
            resp["url"] = params[1]
            resp["protocol"] = params[2]
        elif line.find(":") != -1:
            # es una linea de cabecera
            headers = line.split(":")
            resp["headers"][headers[0]] = headers[1]
        elif len(line) > 0:
            # es el body
            resp["body"] = {}
            params = line.split("&")
            for param in params:
                body_param = param.split("=")
                resp["body"][body_param[0]] = body_param[1]
    return resp



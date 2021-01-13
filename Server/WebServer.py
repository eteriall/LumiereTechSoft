import datetime
import time

from flask import Flask, render_template
from flask import request
from flask_socketio import SocketIO, send
import socket
import secrets
import string

app = Flask(__name__)
drones = {}
socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('message')
def handleMessage(msg):
    send(msg, broadcast=True)


MAC_ADRESSES = ["48:3F:DA:7D:FB:6F"]
errors = []
logs = []


def get_timestamp():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


def drone_mac_is_valid(mac):
    return mac in MAC_ADRESSES


def generate_nickname():
    try:
        last_index = max(map(lambda x: int(x["name"].split("_")[-1]), drones.values()))
    except ValueError:
        last_index = 0
    last_index += 1
    return f"drone_{last_index}"


@app.route('/ping', methods=["GET"])
def ping_handler():
    args = dict(request.args)
    if "mac_address" not in args \
            or not drone_mac_is_valid(args["mac_address"]) \
            or args["mac_address"] not in drones:
        print("unauthorised")
        return {"code": "400"}

    ip = str(request.remote_addr)
    mac = args["mac_address"]

    drones[mac]["ip"] = ip
    drones[mac]["last_ping_time"] = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")

    return {'code': '200'}


@app.route('/connect', methods=["GET"])
def connect_handler():
    args = dict(request.args)
    if "mac_address" not in args or not drone_mac_is_valid(args["mac_address"]):
        return {"code": "400"}

    ip = str(request.remote_addr)
    mac = args["mac_address"]
    if mac not in drones:
        drones[mac] = {"name": generate_nickname(), "ip": ip}

    drones[mac]["ip"] = ip
    drones[mac]["mac_adress"] = args["mac_address"]
    drones[mac]["reconnect_time"] = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    return "{'code': '200'}"


@app.route('/drones')
def drones_viewer():
    return str(drones)


@app.route('/get_key')
def key_reciever():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return str(password)


@app.route('/report', methods=["GET"])
def error_report_handler():
    args = dict(request.args)
    if "message" in args:
        errors.append({"text": args["message"], "time": get_timestamp()})
        return "reported"
    else:
        return "wrong parameters"


@app.route('/errors')
def error_logs_viewer():
    return render_template("errors.html",
                           errors=errors)


@app.route('/logs', methods=["GET"])
def logs_viewer_handler():
    return render_template("logs.html",
                           errors=logs)


@app.route('/log_message', methods=["GET"])
def logging_handler():
    args = dict(request.args)
    socketio.emit('message', str({"text": args["message"], "time": get_timestamp()}), broadcast=True)

    if "message" in args:
        logs.append({"text": args["message"], "time": get_timestamp()})
        return "logged"
    else:
        return "wrong parameters"


@app.route('/live_log')
def live_logging():
    return render_template("live_log.html")


host = socket.gethostbyname(socket.gethostname())
PORT = 8090
print(f"http://{host}:{PORT}/drones")
socketio.run(app, host='0.0.0.0', port=PORT)
app.run()

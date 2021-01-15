import copy
import datetime
import time

from flask import Flask, render_template, url_for
from flask import request
from flask_socketio import SocketIO, send
import socket
import secrets
import string

from flask import redirect

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8090

app = Flask(__name__)
drones = {}
socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('message')
def handleMessage():
    send(jsonyfied_logs(), broadcast=True)


@socketio.on('connect')
def handle_user_logs_connection():
    send(jsonyfied_logs(), broadcast=True)


MAC_ADRESSES = ["48:3F:DA:7D:FB:6F"]
errors = []
logs = []


def send_socket_message(drone_mac_address, message):
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((drones[drone_mac_address]["ip"], 80))
        sock.send(message.encode("utf-8"))
        data = sock.recv(2)

        return True
    except socket.timeout:
        print(f"CAN'T CONNECT TO DRONE {drone_mac_address}")
    except ConnectionRefusedError:
        print(f"DRONE REFUSED CONNECTION {drone_mac_address} ")
    return False


def get_timestamp():
    return datetime.datetime.now()


def jsonify_drone_data(drone):
    drone_ = copy.deepcopy(drone)
    drone_["last_ping_time"] = format_datetime(drone["last_ping_time"])
    drone_["reconnect_time"] = format_datetime(drone["reconnect_time"])
    return drone_


def jsonyfied_drones():
    return list(map(lambda x: jsonify_drone_data(x), drones))


def jsonify_logs_data(log_msg):
    log_msg_ = copy.deepcopy(log_msg)
    log_msg_["time"] = format_datetime(log_msg_["time"])
    return log_msg_


def jsonyfied_logs():
    return list(map(lambda x: jsonify_logs_data(x), logs))


def format_datetime(dtm):
    return dtm.strftime("%d.%m.%y %H:%M:%S")


def deformat_datetime(string):
    return datetime.datetime.strptime(string, "%d.%m.%y %H:%M:%S")


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
        return {"code": "400"}

    ip = str(request.remote_addr)
    mac = args["mac_address"]

    drones[mac]["ip"] = ip
    drones[mac]["last_ping_time"] = datetime.datetime.now()

    return {'code': '200'}


@app.route('/connect', methods=["GET"])
def connect_drone():
    args = dict(request.args)
    if "mac_address" not in args or not drone_mac_is_valid(args["mac_address"]):
        return {"code": "400"}

    ip = str(request.remote_addr)
    mac = args["mac_address"]
    if mac not in drones:
        drones[mac] = {"name": generate_nickname(), "ip": ip}

    drones[mac]["ip"] = ip
    drones[mac]["mac_address"] = args["mac_address"]
    drones[mac]["reconnect_time"] = datetime.datetime.now()
    drones[mac]["last_ping_time"] = datetime.datetime.now()

    return "{'code': '200'}"


@app.route('/command', methods=["GET"])
def command_handler():
    args = dict(request.args)
    if "mac_address" not in args or args["mac_address"] not in drones:
        return "Wrong MAC Address"
    mac = args["mac_address"]
    command = args["command"]
    completed = send_socket_message(mac, command)
    return redirect(url_for('drones')) if completed else "Failed to send command"


@app.route('/drones')
def drones_viewer():
    current_time = get_timestamp()
    for drone in drones:
        send_socket_message(drone, "ping")
    for drone_mac in drones:
        drone = drones[drone_mac]
        offline_time = current_time - drone["last_ping_time"]
        drones[drone_mac]["offline_time"] = offline_time.seconds
    return render_template("drone_list.html", drones=list(drones.values()))


@app.route('/get_key')
def key_reciever():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return str(password)


@app.route('/report', methods=["GET"])
def error_report_handler():
    args = dict(request.args)
    if "message" in args:
        errors.append({"text": args["message"], "time": datetime.datetime.now()})
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

    if "message" in args:
        logs.append({"text": args["message"], "time": datetime.datetime.now()})
        socketio.emit('message', jsonyfied_logs(), broadcast=True)
        return "logged"
    else:
        return "wrong parameters"


@app.route('/live_log')
def live_logging():
    socketio.emit("message", jsonyfied_logs(), broadcast=True)
    return render_template("live_log.html")


print(f"http://{HOST}:{PORT}/drones")
socketio.run(app, host='0.0.0.0', port=PORT)
app.run()

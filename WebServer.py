from flask import Flask
from flask import request
import socket
import secrets
import string

DRONE_KEYS = ['XtVT7Fy8jQ']
app = Flask(__name__)
drones = {}


def drone_key_is_valid(key):
    return key in DRONE_KEYS


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
    if "key" not in args or not drone_key_is_valid(args["key"]):
        return "Access denied!"
    ip = str(request.remote_addr)
    key = args["key"]
    if key not in drones:
        drones[key] = {"name": generate_nickname(), "ip": ip}
    drones[key]["ip"] = ip
    drones[key]["title"] = "Hello, world!"
    return f"{drones[key]}"


@app.route('/drones')
def drones_viewer():
    return str(drones)


@app.route('/get_key')
def key_reciever():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return str(password)


print(socket.gethostbyname(socket.gethostname()))
app.run(host='0.0.0.0', port=8090)

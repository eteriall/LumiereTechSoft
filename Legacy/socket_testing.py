import os
import socket
import sys

IP = "192.168.1.9"
PORT = 80
message = "hi"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))
sock.send(message.encode("utf-8"))
data = sock.recv(1024)
if data is None:
    print("Could not connect to the drone.")
    sys.exit()
data = list(map(lambda x: x.split("="), data.decode("utf-8").split(";")))[:-1]
data = {key: val for key, val in data}
print(data)
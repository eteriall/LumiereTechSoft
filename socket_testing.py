import os
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("172.20.43.13", 80))
sock.send(b"enable_all")
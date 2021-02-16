import PyQt5
import pygame
from PyQt5.QtWidgets import QFileDialog, QApplication

import json
import socket
import sys
import time
import math


def human_read_format(size):
    if size == 0:
        return "0Б"
    size_name = ("Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "ЕБ", "ЗБ")
    i = math.floor(math.log(size, 1024))
    return f"{round(size / (1024 ** i))}{size_name[i]}"


def exp_h(*args):
    sys.__excepthook__(*args)


def send_socket_message(ip, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 80))
    sock.send(message.encode("utf-8"))
    data = sock.recv(2)


sys.excepthook = exp_h
SW, SH = 500, 500
FPS = 60
app = QApplication(sys.argv)

with open(str(QFileDialog.getOpenFileName(None, "Select Show File", filter="*.lumiere",
                                          directory=r"C:\Users\d1520\Desktop\Lumiere\LumiereTechSoft\Shows\shows")[
                  0])) as f:
    commands = f.read().split("\n")
    print(human_read_format(sys.getsizeof(commands)))
    music, *commands = commands
    commands = list(map(lambda x: x.split("-"), commands))
    command_index = 0

run = True
color = (4, 33, 39)

CHOSEN_DRONE_IP = "192.168.1.7"
send_socket_message(CHOSEN_DRONE_IP, json.dumps({"ss": len(commands)}))
x = 0
l = False
commands = commands[:500] if len(commands) > 500 else commands
for line in commands:
    print(f"{x + 1} из {len(commands)} загружено")
    if x > 100 and not l:
        send_socket_message(CHOSEN_DRONE_IP, json.dumps({"rs": 1}))
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)
        screen = pygame.display.set_mode((100, 100))
        l = True
    try:
        time = line[0]
        if len(line[1:]) > 1:
            command = "-".join(line[1:])
        else:
            command = line[1]
        drone_mdg = {"se": json.dumps({"cd": json.loads(command), "t": int(time)}), "ei": x}
        print(drone_mdg)
        send_socket_message(CHOSEN_DRONE_IP, json.dumps(drone_mdg))
        x += 1
    except:
        pass

while True:
    pygame.display.update()

import json
import socket
import sys
import time

import pygame
import PyQt5
from pygame import gfxdraw
from PyQt5.QtWidgets import QFileDialog, QApplication


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
    music, *commands = commands
    commands = list(map(lambda x: x.split("-"), commands))
    command_index = 0

screen = pygame.display.set_mode((SW, SH))
res = []

clock = pygame.time.Clock()
run = True
color = (4, 33, 39)

pygame.mixer.init()
pygame.mixer.music.load(music)
pygame.mixer.music.play(-1)
start_time = time.time()

while run:
    screen.fill((0, 0, 0))
    events = pygame.event.get()
    millis = int((time.time() - start_time) * 1000)
    try:
        c = commands[command_index]
        ctime, ctext = c[0], c[1]
        ctime = int(ctime)
        if ctime <= millis:
            send_socket_message("192.168.1.9", ctext)
            command_index += 1

    except IndexError:
        pass

    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()

    gfxdraw.filled_circle(screen, SW // 2, SH // 2, 100, color)
    pygame.display.flip()

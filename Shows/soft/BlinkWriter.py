import json
import socket
import sys
import time

import pygame
import PyQt5
from pygame import gfxdraw
from PyQt5.QtWidgets import QFileDialog, QApplication


def send_socket_message(ip, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 80))
    sock.send(message.encode("utf-8"))
    data = sock.recv(10)


def exp_h(*args):
    sys.__excepthook__(*args)


sys.excepthook = exp_h
SW, SH = 500, 500
FPS = 60
app = QApplication(sys.argv)
music = str(QFileDialog.getOpenFileName(None, "Select Audio", filter="*.mp3",
                                        directory=r"C:\Users\d1520\Desktop\Lumiere\LumiereTechSoft\Shows\music")[0])
screen = pygame.display.set_mode((SW, SH))
res = []

clock = pygame.time.Clock()
run = True


def color_lerp(current, goal, amount=50):
    new = list(current[:])
    for c1, c2, i in zip(current, goal, range(len(goal))):
        if c1 > c2:
            new[i] = max(c2, c1 - amount)
        if c1 < c2:
            new[i] = min(c2, c1 + amount)
    return new


color = (4, 33, 39)
color2 = (4, 33, 39)
tcolor = (4, 33, 39)
tcolor2 = (4, 33, 39)
pygame.mixer.init()
pygame.mixer.music.load(music)
pygame.mixer.music.play(-1)
start_time = time.time()

while run:
    screen.fill((0, 0, 0))
    events = pygame.event.get()
    millis = int((time.time() - start_time) * 1000)

    ev_hpnd = True
    params = {}
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                params["b_led1"] = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_q:
                params["b_led1"] = 0

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                params["b_led2"] = 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_e:
                params["b_led2"] = 0

            else:
                if params == {}:
                    ev_hpnd = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            print("a")
            run = False

    if params != {}:
        print(params)
        res += [(millis, json.dumps(params))]
        send_socket_message("192.168.1.9", json.dumps(params))

    if "b_led1" in params and params["b_led1"] == 1:
        tcolor = (255, 255, 255)
    if "b_led1" in params and params["b_led1"] == 0:
        tcolor = (4, 33, 39)

    if "b_led2" in params and params["b_led2"] == 1:
        tcolor2 = (255, 255, 255)
    if "b_led2" in params and params["b_led2"] == 0:
        tcolor2 = (4, 33, 39)

    color = color_lerp(color, tcolor)
    color2 = color_lerp(color2, tcolor2)

    gfxdraw.aacircle(screen, 160, SH // 2, 50, list(map(int, color)))
    gfxdraw.aacircle(screen, 340, SH // 2, 50, list(map(int, color2)))
    pygame.display.flip()
    clock.tick(60)

with open(str(QFileDialog.getSaveFileName(None, "Save show", filter="*.lumiere")[0]), mode="w") as f:
    f.write(music + "\n")
    print(res)
    for time, command in res:
        f.write(f"{time}-{command}\n")

import json
import socket
import sys
import time


def send_socket_message(ip, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.1.9", 80))
    try:
        sock.send(message.encode("utf-8"))
        data = sock.recv(2)
    except:
        pass


res = {0: {'strength': 0.0, 'pos': (23.893774032592773, 26.049346923828125, 31.161624908447266)},
       290: {'strength': 10.0, 'pos': (27.623510360717773, 22.171112060546875, 21.1782169342041)},
       331: {'strength': 10.0, 'pos': (28.52263069152832, 21.535032272338867, 19.540809631347656)},
       338: {'strength': 0.0, 'pos': (28.679527282714844, 21.437864303588867, 19.290674209594727)},
       450: {'strength': 10.0, 'pos': (31.215129852294922, 20.591957092285156, 17.113136291503906)},
       618: {'strength': 10.0, 'pos': (33.604557037353516, 20.591957092285156, 33.84279251098633)}}

lf_index = 0
last_frame = list(res.keys())[lf_index]
while True:
    ex_time = (last_frame / 60) * 1000
    millis = int(time.time() * 1000)
    if ex_time <= millis:
        lf_index += 1
        v = res[last_frame]["strength"]
        try:
            last_frame = list(res.keys())[lf_index]
            if v >= 5:
                send_socket_message("192.168.1.9", json.dumps({"b_led1": 1}))
            else:
                send_socket_message("192.168.1.9", json.dumps({"b_led1": 0}))
        except:
            sys.exit()

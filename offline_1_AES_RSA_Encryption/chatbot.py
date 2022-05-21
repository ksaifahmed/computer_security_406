from audioop import add
from ctypes.wintypes import tagRECT
from re import T
import socket
import threading

USER_ID = 0
PORT = 6000
CHUNK_SIZE = 1024
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def receiver_handler(conn, addr):
    global USER_ID
    USER_ID += 1
    print(f"user id = {USER_ID}, address = {addr} connected!")

    while True:
        msg = conn.recv(CHUNK_SIZE).decode(FORMAT)
        if msg:
            print(f"From [{addr}]: {msg}")
            conn.send(msg.upper().encode(FORMAT))


def init_server():
    server.listen()
    print("Starting chatbot server...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=receiver_handler, args=(conn, addr))
        thread.start()

thread = threading.Thread(target=init_server)
thread.start()



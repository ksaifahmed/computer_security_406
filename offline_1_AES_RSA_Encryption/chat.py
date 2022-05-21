import socket
import threading

PORT = 6000
CHUNK_SIZE = 1024
SERVER_IP = "192.168.1.104"
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'


def receiver_handler(conn):
    print(f"connected to server-ip: {SERVER_IP}")

    while True:
        msg = conn.recv(CHUNK_SIZE).decode(FORMAT)
        if msg:
            print(f"SERVER [{SERVER_IP}]: {msg}")

def sender(client):
    while True:
        msg = input()
        client.send(msg.encode(FORMAT))


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
thread = threading.Thread(target=receiver_handler, args=(client,))
thread.start()
sender(client)
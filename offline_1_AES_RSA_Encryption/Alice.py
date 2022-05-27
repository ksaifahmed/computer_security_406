import os
import pickle
import socket
import threading
from AES import AES_Encryption, key_scheduling
from RSA import RSAEncryption, key_pair_generation

# networking ===================
PORT = 6000
CHUNK_SIZE = 1024
SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'


# RSA VALUE OF "K"
RSA_K = 128

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


# main handler function
def handler(conn, addr):
    print(f"user with address = {addr} connected!")

    while True:
        print("Enter text to send:")
        plain_text = input()
        print("Enter key:")
        key = input()

        # encryption
        round_keys = key_scheduling(key)
        cipher_text = AES_Encryption(plain_text, round_keys)
        e, n, d = key_pair_generation(RSA_K)
        print(f"Keys generated: ======================\ne: {e}, n: {n}, d: {d}\n")
        cipher_keys = RSAEncryption(key, e, n)

        # create new folder and write
        newpath = r'.\secret_folder' 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        f = open(newpath+"\key.txt", "w")
        f.write(str(d))
        f.close()

        # send data
        conn.send(cipher_text)
        msg = conn.recv(CHUNK_SIZE).decode(FORMAT) # ACK
        conn.send(pickle.dumps(cipher_keys))
        msg = conn.recv(CHUNK_SIZE).decode(FORMAT) # ACK
        conn.send(str(n).encode(FORMAT))

        # perform matching
        msg = conn.recv(CHUNK_SIZE).decode(FORMAT) # WAIT FOR DECRYPTION ACK
        decrypted_text = ""
        if msg == "Decrypted":
            f = open(newpath+"\message.txt", "r")
            decrypted_text = f.read()
            print("Decrypted text from file: \n" + decrypted_text, end="\n\n")
            f.close()

        
            

def init_server():
    server.listen()
    print("Starting server...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handler, args=(conn, addr))
        thread.start()

thread = threading.Thread(target=init_server)
thread.start()



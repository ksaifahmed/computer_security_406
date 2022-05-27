from copyreg import pickle
from pydoc import plain
import socket
import pickle
import threading

from RSA import RSADecryption, convert_to_strs
from AES import AES_Decryption, key_scheduling

PORT = 6000
CHUNK_SIZE = 1024
SERVER_IP = "192.168.1.104"
ADDR = (SERVER_IP, PORT)
FORMAT = 'utf-8'


def receiver_handler(conn):
    print(f"connected to server-ip: {SERVER_IP}")

    while True:
        # encrypted text from ALICE
        cipher_text = conn.recv(CHUNK_SIZE)
        conn.send("ACK".encode(FORMAT))

        # encrypted keys
        cipher_keys = conn.recv(CHUNK_SIZE)
        cipher_keys = pickle.loads(cipher_keys)
        conn.send("ACK".encode(FORMAT))
        
        # public RSA key "n"
        public_key = conn.recv(CHUNK_SIZE).decode(FORMAT)
        
        # reading private key from folder
        newpath = r'.\secret_folder' 
        f = open(newpath+"\key.txt", "r")
        private_key = int(f.read())
        f.close()

        # decrypting the AES key
        aes_key = RSADecryption(cipher_keys, private_key, int(public_key))
        aes_key = convert_to_strs(aes_key)

        # decrypting the message
        round_keys = key_scheduling(aes_key)
        plain_text = AES_Decryption(bytearray(cipher_text), round_keys)
        
        # writing plain text in file
        f = open(newpath+"\message.txt", "w")
        plain_text = ("".join(map(chr, plain_text))).rstrip(chr(4))
        f.write(plain_text)
        f.close()

        print(cipher_text, end=" [cipher_text]\n\n")
        print(cipher_keys, end=" --- [encrypted symmetric key]\n\n")
        print(public_key, end=" [public key 'n']\n\n")
        print(private_key, end=" [private key 'd']\n\n")
        print(plain_text, end=" [plain text]\n\n")

        # ACK THAT TASK IS DONE
        conn.send("Decrypted".encode(FORMAT))


def sender(client):
    while True:
        msg = input()
        client.send(msg.encode(FORMAT))


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
thread = threading.Thread(target=receiver_handler, args=(client,))
thread.start()
sender(client)
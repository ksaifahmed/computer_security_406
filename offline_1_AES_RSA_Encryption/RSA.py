from BitVector import *
import math
import time

def str_to_hex(key):
    key_list = bytes(key, 'ascii')
    return bytearray(key_list)


# key pair generation ====================================================
def key_pair_generation(k):
    bit_size = int(k/2)
    p = BitVector(intVal = 0)
    q = BitVector(intVal = 0)
    e = BitVector(intVal = 0)

    # generate p, q   
    while True:
        p = p.gen_random_bits(bit_size)  
        check = p.test_for_primality()
        if check > 0.9:
            break
    while True:
        q = q.gen_random_bits(bit_size)  
        check = q.test_for_primality()
        if check > 0.99:
            break    
    
    n = p.int_val() * q.int_val()
    phi = (p.int_val() - 1) * (q.int_val() - 1)

    # coprime 'e'
    while True:
        e = e.gen_random_bits(phi.bit_length()-1)
        if math.gcd(e.int_val(), phi) == 1:
            break
    
    phi = BitVector(intVal = phi)   
    d = e.multiplicative_inverse(phi)
    return e.int_val(), n, d.int_val()


# RSA encryption ====================================================
def RSAEncryption(text, e, n):
    text = str_to_hex(text)
    cipher = []
    for char in text:
        cipher.append(pow(int(char), e, n))
    return cipher

def RSADecryption(text, d, n):
    plain = []
    for char in text:
        plain.append(pow(int(char), d, n))
    return plain
# RSA decryption ====================================================


def convert_to_strs(list):
    return ''.join(chr(i) for i in list)


def run_single(k, plain_text):
    start = time.time()
    e, n, d = key_pair_generation(k)
    key_gen_time = time.time() - start
    print(f"Keys generated: ======================\ne: {e}, n: {n}, d: {d}\n")
    
    start = time.time()
    cipher = RSAEncryption(plain_text, e, n)
    cipher_time = time.time() - start
    print("Cipher Text: =========================")
    print(cipher, end="\n\n")

    start = time.time()
    plain = RSADecryption(cipher, d, n)
    decipher_time = time.time() - start
    print("Deciphered Text: =========================")        
    print(convert_to_strs(plain) + " --- [IN ASCII]")
    print(plain, end=" --- [IN ASCII VALUES]\n")
    
    return key_gen_time, cipher_time, decipher_time


def run_stats(plain_text):
    k_list = [16, 32, 64, 128, 256, 512, 1024]
    data = ""
    for k in k_list:
        kt, ct, dt = run_single(k, plain_text)
        data += "k=" + str(k) + ", key_gen=" + str(kt) + ", enc=" + str(ct) + ", dec=" + str(dt) + "\n"
    
    print("\n\n\n=====================DATA GENERATED==============================\n")
    print(data)





if __name__ == "__main__":
    print("\nTest performance --> 1")
    print("Test individually --> any key")

    comm = input()
    if comm == "1":
        print("Enter plain text")
        plain_text = input()
        print("\n")
        run_stats(plain_text)
    else:
        print("Enter value of k:")
        k = input()
        print("Enter plain text")
        plain_text = input()
        print("\n")

        key_gen_time, cipher_time, decipher_time = run_single(int(k), plain_text)        
        print("Execution Time:")
        print(f"Key Generation: {key_gen_time} seconds")
        print(f"Encryption Time: {cipher_time} seconds")
        print(f"Decryption Time: {decipher_time} seconds")

import string
from BitVector import *
from bitvectordemo import *
import time


# required values ================================================
info_keys = {
    16: (10, 4, 44),
    24: (8, 6, 52),
    32: (7, 8, 60),
}
round_len = {
    176: 9,
    208: 11,
    240: 13,
}
BLOCK_SIZE = 16
PADDER_ASCII = 4 #diamond


# KEY EXPANSION START ================================================
# string to tuple of hexes
def str_to_hex(key):
    key_list = bytes(key, 'ascii')
    return bytearray(key_list)


def circular_left_shift(w_):
    first = w_[0]
    for i in range(len(w_)-1):
        w_[i] = w_[i+1]
    w_[-1] = first
    return w_


def byte_sub(w_):
    for i in range(len(w_)):
        r = w_[i] >> 4;
        c = w_[i] & 0b00001111;
        w_[i] = Sbox[r*16+c]
    return w_


# the 'g' function
def block_g(w_, rc):
    w_ = circular_left_shift(w_)
    w_ = byte_sub(w_)
    w_[0] ^= rc
    return w_


# print byte array in hex
def print_in_hex(byte_arr):
    res = ""
    count = 0
    for b in byte_arr:
        res += "%02x" % b
        count += 1
        if count == BLOCK_SIZE:
            res += "\n"
            count = 0;   
    if(res[-1] == "\n"):
        res = res.rstrip("\n")
    print(res+" [IN HEX]")


# calculates round constant
def rc(round):
    if round == 1:
        return 1
    elif rc(round-1) < 128:
        return 2*rc(round-1)
    else:
        return (2*rc(round-1)) ^ 283


# key scheduling/expansion
def key_scheduling(key):
    round_keys = str_to_hex(key)
    key_count = len(key)/4
    rounds, w_len, max_key = info_keys[len(key)]
    start = 0

    for i in range(rounds):
        w_0 = round_keys[start:4+start]
        start += 4 * (w_len-1) #goes to last word
        w_n = round_keys[start:4+start]
        start -= 4 * (w_len-2) #comes back

        g = block_g(w_n, rc(i+1))
        w_4 = bytes([aa ^ bb for aa, bb in zip(g, w_0)])
        round_keys += w_4
        key_count += 1 #increase key count

        if key_count == max_key:
            return round_keys

        for j in range(w_len-1):
            w_j = bytes([aa ^ bb for aa, bb in zip(w_4, round_keys[start:4+start])])
            w_4 = w_j
            round_keys += w_j
            start += 4

            key_count += 1 #increase key count
            if key_count == max_key:
                return round_keys
    
    return round_keys
# KEY EXPANSION END ================================================




# AES ENCRYPTION START ================================================
# padding
def padd_text(text):
    i, count = PADDER_ASCII, BLOCK_SIZE - len(text)
    text += bytearray((i,)) * count
    return text


def add_rc(text, keys):
    for i in range(len(keys)):
        text[i] ^= keys[i]
    return text


def shift_row(text):
    text[1], text[5], text[9], text[13] = text[5], text[9], text[13], text[1]
    text[2], text[6], text[10], text[14] = text[10], text[14], text[2], text[6]
    text[3], text[7], text[11], text[15] = text[15], text[3], text[7], text[11]
    return text


def mix_col(text):
    text_mat = []
    start = 0
    for j in range(4):
        row = []
        for i in range(4):
            row.append(BitVector(intVal=text[i+start], size=8))
        start += 4
        text_mat.append(row)
    
    text_mat = list(map(list, zip(*text_mat))) # transpose
    AES_modulus = BitVector(bitstring='100011011')

    for i in range(4):
        for j in range(4):
            text[i+4*j] = 0b00000000
            for k in range(4):
                ans = Mixer[i][k].gf_multiply_modular(text_mat[k][j], AES_modulus, 8)
                text[i+4*j] ^= ans.int_val()
    
    return text


def AES_Encrypt(text, round_keys):
    rounds = round_len[len(round_keys)]
    start = 0
    cipher_text = add_rc(text, round_keys[start:start+BLOCK_SIZE])
    start += BLOCK_SIZE

    for i in range(rounds):
        cipher_text = mix_col(shift_row(byte_sub(cipher_text)))
        cipher_text = add_rc(cipher_text, round_keys[start:start+BLOCK_SIZE])
        start += BLOCK_SIZE

    cipher_text = shift_row(byte_sub(cipher_text))
    cipher_text = add_rc(cipher_text, round_keys[start:start+BLOCK_SIZE])
    return cipher_text


def AES_Encryption(plain_text, round_keys):
    plain_text = str_to_hex(plain_text)
    factor = len(plain_text)/BLOCK_SIZE
    cipher_text = bytearray()
    start = 0
    
    for i in range(int(factor)):
        cipher_text += AES_Encrypt(plain_text[start:start+BLOCK_SIZE], round_keys)
        start += BLOCK_SIZE
    
    if factor > int(factor):
        padded_text = padd_text(plain_text[start:start+BLOCK_SIZE])
        cipher_text += AES_Encrypt(padded_text, round_keys)
    
    return cipher_text

# AES ENCRYPTION END ================================================



# AES DECRYPTION START ================================================
def inv_shift_row(text):
    text[1], text[5], text[9], text[13] = text[13], text[1], text[5], text[9]
    text[2], text[6], text[10], text[14] = text[10], text[14], text[2], text[6]
    text[3], text[7], text[11], text[15] = text[7], text[11], text[15], text[3]
    return text


def inv_mix_col(text):
    text_mat = []
    start = 0
    for j in range(4):
        row = []
        for i in range(4):
            row.append(BitVector(intVal=text[i+start], size=8))
        start += 4
        text_mat.append(row)
    
    text_mat = list(map(list, zip(*text_mat))) # transpose
    AES_modulus = BitVector(bitstring='100011011')

    for i in range(4):
        for j in range(4):
            text[i+4*j] = 0b00000000
            for k in range(4):
                ans = InvMixer[i][k].gf_multiply_modular(text_mat[k][j], AES_modulus, 8)
                text[i+4*j] ^= ans.int_val()
    
    return text


def inv_byte_sub(w_):
    for i in range(len(w_)):
        r = w_[i] >> 4;
        c = w_[i] & 0b00001111;
        w_[i] = InvSbox[r*16+c]
    return w_


def AES_Decrypt(text, round_keys):
    rounds = round_len[len(round_keys)]
    start = len(round_keys)-BLOCK_SIZE
    plain_text = add_rc(text, round_keys[start:start+BLOCK_SIZE])
    start -= BLOCK_SIZE

    for i in range(rounds):
        plain_text = inv_byte_sub(inv_shift_row(plain_text))
        plain_text = add_rc(plain_text, round_keys[start:start+BLOCK_SIZE])        
        plain_text = inv_mix_col(plain_text)
        start -= BLOCK_SIZE

    plain_text = inv_byte_sub(inv_shift_row(plain_text))
    plain_text = add_rc(plain_text, round_keys[start:start+BLOCK_SIZE])
    return plain_text


def AES_Decryption(cipher_text, round_keys):
    if type(cipher_text) is str:
        cipher_text = str_to_hex(cipher_text)
    
    factor = len(cipher_text)/BLOCK_SIZE
    plain_text = bytearray()
    start = 0
    
    for i in range(int(factor)):
        plain_text += AES_Decrypt(cipher_text[start:start+BLOCK_SIZE], round_keys)
        start += BLOCK_SIZE
    
    return plain_text

# AES DECRYPTION END ================================================





if __name__ == "__main__":
    print("Enter plain text:")
    plain_text = input()
    print("Enter key:")
    key = input()
    len_k = len(key)
    
    if len_k not in [16, 24, 32]:
        print(f"Invalid size of key: {len_k}!")
    else:
        print("\n\nPlain Text:")
        print(plain_text+" [IN ASCII]")
        print_in_hex(str_to_hex(plain_text))
        print("")
        
        print("Key:")
        print(key+" [IN ASCII]")
        print_in_hex(str_to_hex(key))
        print("")

        start = time.time()
        round_keys = key_scheduling(key)
        # print_in_hex(round_keys)
        stop = time.time()
        key_gen_time = stop - start

        start = time.time()
        cipher = AES_Encryption(plain_text, round_keys)
        cipher_time = time.time() - start
        print("Cipher Text:")
        print_in_hex(cipher)
        cipher_text = "".join(map(chr, cipher))
        print(cipher_text, end=" [IN ASCII]\n\n")

        start = time.time()
        plain = AES_Decryption(cipher, round_keys)
        decipher_time = time.time() - start
        print("Deciphered Text:")
        print_in_hex(plain)
        
        plain = ("".join(map(chr, plain))).rstrip(chr(4))
        print(plain, end=" [IN ASCII]\n\n")

        print("Execution Time:")
        print(f"Key Scheduling: {key_gen_time} seconds")
        print(f"Encryption Time: {cipher_time} seconds")
        print(f"Decryption Time: {decipher_time} seconds")                
        

    
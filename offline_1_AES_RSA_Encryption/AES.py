from BitVector import *
from bitvectordemo import *
import time

info_keys = {
    16: (10, 4),
    24: (12, 6),
    32: (14, 8),
}

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
def print_in_hex(byte_arr, length):
    res = ""
    count = 0
    for b in byte_arr:
        res += "%02x " % b
        count += 1
        if count == length:
            res += "\n"
            count = 0;   
    print(res.upper())

# calculates round constant
def rc(round):
    if round == 1:
        return 1
    elif rc(round-1) < 128:
        return 2*rc(round-1)
    else:
        return (2*rc(round-1)) ^ 283


# key scheduling/expansion
round_keys = tuple()
def key_scheduling(key):
    global round_keys
    round_keys = str_to_hex(key)
    rounds, w_len = info_keys[len(key)]
    start = 0

    for i in range(rounds):
        w_0 = round_keys[start:4+start]
        print_in_hex(w_0, 10)
        start += 4 * (w_len-1) #goes to last word
        w_n = round_keys[start:4+start]
        start -= 4 * (w_len-2) #comes back

        g = block_g(w_n, rc(i+1))
        w_4 = bytes([aa ^ bb for aa, bb in zip(g, w_0)])
        round_keys += w_4

        for j in range(w_len-1):
            w_j = bytes([aa ^ bb for aa, bb in zip(w_4, round_keys[start:4+start])])
            w_4 = w_j
            round_keys += w_j
            start += 4
    
    print_in_hex(round_keys, len(key))
    return round_keys
    

if __name__ == "__main__":
    print("Enter key:")
    key = input()
    len_k = len(key)
    
    if len_k not in [16, 24, 32]:
        print(f"Invalid size of key: {len_k}!")
    else:
        start = time.time()
        key_scheduling(key)
        stop = time.time()
        print(f"Elapsed time: {stop - start}")

    
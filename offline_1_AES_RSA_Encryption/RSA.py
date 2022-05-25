from BitVector import *
import math

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



print(key_pair_generation(32))
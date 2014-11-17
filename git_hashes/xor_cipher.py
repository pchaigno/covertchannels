#!/usr/bin/env python3

import random
import binascii


"""Generates the key for the XOR operation
Args:
        length: the length of the generated key.        
"""
def genkey(length, seed):
    random.seed(seed)
    k = []
    for ii in range(0,length):
        k.append(random.randint(0,255))
    return k

"""Converts a string into a list of hex values
Args:
       message: the message to encode
"""
def string_to_hex(message):
    m = []
    for c in message:
        m.append(ord(c))
    return m
    
"""Converts a hex list into string
Args:
       hexl: the message to decode
"""
def hex_to_string(hexl):
    m = ""
    for c in hexl:
        m = m + chr(c) 
    return m

"""Computes xor value for two hex values
Args:
       h1: the first hex value
       h2: the second hex value
"""
def xor_hex(s,t):
    xorl = []
    for ii in range(0,len(s)):
        xorl.append(s[ii]^t[ii])
    return xorl

"""Generates the message to transmit in the hash
Args:
        hexl: the list of hex values
"""
def generate_message_to_transmit(hexl):
    m = ""
    for ii in hexl:
        if len(hex(ii)) == 3:
            m = m + hex(0)[2]+ hex(ii)[2]
        else:
            m = m + hex(ii)[2] + hex(ii)[3]
    return m

"""Transform the hash received to a list of hex values
Args:
       hashr: the hash received
"""
def hash_received_to_hexl(hashr):
    mes = []
    for ii in range(0,int(len(hashr)/2)):
        val = hashr[ii*2]+hashr[ii*2+1]
        val = int(val,16)
        mes.append(val)
    return mes
    
    
if __name__ == "__main__":    
    s = "123kdjrgiu"
    mess = "this is a secret message"
    print(mess)
    hexl = string_to_hex(mess)
    k = genkey(len(hexl),s)
    mx = xor_hex(k,hexl)
    mxt = generate_message_to_transmit(mx)
    print(mxt)
    mh = hash_received_to_hexl(mxt)
    m = xor_hex(mh, k)
    f = hex_to_string(m)
    print(f)

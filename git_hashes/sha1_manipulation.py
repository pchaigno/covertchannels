#!/usr/bin/env python3
import sys;
import hashlib;
import time;

text = sys.argv[1]
lettersWanted = sys.argv[2]
offset = 0
if len(sys.argv) > 3:
	offset = int(sys.argv[3])

sha1 = str(hashlib.sha1(text.encode('utf-8')).hexdigest())
print(sha1)



start_time = time.time()
while sha1[offset:offset+len(lettersWanted)] != lettersWanted:
	text += '\n'
	sha1 = hashlib.sha1(text.encode('utf-8')).hexdigest()

print("--- %s seconds ---" % (time.time() - start_time))
print(len(text) - len(sys.argv[1]))
print(sha1)

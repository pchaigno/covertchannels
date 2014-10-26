#!/usr/bin/env python3
import sys
import string
import hashlib
import time
import space_encoding

def partial_collision(message, collision, offset):
	sha1 = str(hashlib.sha1(message.encode('utf-8')).hexdigest())
	encoded_spaces = '0';
	while sha1[offset: offset + len(collision)] != collision:
		encoded_spaces = space_encoding.increment(encoded_spaces)
		spaces = space_encoding.decode(encoded_spaces)
		sha1 = hashlib.sha1((message + spaces).encode('utf-8')).hexdigest()
	return encoded_spaces

if __name__ == "__main__":
	comment = sys.argv[1]
	message = sys.argv[2]
	offset = 0
	if len(sys.argv) > 3:
		offset = int(sys.argv[3])

	sha1 = str(hashlib.sha1(comment.encode('utf-8')).hexdigest())
	print(comment)
	print(sha1)

	start_time = time.time()
	encoded_spaces = partial_collision(comment, message, offset)

	print()
	print("--- %s seconds ---" % (time.time() - start_time))
	print()
	print(encoded_spaces)
	print(comment + space_encoding.decode(encoded_spaces) + "EOL")
	print(sha1)

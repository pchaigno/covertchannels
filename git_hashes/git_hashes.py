#!/usr/bin/env python3
import sys;
import string;
import hashlib;
import time;

def increment(string):
	new_string = ''
	all_1 = True
	for bit in string:
		if bit == '0':
			all_1 = False
			break
	if all_1:
		new_string += '1'
		for bit in string:
			new_string += '0'
	else:
		new_string = '{:0{}b}'.format(int(string, 2) + 1, len(string))
	return new_string

def to_spaces(string):
	spaces = "";
	for bit in string:
		if bit == '0':
			spaces += " "
		else:
			spaces += "	"
	return spaces

def partial_collision(message, collision, offset):
	spaces = '0';
	while sha1[offset: offset + len(message)] != message:
		spaces = increment(spaces)
		sha1 = hashlib.sha1((comment + to_spaces(spaces)).encode('utf-8')).hexdigest()

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
	partial_collision(comment, message, offset)

	print()
	print("--- %s seconds ---" % (time.time() - start_time))
	print()
	print(spaces)
	print(comment + to_spaces(spaces) + "EOL")
	print(sha1)

#!/usr/bin/env python3
import sys;
import string;

"""Increments the binary encoding by one.

If the last encoded space string was the maximum, the length of the string is increased.
Otherwise, the binary value is just increased.
110 => 111
111 => 0001

Args:
	string: The encoded string.

Returns:
	The new encoded string.
"""
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


"""Decodes a string of encoded spaces.

Converts the encoded spaces (as binary) into actual spaces and tabulations.
A 0 becomes a white space and a 1 becomes a tabulation.

Args:
	string: The spaces encoded in binary.

Returns:
	The string of spaces and tabulations.
"""
def decode(string):
	spaces = "";
	for bit in string:
		if bit == '0':
			spaces += " "
		else:
			spaces += "	"
	return spaces


if __name__ == "__main__":
	string = '0'
	for i in range(0, 20):
		print(string + ":" + to_spaces(string) + "\\")
		string = increment(string)

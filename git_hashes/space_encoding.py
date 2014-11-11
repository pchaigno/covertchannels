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
        return '{:0{}b}'.format(int(string, 2) + 1, len(string))


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
                print(string + ":" + decode(string) + "\\")
                string = increment(string)

        print ("Unit test for space_encoding: should return no falses")
        print(increment('100') == '101')
        print(increment('1111') == '10000')
        print(increment('1101') == '1110')
        print(increment('1101') != '1111')        
        print(decode('10') == '\t ')
        print(decode('10101') == '\t \t \t')
        print(decode('1101') != ' \t\t \t')

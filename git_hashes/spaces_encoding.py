#!/usr/bin/env python3
import sys;
import string;

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


string = '0'
for i in range(0, 20):
	print(string + ":" + to_spaces(string) + "\\")
	string = increment(string)
#!/usr/bin/env python3
import sys
import string
import hashlib
import time
import space_encoding

"""Find a partial collision on the hash of a git commit.

Args:
	header: The information for this commit which is encoded to generate the hash (without the commit message).
	message: The commit message.
	collision: The hexadecimal characters to obtain in the hash.
	offset: The offset where the hidden characters (collision) should be found in the hash.

Return:
	The spaces added to the commit message for the collision encoded as binary.
"""
def partial_collision(header, message, collision, offset):
	complete_header = header + message
	sha1 = str(hashlib.sha1(complete_header.encode('utf-8')).hexdigest())
	encoded_spaces = '0';
	while sha1[offset: offset + len(collision)] != collision:
		encoded_spaces = space_encoding.increment(encoded_spaces)
		spaces = space_encoding.decode(encoded_spaces)
		complete_header = header + message + spaces
		sha1 = hashlib.sha1(complete_header.encode('utf-8')).hexdigest()
	return encoded_spaces


"""Find a partial collision on the hash of a git commit.

Args:
	comment: The commit message.
	message: The hexadecimal characters to obtain in the hash.
	offset: The offset where the hidden characters (collision) should be found in the hash.
"""
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: git_hashes.py <comment> <message> [<offset>]")
		sys.exit(2)

	header = "commit 327tree 9bedf67800b2923982bdf60c89c57ce6fd2d9a1c\nparent de1eaf515ebea46dedea7b3ae0e5ebe3e1818971\nauthor jnthn <jnthn@jnthn.net> 1334500503 +0200\ncommitter jnthn <jnthn@jnthn.net> 1334500545 +0200\n\n"
	comment = sys.argv[1]
	message = sys.argv[2]
	offset = 0
	if len(sys.argv) > 3:
		offset = int(sys.argv[3])

	complete_header = header + comment
	sha1 = str(hashlib.sha1(complete_header.encode('utf-8')).hexdigest())
	print(complete_header)
	print(sha1)

	start_time = time.time()
	encoded_spaces = partial_collision(header, comment, message, offset)

	print()
	print("--- %s seconds ---" % (time.time() - start_time))
	print()
	print(encoded_spaces)
	print(comment + space_encoding.decode(encoded_spaces) + "EOL")
	print(sha1)

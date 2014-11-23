#!/usr/bin/env python3
import sys
import string
import hashlib
import time
import space_encoding

"""Find a partial collision on the hash of a git commit.

Args:
	tree: Hash of the current git tree.
	log: The information on the commit as a Python array.
	parent_hash: The hash of the parent commit or None if there is no parent.
	collision: The hexadecimal characters to obtain in the hash.
	offset: The offset where the hidden characters (collision) should be found in the hash (default = 0).

Returns:
	The spaces added to the commit message for the collision encoded as binary.
"""
def partial_collision(tree, log, parent_hash, collision, offset = 0):
	commit_information = build_commit_information(tree, log, parent_hash)
	hash_input = build_git_hash_input(commit_information, log['message'])
	sha1 = str(hashlib.sha1(hash_input.encode('utf-8')).hexdigest())
	encoded_spaces = '';
	while sha1[offset: offset + len(collision)] != collision:
		encoded_spaces = space_encoding.increment(encoded_spaces)
		spaces = space_encoding.decode(encoded_spaces)
		hash_input = build_git_hash_input(commit_information, log['message'] + spaces)
		sha1 = hashlib.sha1(hash_input.encode('utf-8')).hexdigest()
	return encoded_spaces


"""Builds the information on a commit from its log.

This information will be used to generate the commit hash.

Args:
	tree: Hash of the current git tree.
	log: Log of the commit, Python array with the information on the committer, author, dates and commit message.
	parent_hash: Hash of the parent commit or None if no parent.

Returns:
	The commit information without the commit message.
	It's the string that will be used to generate the commit hash but
	without the commit message at the end and the size in bytes at the beginning.
"""
def build_commit_information(tree, log, parent_hash = None):
	hash_input = "tree %s\n" % tree
	if not parent_hash == None:
		hash_input += "parent %s\n" % parent_hash
	hash_input += "author %s <%s> %s -0500\n" % (log['author'], log['author-email'], str(log['author-date']))
	hash_input += "committer %s <%s> %s -0500\n\n" % (log['committer'], log['committer-email'], str(log['committer-date']))
	return hash_input


"""Builds the string that will be used to generate the git hash.

The commit information and the commit message are concatenated together and preceded by their size in bytes.

Args:
	commit_information: The commit information without the commit message at the end. See build_commit_information.
	commit_message: The commit message.
"""
def build_git_hash_input(commit_information, commit_message):
	end_hash_input = "%s%s\n" % (commit_information, commit_message)
	hash_input = "commit %s\0%s" % (len(end_hash_input.encode()), end_hash_input)
	return hash_input


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

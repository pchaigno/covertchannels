#!/usr/bin/env python3

from Crypto.Cipher import AES
import os
import sys
import git
import channel

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 16

# the character used for padding. 
PADDING = ' '
    
"""Encrypt a message using AES

Args:
	message: the message to encrypt
	key: the secret key to use in the symmetric cipher. Must be BLOCK_SIZE bytes long.
"""
def encrypt_message(message, key):
    # Pad the message. This is used to ensure that the message encrypted is always a multiple of BLOCK_SIZE
    message = message + (BLOCK_SIZE - len(message) % BLOCK_SIZE) * PADDING

    # Encrypt the message
    cipher = AES.new(key)
    encoded_messsage = cipher.encrypt(message);

    return encoded_messsage

"""Decrypt a message using AES

Args:
	message: the message to decrypt
	key: the secret key to use in the symmetric cipher. Must be BLOCK_SIZE bytes long.
"""
def decrypt_message(message, key):
    # Remove the padding
    message = message.rstrip()

    # Decrypt the message
    cipher = AES.new(key)
    decoded_messsage = cipher.decrypt(message);

    return decoded_messsage
 
 
"""Encrypt the message and communicate using git repository

Args:
	source-repository: URL to the repository to use as a source for commits and commit messages.
	channel-repository: URL to the repository to use to exchange the messages.
	message: The message to send.
        key: the key used for encryption
"""
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: channel.py <channel-repository> [<source-repository> <message>] <key>")
        sys.exit(2)

    channel_repository = sys.argv[1]
    source_repository = None
    message = None
    if len(sys.argv) == 5:
        source_repository = sys.argv[2]
        message = sys.argv[3]
        key = sys.argv[4]
        message =  encrypt_message(message, key)
        
        # Check that the channel repository is an SSH link:
        # Otherwise we won't be able to push without a password prompt.
    if not git.is_ssh(channel_repository):
        print("The channel repository needs to be an SSH link to a repository with the SSH key associated to your account.")
        sys.exit(3)

    if message == None or source_repository == None:
        key = sys.argv[2]
        message = channel.receive(channel_repository)
        message = decrypt_message(message, key)
        print("%s" % message.decode())
    else:
        channel.send(source_repository, channel_repository, message)



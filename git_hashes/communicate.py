#!/usr/bin/env python3

import os
import sys
import git
import channel
import argparse
import xor_cipher as cipher
 
"""Encrypt the message and communicate using git repository

Args:
	source-repository: URL to the repository to use as a source for commits and commit messages.
	channel-repository: URL to the repository to use to exchange the messages.
	message: The message to send.
        key: the key used for encryption
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Covert communication using git repositories")
    parser.add_argument("key", help="Key to encrypt the message", type=str)    
    parser.add_argument("channel", help="The repository used to transmit the message", type=str)
    parser.add_argument("source", help="The repository used to generate the commits", type=str, nargs='?')
    parser.add_argument("message", help="The message to transmit", type=str, nargs='?', default='')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    channel_repository = args.channel
    source_repository = args.source
    message = args.message
    key = args.key

    # Check that the channel repository is an SSH link:
    # Otherwise we won't be able to push without a password prompt.
    if not git.is_ssh(channel_repository):
        print("The channel repository needs to be an SSH link to a repository with the SSH key associated to your account.")
        sys.exit(3)
    
    # Decrypt
    if message == '':
        if args.verbose:
            print("Receiving message using " + channel_repository)
        message = channel.receive(channel_repository)
        if args.verbose:
            print("Encrypted message: " + message)
        mh = cipher.hash_received_to_hexl(message)
        k = cipher.genkey(len(mh), key)
        m = cipher.xor_hex(mh, k)
        decrypted_message = cipher.hex_to_string(m)
        print("%s" % decrypted_message)

    # Encrypt
    else:
        if args.verbose:
            print("Sending message using " + channel_repository)
        hexl = cipher.string_to_hex(message)
        k = cipher.genkey(len(hexl), key)
        mx = cipher.xor_hex(k, hexl)
        encrypted_message = cipher.generate_message_to_transmit(mx)
        if args.verbose:
            print("Encrypted message: " + encrypted_message)
        channel.send(source_repository, channel_repository, encrypted_message)

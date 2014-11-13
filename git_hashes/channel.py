#!/usr/bin/env python3
import sys
import os
import git_hashes
import git
import space_encoding

NB_CHARACTERS_PER_COMMIT = 2

"""Sends a message through the covert channel in git hashes.

Args:
	source_repository_url: URL of the repository to use as a source for commits and commit messages.
	channel_repository_url: URL of the support repository to exchange messages.
	message: The message to send.
"""
def send(source_repository_url, channel_repository_url, message):
	source_repository = git.get_name(source_repository_url)
	logs = []
	if not os.path.exists(source_repository):
		logs = init_source(source_repository_url)
	else:
		logs = git.read_logs(source_repository)

	channel_repository = git.get_name(channel_repository_url)
	if not os.path.exists(channel_repository):
		init_channel(channel_repository_url)

	# Change current working directory:
	os.chdir(channel_repository)
	source_repository = "../%s" % source_repository

	nb_commits = git.get_nb_commits(channel_repository)
	fragments = fragment_message(message)
	for i in range(nb_commits, nb_commits + len(fragments)):
		log = logs[i]
		fragment = fragments[i - nb_commits]

		git.apply_patch(channel_repository, source_repository, i)

		# Computes the new commit message to get the right hash:
		tree = git.get_git_tree(channel_repository)
		parent_hash = None
		if i != 0:
			parent_hash = git.get_last_commit_hash(channel_repository)
		encoded_spaces = git_hashes.partial_collision(tree, log, parent_hash, fragment)
		message = log['message'] + space_encoding.decode(encoded_spaces)

		git.commit(channel_repository, log, message)

		# Checks commit hash:
		git_hash = git.get_last_commit_hash(channel_repository)
		if not fragment == git_hash[0:2]:
			print("Fragment %s not found in commit %s ('%s')" % (fragment, git_hash, log['message']))
			sys.exit(4)

	git.push(channel_repository)

	os.chdir('..')


"""Splits the message in pieces of size NB_CHARACTERS_PER_COMMIT.

Args:
	message: The original message.

Returns:
	An array of messages of size NB_CHARACTERS_PER_COMMIT.
"""
def fragment_message(message):
	fragments = []
	for i in range(0, len(message), NB_CHARACTERS_PER_COMMIT):
		fragments.append(message[i: i + NB_CHARACTERS_PER_COMMIT])
	return fragments


"""Receives a message through the covert channel in git hashes.

Args:
	repository_url: URL of the support repository to exchange messages.

Returns:
	The message received.
"""
def receive(repository_url):
	repository = git.get_name(repository_url)
	new_logs = []
	if not os.path.exists(repository):
		new_logs = init_channel(repository_url)
	else:
		new_logs = git.update_repository(repository)

	message = ''
	for log in new_logs:
		if len(log['hash']) > NB_CHARACTERS_PER_COMMIT:
			message += log['hash'][0:NB_CHARACTERS_PER_COMMIT]
	return message


"""Inits the source repository on the local computer.

Clones the repository and extract the pach files and the commit messages.

Args:
	source_repository: The source repository as an URL.

Returns:
	The git logs of the source repository.
"""
def init_source(source_repository):
	repository_name = git.clone_repository(source_repository)
	logs = git.dump_logs(repository_name)
	git.dump_commits(repository_name, logs)
	return logs


"""Inits the repository to exchange the covert messages.

Clones the repository and extract the commit information.

Args:
	channel_repository: URL to the repository to exchange messages.

Returns:
	The git logs of the channel repository.
"""
def init_channel(channel_repository):
	repository_name = git.clone_repository(channel_repository)
	logs = git.dump_logs(repository_name)
	return logs


"""Exchanges messages through a git repository using the hashes.

Args:
	source-repository: URL to the repository to use as a source for commits and commit messages.
	channel-repository: URL to the repository to use to exchange the messages.
	message: The message to send.
"""
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: channel.py <channel-repository> [<source-repository> <message>]")
		sys.exit(2)

	channel_repository = sys.argv[1]
	source_repository = None
	message = None
	if len(sys.argv) == 4:
		source_repository = sys.argv[2]
		message = sys.argv[3]

	# Check that the channel repository is an SSH link:
	# Otherwise we won't be able to push without a password prompt.
	if not git.is_ssh(channel_repository):
		print("The channel repository needs to be an SSH link to a repository with the SSH key associated to your account.")
		sys.exit(3)

	if message == None or source_repository == None:
		message = receive(channel_repository)
		print("message: %s" % message)
	else:
		send(source_repository, channel_repository, message)

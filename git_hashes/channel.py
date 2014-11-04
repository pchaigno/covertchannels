#!/usr/bin/env python3
import sys
import git_hashes
import git
import space_encoding

NB_CHARACTERS_PER_COMMIT = 3

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
		logs = init_source(source_repository)
	else:
		logs = read_logs(repository)

	channel_repository = git.get_name(channel_repository_url)
	if not os.path.exists(channel_repository):
		init_channel(channel_repository)

	# Change current working directory:
	os.chdir(channel_repository)
	source_repository = "../%s" % source_repository

	fragments = fragment_message(message)
	for i in range(0, len(fragments)):
		log = logs[i]
		git.apply_patch(channel_repository, source_repository, i)

		# Computes the new commit message to get the right hash:
		tree = git.get_git_tree(channel_repository)
		hash_input = ''
		if i == 0:
			hash_input = git_hashes.build_hash_input(tree, log)
		else:
			hash_input = git_hashes.build_hash_input(tree, log, logs[i-1])
		encoded_spaces = git_hashes.partial_collision(hash_input, log['message'], fragments[i])
		message = log['message'] + space_encoding.decode(encoded_spaces)

		git.commit(repository, log, message)
	
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
	if not os.path.exists(repository):
		init_channel(repository)

	new_logs = git.update_repository(repository)
	message = ''
	for log in new_logs:
		if len(log['message']) > NB_CHARACTERS_PER_COMMIT:
			message += log['message'][0:NB_CHARACTERS_PER_COMMIT]
	return message


"""Inits the source repository on the local computer.

Clones the repository and extract the pach files and the commit messages.

Args:
	source_repository: The source repository.

Returns:
	The git logs of the source repository
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
	The name of the repository.
"""
def init_channel(channel_repository):
	repository_name = git.clone_repository(channel_repository)
	git.dump_logs(repository_name)
	return repository_name


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
	message = None
	if len(sys.argv) == 4
		source_repository = sys.argv[2]
		message = sys.argv[3]

	if message == None:
		message = receive(channel_repository)
		print("%s" % message)
	else:
		send(source_repository, channel_repository, message)

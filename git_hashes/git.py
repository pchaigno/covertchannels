#!/usr/bin/env python3
import sys
import os
import re
import json
import subprocess
import time

"""Error raised when a git repository is not found

Attributes:
	repository: Name of the git repository.
"""
class RepositoryNotFoundError(Exception):
	def __init__(self, repository):
		self.repository = repository

	def __str__(self):
		return "The repository %s could not be found." % self.repository


"""Dumps the logs from a git repository as a JSON document.

The call to this function must be made from the parent directory of the directory of the repository.
The logs are saved as a JSON document in the directory of the repository.
This function temporarily changes the current working directory.

Args:
	repository: The name of the folder where the repository is.

Returns:
	The logs as a Python array.
"""
def dump_logs(repository):
	change_pwd = goto_repository(repository)

	# Dumps the git logs in a JSON document.
	os.system("""git log --reverse --pretty=format:'{%n  "hash": "%H",%n  "author": "%an",%n  "author-email": "%ae",%n  "author-date": %at,%n  "committer": "%cn",%n  "committer-email": "%ce",%n  "committer-date": %ct,%n  "message": "%s"%n},' $@ | perl -pe 'BEGIN{print "["}; END{print "]\n"}' | perl -pe 's/},]/}]/' > logs.json""")

	# Rewrites the escaped JSON document in a new file.
	# Then, the original JSON document in overwritten with the new one:
	json_data = open('logs.json')
	json_escaped = open('logs-escaped.json', 'w')
	for line in json_data:
		matches = re.match(r'^  "message": "(.+)"$', line)
		if matches:
			# Escapes the backslashes first, the double quotes after
			# because we need to add a backslash to escape the double quotes:
			message = matches.group(1).replace('\\', '\\\\')
			message = message.replace('"', '\\"')
			line = '  "message": "%s"\n' % (message)
		json_escaped.write(line)
	json_data.close()
	json_escaped.close()
	os.system("mv logs-escaped.json logs.json")

	if change_pwd:
		os.chdir('..')

	logs = read_logs(repository)
	return logs


"""Read the logs from the JSON document.

The logs need to be dumped first (ie. before the call to this function).

Args:
	repository: The name of the folder where the repository is.

Returns:
	The git logs of the repository as a Python array.
"""
def read_logs(repository):
	change_pwd = goto_repository(repository)

	json_data = open("logs.json")
	logs = json.load(json_data)
	json_data.close()
	
	if change_pwd:
		os.chdir('..')

	return logs


"""Dumps the commits from a git repository as patch files.

The patch files are created into the repository directory.
This function temporarily changes the current working directory.

Args:
	repository: The name of the folder where the repository is.
	logs: The git logs as a Python array.
"""
def dump_commits(repository, logs):
	change_pwd = goto_repository(repository)

	# Uses the binary option to be able to dump and then apply the images and other binary files:
	os.system("git show --binary %s > 0.patch" % (logs[0]['hash']))
	for i in range(1, len(logs)):
		result = os.system("git diff --binary %s %s > %d.patch" % (logs[i-1]['hash'], logs[i]['hash'], i))

	if change_pwd:
		os.chdir('..')


"""Rebuild a git repository from patches and with some modifications.

Uses the patch files and the git logs to rebuild a repository.
A commit is made between each patch applied.
The contributors can be replaced with the credentials specified.
All the committer and author dates will be shift by the offset value.

This function temporarily changes the current working directory.
It only reproduces the commit history and doesn't push it.
The user will need to add a remote repository (git remote add) before pushing.

Args:
	dump_folder: The directory containing the pach files and the JSON document.
	logs: The git logs as a Python array.
	repository: The directory name for the new repository.
	your_username: Your username. Will replace the contributors specified.
	your_email: Your email address. Will replace the email addresses of the contributors specified.
	contributors: The contributors to replace or all to replace all of them.
	offset: The offset (in seconds) of which the commit's dates must be shifted.
"""
def rebuild_repository(dump_folder, logs, repository, your_username, your_email, contributors = [], offset = 0):
	os.system("mkdir %s" % (repository))
	os.chdir(repository)

	os.system("git init")
	for i in range(0, len(logs)):
		log = logs[i]
		
		# Changes the committer and author (and their email addresses) and the dates if needed:
		committer = log['committer']
		committer_email = log['committer-email']
		if contributors == 'all' or committer_email in contributors:
			committer = your_username
			committer_email = your_email
		author = log['author']
		author_email = log['author-email']
		if contributors == 'all' or author_email in contributors:
			author = your_username
			author_email = your_email
		committer_date = log['committer-date'] + offset
		author_date = log['author-date'] + offset

		# Checks that the current dates hasn't been reached (we don't want to make commits in the future):
		current_time = (int)(time.time())
		if committer_date > current_time or author_date > current_time:
			print("Reached current date.")
			break

		apply_patch(repository, dump_folder, i)

		# The values for the committer can only be changed through the environnement variables:
		os.environ["GIT_COMMITTER_NAME"] = committer
		os.environ["GIT_COMMITTER_EMAIL"] = committer_email
		os.environ["GIT_COMMITTER_DATE"] = str(committer_date)

		# Need to escape the double quotes for the commit message.
		message = log['message'].replace('"', '\\"')

		# Quiet mode for the commits, only the errors are shown.
		# allow-empty option for commits containing nothing (merge commits for example).
		# cleanup=verbatim to keep the spaces at the end of the commit message.
		os.system("""git commit --allow-empty --cleanup=verbatim -q -m "%s" --author="%s <%s>" --date=%d""" % (message, author, author_email, author_date))

	os.chdir('..')


"""Applies a patch to a git repository.

Adds the changes to the git tree (`git add --all .`).
Doesn't display the command output.

Args:
	repository: The name of the folder where is the repository to patch.
	dump_folder: Path to the folder where the patch file is.
	patch_number: The number of the patch (patch files have the format i.patch).
"""
def apply_patch(repository, dump_folder, patch_number):
	change_pwd = goto_repository(repository)

	os.system("git apply --whitespace=nowarn ../%s/%d.patch 2> /dev/null " % (dump_folder, patch_number))
	os.system("git add --all .")

	if change_pwd:
		os.chdir('..')


"""Commits in a git repository.

The information is retrieved from the git log.
Only the commit message can be changed.

Args:
	repository: The name of the git repository.
	log: The commit log.
	message: The new commit message or None if none was provided.
"""
def commit(repository, log, message = None):
	change_pwd = goto_repository(repository)

	# The values for the committer can only be changed through the environnement variables:
	os.environ["GIT_COMMITTER_NAME"] = log['committer']
	os.environ["GIT_COMMITTER_EMAIL"] = log['committer-email']
	os.environ["GIT_COMMITTER_DATE"] = str(log['committer-date'])

	# Check if a new commit message was provided:
	if message == None:
		message = log['message']

	# Quiet mode for the commits, only the errors are shown.
	# allow-empty option for commits containing nothing (merge commits for example).
	# cleanup=verbatim to keep the spaces at the end of the commit message.
	os.system("""git commit --allow-empty --cleanup=verbatim -q -m "%s" --author="%s <%s>" --date=%d""" % (message, log['author'], log['author-email'], log['author-date']))

	if change_pwd:
		os.chdir('..')


"""Gets the email addresses of the contributors of a repository.

The following git command is used: git log --format='%ae' | sort -u.
This function temporarily changes the current working directory.

Args:
	repository: The name of the folder where the repository is.

Returns:
	The list of contributors' email addresses.
"""
def get_contributors(repository):
	change_pwd = goto_repository(repository)

	process1 = subprocess.Popen(('git', 'log', '--format=%ae'), stdout=subprocess.PIPE)
	process2 = subprocess.Popen(('sort', '-u'), stdin=process1.stdout, stdout=subprocess.PIPE)
	contributors = process2.stdout.read().decode('utf-8').split("\n")

	if change_pwd:
		os.chdir('..')

	return contributors


"""Clones a repository.

Args:
	url: The URL to the git repository (need to be HTTP or HTTPS).

Returns:
	The folder where the repository was downloaded.
"""
def clone_repository(url):
	os.system("git clone %s" % url)
	print()
	return get_name(url)


"""Pushes the new commits to the remote repository.

The link to the remote repository needs to be an SSH link.
ie. you need to clone from an SSH link or add an SSH remote.
Your local SSH key need to be associated to the remote git server.
Otherwise the password will be asked and the command will fail.

Args:
	repository: The name of the folder where the repository is.
"""
def push(repository):
	change_pwd = goto_repository(repository)
	os.system("git push origin master")
	if change_pwd:
		os.chdir('..')


"""Gets the name of the repository.

Args:
	url: URL to the repository.

	Returns: The name of the repository.
"""
def get_name(url):
	matches = re.match(r'(https?:\/\/|git@).+\/([^\/]+?)(\.git)?$', url)
	if not matches:
		raise Exception("You need to provide a HTTP(S) or SSH link.")
	repository = matches.group(2)
	return repository


"""Checks if the URL to the repository is an SSH link.

An SSH link has the format git@host:username/repo(.git)?.

Args:
	url: URL to the repository.

Returns:
	True if the url to the git repository is an SSH link.
"""
def is_ssh(url):
	matches = re.match(r'git@.+:\w+\/([^\/]+)(\.git)?$', url)
	if matches:
		return True
	return False


"""Gets the number of commits in a repository.

Use the command `git rev-list HEAD --count`.

Args:
	repository: The repository (name of the folder where it is).

Returns:
	The number of commits in the current branch of the repository.
"""
def get_nb_commits(repository):
	change_pwd = goto_repository(repository)

	process1 = subprocess.Popen(('git', 'log', '--pretty=oneline'), stdout=subprocess.PIPE)
	process2 = subprocess.Popen(('wc', '-l'), stdin=process1.stdout, stdout=subprocess.PIPE)
	nb_commits = int(process2.stdout.read().decode('utf-8'))

	if change_pwd:
		os.chdir('..')

	return nb_commits


"""Gets the hash of the current git tree.

Uses the command `git write-tree`.
Only files and folders added to git with `git add` will be considered.

Args:
	repository: The repository (name of the folder where it is).

Returns:
	The hash of the current git tree.
"""
def get_git_tree(repository):
	change_pwd = goto_repository(repository)

	process = subprocess.Popen(('git', 'write-tree'), stdout=subprocess.PIPE)
	tree_hash = process.stdout.read().decode('utf-8').strip()

	if change_pwd:
		os.chdir('..')

	return tree_hash


"""Gets the hash of the last commit.

Uses the command `git log --pretty=format:'%s' -n 1`.

Args:
	repository: The repository (name of the folder where it is).

Returns:
	The hash of the last commit made.
"""
def get_last_commit_hash(repository):
	change_pwd = goto_repository(repository)

	process = subprocess.Popen(('git', 'log', '--pretty=format:%H', '-1'), stdout=subprocess.PIPE)
	commit_hash = process.stdout.read().decode('utf-8').strip()

	if change_pwd:
		os.chdir('..')

	return commit_hash


"""Updates a repository with git pull and updates the logs.json file.

Args:
	repository: Name of the repository, should be in a folder with that name.

Returns:
	The information on the new commits as a Python array.
"""
def update_repository(repository):
	# Updates the repository:
	nb_commits = get_nb_commits(repository)
	change_pwd = goto_repository(repository)
	os.system("git pull origin master")
	if change_pwd:
		os.chdir('..')

	# Retrieves the information on the new commits:
	new_nb_commits = get_nb_commits(repository)
	logs = dump_logs(repository)
	nb_new_commits = new_nb_commits - nb_commits
	return logs[len(logs) - nb_new_commits: len(logs)]


"""Change the current working directory.

If we are already in the git repository, don't change anything.

Args:
	The new current working directory, a git repository.

Returns:
	True if the working directory was changed.
	If true is returned it means we should leave it (ie. return to the parent directory)
	at the end of the operations.
"""
def goto_repository(repository):
	if os.path.exists(repository):
		os.chdir(repository)
		return True
	elif os.system("git rev-parse") != 0:
		raise RepositoryNotFoundError(repository)
	return False


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: git.py <repository> <new-name>")
		sys.exit(2)

	repository = sys.argv[1]
	new_repository = sys.argv[2]

	contributors = get_contributors(repository)
	print(contributors)

	logs = dump_logs(repository)
	dump_commits(repository, logs)
	rebuild_repository(repository, logs, new_repository, '', '', [], 0)
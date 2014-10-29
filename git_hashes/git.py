#!/usr/bin/env python3
import sys
import json
import os
import re

def dump_repository(repository):
	os.chdir(repository)

	os.system("""git log --reverse --pretty=format:'{%n  "hash": "%H",%n  "author": "%an",%n  "author-email": "%ae",%n  "author-date": %at,%n  "committer": "%cn",%n  "committer-email": "%ce",%n  "committer-date": %ct,%n  "message": "%s"%n},' $@ | perl -pe 'BEGIN{print "["}; END{print "]\n"}' | perl -pe 's/},]/}]/' > logs.json""")

	json_data = open('logs.json')
	json_escaped = open('logs-escaped.json', 'w')
	for line in json_data:
		matches = re.match(r'^  "message": "(.+)"$', line)
		if matches:
			message = matches.group(1).replace('"', '\\"')
			line = '  "message": "%s"\n' % (message)
		json_escaped.write(line)
	json_data.close()
	json_escaped.close()
	os.system("mv logs-escaped.json logs.json")

	json_data = open('logs.json')
	logs = json.load(json_data)
	json_data.close()

	os.system("git show --binary %s > 0.patch" % (logs[0]['hash']))
	for i in range(1, len(logs)):
		os.system("git diff --binary %s %s > %d.patch" % (logs[i-1]['hash'], logs[i]['hash'], i))

	os.chdir('..')

def rebuild_repository(dump_folder, repository):
	os.system("mkdir %s" % (repository))
	os.chdir(repository)

	json_data = open("../%s/logs.json" % (dump_folder))
	logs = json.load(json_data)
	json_data.close()

	os.system("git init")
	for i in range(0, len(logs)):
		log = logs[i]
		os.system("git apply ../%s/%d.patch" % (dump_folder, i))
		os.system("git add --all .")
		os.environ["GIT_COMMITTER_NAME"] = log['committer']
		os.environ["GIT_COMMITTER_EMAIL"] = log['committer-email']
		os.environ["GIT_COMMITTER_DATE"] = str(log['committer-date'])
		os.system("""git commit -m "%s" --author="%s <%s>" --date=%d""" % (log['message'], log['author'], log['author-email'], log['author-date']))

	os.chdir('..')

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: git.py <old-repository> <new-repository>")
		print("Usage: git.py dump <repository>")
		print("Usage: git.py rebuild <dump-folder> <repository>")
		sys.exit(2)

	action = sys.argv[1]
	if action == 'dump':
		repository = sys.argv[2]
		dump_repository(repository)

	elif action == 'rebuild':
		if len(sys.argv) < 4:
			print("Usage: git.py rebuild <dump-folder> <repository>")
			sys.exit(2)

		dump_folder = sys.argv[2]
		repository = sys.argv[3]
		rebuild_repository(dump_folder, repository)

	else:
		old_repository = sys.argv[1]
		new_repository = sys.argv[2]
		dump_repository(old_repository)
		rebuild_repository(old_repository, new_repository)

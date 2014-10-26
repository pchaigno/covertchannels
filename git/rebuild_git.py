#!/usr/bin/env python3
import sys
import json
import os

if len(sys.argv) < 3:
	print("usage: rebuil_git.py <dump-folder> <repository>")
	sys.exit(2)

dump_folder = sys.argv[1]
repository = sys.argv[2]

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
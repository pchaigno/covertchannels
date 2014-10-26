#!/usr/bin/env python3
import sys
import json
import os

def dump_repository(repository):
	os.chdir(repository)

	os.system("""git log --reverse --pretty=format:'{%n  "hash": "%H",%n  "author": "%an",%n  "author-email": "%ae",%n  "author-date": %at,%n  "committer": "%cn",%n  "committer-email": "%ce",%n  "committer-date": %ct,%n  "message": "%s"%n},' $@ | perl -pe 'BEGIN{print "["}; END{print "]\n"}' | perl -pe 's/},]/}]/' > logs.json""")

	json_data = open('logs.json')
	logs = json.load(json_data)
	json_data.close()

	os.system("git show --binary %s > 0.patch" % (logs[0]['hash']))
	for i in range(1, len(logs)):
		os.system("git diff --binary %s %s > %d.patch" % (logs[i-1]['hash'], logs[i]['hash'], i))

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage: rebuil_git.py <repository>")
		sys.exit(2)

	repository = sys.argv[1]
	dump_repository(repository)
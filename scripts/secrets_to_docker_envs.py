#!/usr/bin/env python
import json, os, sys

CWD = os.getcwd()

if len(sys.argv) > 1:
    envfile = sys.argv[1]
else:
    envfile = 'secrets.json'

dockerenv = []
with open(os.path.join(CWD, envfile), "r") as env:
    j = json.load(env)
    for (k, v) in j.items():
        # https://stackoverflow.com/a/33699705
        if isinstance(k, ("".__class__, u"".__class__)):
            dockerenv.append("-e {}={}".format(k, str(v)))
    print(' '.join(dockerenv))

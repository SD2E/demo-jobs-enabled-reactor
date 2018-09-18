#!/usr/bin/env python
import sys
from agavepy.agave import Agave, AgaveException
try:
    Agave.restore()
except Exception as a:
    raise AgaveException("Unable to authenticate: {}".format(a))
    sys.exit(1)

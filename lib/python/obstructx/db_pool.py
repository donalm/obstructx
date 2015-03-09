#!/usr/bin/env python

import platform
pypy = "PyPy" == platform.python_implementation()

try:
    if pypy:
        from psycopg2cffi import compat
        compat.register()
except Exception, e:
    print "ERROR: Failed to register psycopg2cffi: %s" % (e,)
    raise
    



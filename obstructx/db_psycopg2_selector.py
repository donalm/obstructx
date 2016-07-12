#!/usr/bin/env python

"""
Find out if we're running in a pypy session, in which case we need to
use the cffi version of psycopg2
"""
import platform

try:
    pypy = "PyPy" == platform.python_implementation()
    if pypy:
        from psycopg2cffi import compat
        compat.register()
except Exception, e:
    import logging
    import traceback
    logger = logging.getLogger()
    logger.error("Failed to import psycopg2cffi: %s", traceback.format_exc())

import psycopg2

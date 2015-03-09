#!/usr/bin/env python

"""
Find out if we're running in a pypy session, in which case we need to
use the cffi version of psycopg2
"""
import platform
import json
pypy = "PyPy" == platform.python_implementation()

try:
    if pypy:
        from psycopg2cffi import compat
        compat.register()
        print("Psycopg2 CFFI registered")
except Exception, e:
    print("ERROR: Failed to register psycopg2cffi: %s" % (e,))
    raise

import psycopg2
import psycopg2.extras
from txpostgres import txpostgres
from twisted.python.modules import getModule
from twisted.python import util
from twisted.internet import reactor, task, defer


def get_database_credentials():
    filepath = getModule(__name__).filePath
    basedir = filepath.parent().parent().parent().parent()
    return json.loads(basedir.child("etc").child("database_credentials.json").getContent())


class Pool(txpostgres.ConnectionPool):

    def __init__(self, appname):
        credentials = get_database_credentials()
        app_credentials = credentials[appname]
        args = tuple()
        txpostgres.ConnectionPool.__init__(self,
                                           None,
                                           *args,
                                           connection_factory=psycopg2.extras.NamedTupleConnection,
                                           **app_credentials)


def go(result, pool):
    query = """
        SELECT
            *
        FROM
            alternate_stock"""
    df = pool.runQuery(query)
    df.addCallback(dumpres)
    return df


def dumpres(result):
    print("RESULT: %s" % (result,))
    print(result[0].isbn)
    return result



def main(reactor):
    print("MAIN %s" % (reactor,))


    pool = Pool("booktown")
    df = pool.start()
    df.addCallback(go, pool)

    return df




if __name__ == "__main__":
    task.react(main)


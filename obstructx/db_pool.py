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
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
from txpostgres import txpostgres
from txpostgres.reconnection import DeadConnectionDetector
from twisted.python.modules import getModule
from twisted.python import util
from twisted.internet import reactor, task, defer


def get_database_credentials(database_name):
    filepath = getModule(__name__).filePath
    basedir = filepath.parent().parent().parent().parent()
    return json.loads(basedir.child("etc").child("database_credentials_%s.json" % (database_name,)).getContent())


def Pool(database_name):
    return PoolFactory.get(database_name)


class PoolFactory(object):
    pools = {}
    @classmethod
    def get(cls, database_name):
        if not database_name in cls.pools:
            cls.pools[database_name] = _Pool(database_name)
        return cls.pools[database_name]

class _Pool(txpostgres.ConnectionPool):

    def __init__(self, database_name):
        self.status_df = None
        credentials = get_database_credentials(database_name)
        app_credentials = credentials
        args = tuple()

        def connection_factory(self, *args, **kwargs):
            kwargs['detector'] = DeadConnectionDetector()
            return txpostgres.Connection(*args, **kwargs)

        txpostgres.ConnectionPool.connectionFactory = connection_factory
        txpostgres.ConnectionPool.__init__(self,
                                           None,
                                           *args,
                                           connection_factory=psycopg2.extras.NamedTupleConnection,
                                           **app_credentials)

    def start(self):
        if not self.status_df:
            self.status_df = txpostgres.ConnectionPool.start(self)

        """
        Everyone who calls 'start' gets their own deferred
        Probably not important, but it makes the code more
        predictable
        """
        df = defer.Deferred()

        def cb(result):
            df.callback(result)
            return result

        self.status_df.addCallback(cb)
        return df


class BookTown(object):

    def __init__(self):
        pass

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

#!/usr/bin/env python

from twisted.internet import reactor
from twisted.internet import defer

from obstructx import db_introspect
from obstructx import db_pool
from obstructx import log

logger = log.get_logger()

class DbMethods(object):
    def extract_first(self, results):
        return [result[0] for result in results]

class Inquisitor(DbMethods):

    def initialize_pool(self):
        logger.error("initialize_pool")
        self.pool = db_pool.Pool("booktown")
        df = self.pool.start()
        return df

    def get_tables(self, *args):
        logger.error("get_tables")
        query = db_introspect.queries["list_tables"]
        df.addCallback(self.extract_first)
        return self.pool.runQuery(query)

    def parse_tables(self, tables):
        dfs = []
        for table in tables:
            dfs.append(self.get_columns, table)
        return defer.DeferredList(dfs)

    def get_databases(self, *args):
        logger.error("get_databses")
        query = db_introspect.queries["list_databses"]
        df = self.pool.runQuery(query)
        df.addCallback(self.extract_first)
        return df

    def get_columns(self, table, *args):
        logger.error("get_columns")
        query = db_introspect.queries["list_table_columns"]
        return self.pool.runQuery(query, (table,))

    def get_foreign_keys(self, *args):
        logger.error("get_foreign_keys")
        query = db_introspect.queries["list_foreign_keys"]
        df = self.pool.runQuery(query)
        return df

    def show_result(self, result):
        if isinstance(result, basestring):
            print("RESULT: %s" % (result,))
            return
        for item in result:
            print("-- %s" % (item,))

def main():
    i = Inquisitor()
    df = i.initialize_pool()
    df.addCallback(i.get_tables)
    df.addCallback(i.parse_tables)
    df.addCallback(i.show_result)
    #df.addCallback(i.get_tables)
    #df.addCallback(i.show_result)


if __name__ == '__main__':
    main()

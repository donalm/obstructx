#!/usr/bin/env python

from twisted.internet import reactor


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

    def get_databases(self, *args):
        logger.error("get_databses")
        query = db_introspect.queries["list_databses"]
        df = self.pool.runQuery(query)
        df.addCallback(self.extract_first)
        return df

    def get_columns(self, *args):                                                                                                                                                                
        logger.error("get_columns")                                                                                                                                                              
        query = db_introspect.queries["list_table_columns"]                                                                                                                                  
        return self.pool.runQuery(query, (self.table,)) 

    def get_foreign_keys(self, *args):
        logger.error("get_foreign_keys")
        query = db_introspect.queries["list_foreign_keys"]
        df = self.pool.runQuery(query)
        return df
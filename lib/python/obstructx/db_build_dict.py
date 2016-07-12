#!/usr/bin/env python

import json

from collections import OrderedDict

from twisted.internet import reactor
from twisted.internet import defer

from obstructx import db_introspect
from obstructx import db_pool
from obstructx import log

logger = log.get_logger()
logger.error("TEST")

class DbMethods(object):
    def extract_first(self, results):
        return [result[0] for result in results]

    def query_first(self, query, queryargs=None):
        if queryargs is None:
            queryargs = ()
        df = self.pool.runQuery(query, queryargs)
        df.addCallback(lambda x: x[0])
        return df

class Inquisitor(DbMethods):
    data = {}

    def __init__(self, database_name):
        self.database_name = database_name

    def initialize_pool(self):
        logger.error("initialize_pool")

        Inquisitor.data[self.database_name] = {}
        self.pool = db_pool.Pool(self.database_name)
        df = self.pool.start()
        return df

    def get_database_metadata(self):
        df = self.initialize_pool()
        df.addCallback(self.get_tables)
        return df

    def get_tables(self, *args):
        logger.error("get_tables")
        query = db_introspect.queries["list_tables"]
        df = self.pool.runQuery(query)
        df.addCallback(self.parse_tables)
        return df

    def parse_tables(self, tables):
        dfs = []
        for table in tables:
            database = table.table_catalog
            table = table.table_name
            Inquisitor.data[database][table] = {"fields":OrderedDict(), "indices":OrderedDict()}
            df = self.get_columns(table)
            df.addCallback(self.show_columns)
            df.addCallback(self.get_foreign_keys)
            df.addCallback(self.get_indices)
            df.addCallback(self.parse_indices)
            dfs.append(df)

        dfl = defer.DeferredList(dfs)
        #dfl.addCallback(self.get_foreign_keys)
        #dfl.addCallback(self.parse_foreign_keys)
        return dfl


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

    def get_indices(self, table, *args):
        logger.error("get_indices: %s" % (table,))
        query = db_introspect.queries["list_table_indices"]
        df = self.pool.runQuery(query, (table,))
        return df

    def parse_indices(self, results):
        #print("parse_indices: %s" % results,)
        for result in results:
            leader = result.column_names[0]
            Inquisitor.data[self.database_name][result.table_name]["fields"][leader]["leads_index"] = True
            Inquisitor.data[self.database_name][result.table_name]["indices"][result.index_name] = {"fields": result.column_names, "unique":result.unique}
            if len(result.column_names) == 1 and result.unique:
                Inquisitor.data[self.database_name][result.table_name]["fields"][leader]["unique"] = True

    def get_foreign_keys(self, table, *args):
        logger.error("get_foreign_keys")
        query = db_introspect.queries["list_foreign_keys"]
        df = self.pool.runQuery(query, (table,))
        df.addCallback(self.parse_foreign_keys, table)
        return df

    def parse_foreign_keys(self, results, table_name):
        for result in results:
            Inquisitor.data[result.database_name][result.table_name]["fields"][result.column_name]["references_foreign_key"] = (result.foreign_table_name, result.foreign_column_name,)
            try:
                Inquisitor.data[result.database_name][result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"].append((result.table_name, result.column_name,))
            except Exception, e:
                Inquisitor.data[result.database_name][result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"] = [(result.table_name, result.column_name,)]
        return table_name

    def show_result(self, result):
        if isinstance(result, basestring):
            print("RESULT: %s" % (result,))
            return
        for item in result:
            print("-- %s" % (item,))

    def show_columns(self, results):
        database_name = results[0].table_catalog
        table = results[0].table_name
        nullable = {"YES":True, "NO":False}
        for column in results:
            val = {}
            val['name'] = column.column_name
            val['type'] = column.data_type
            val['nullable'] = nullable[column.is_nullable]
            val['default'] = column.column_default
            val['references_foreign_key'] = None
            val['referenced_by_foreign_key'] = None
            val['leads_index'] = False
            Inquisitor.data[database_name][table]["fields"][column.column_name] = val

        return table


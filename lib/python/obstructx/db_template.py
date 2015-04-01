#!/usr/bin/env python

import re
import json
import time
from twisted.python import log
from collections import OrderedDict

appname = "obstructx"
from obstructx import config
config.Config.init(appname)

from obstructx.log import get_logger
logger = get_logger(appname)
logger.error("WOAH")

from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import defer

from obstructx import db_introspect
from obstructx import db_pool
from obstructx import log

logger = log.get_logger()

class BadQueryException(Exception):
    pass

class Table(object):
    timing = False
    database = None
    name = None
    fields = None
    absolute_fields = None
    whitelist_regex = re.compile("[^\-\w]+")
    comparison_operators_string = "< > <= >= = <> != in"
    comparison_operators = set(comparison_operators_string.split())
    db_connection_pool = None

    @classmethod
    def initialize_db_connection_pool(cls):
        if cls.db_connection_pool is not None:
            df = defer.Deferred()
            df.callback()
            return df
        cls.db_connection_pool = db_pool.Pool(cls.database)
        df = cls.db_connection_pool.start()
        return df

    @classmethod
    def run_query(cls, query, values):
        """
        If the pool hasn't been initialized this will raise an
        exception
        """
        if cls.timing:
            start_time = time.time()
            df = cls.db_connection_pool.runQuery(query, values)
            df.addCallback(cls.timing_query_returned, start_time)
            return df

        return cls.db_connection_pool.runQuery(query, values)

    @classmethod
    def timing_query_returned(cls, result, start_time):
        logger.error("TIMING: %s", time.time() - start_time)
        return result

    @classmethod
    def whitelist_keyword(cls, keyword):
        """
        Remove any character from a keyword (commonly a database table's field
        name) that is not explicitly permitted by our whitelist. Importantly
        the dot character must be removed.
        """
        return cls.whitelist_regex.sub("", keyword)

    @classmethod
    def whitelist_comparison_operator(cls, comparison_operator):
        if comparison_operator in cls.comparison_operators:
            return True
        return False

    @classmethod
    def is_sequence(cls, value):
        return (not hasattr(value, "strip") and
                    hasattr(value, "__getitem__") or
                    hasattr(value, "__iter__"))

    @classmethod
    def whitelist_clause(cls, fieldname, clause):

        if cls.is_sequence(clause):
            if clause[0] in cls.comparison_operators:
                comparison_operator = clause[0]
                value = clause[1:]
            else:
                raise BadQueryException("First element of clause '%s' is not a permitted comparison operator (%s)" % (clause, cls.comparison_operators_string,))
        else:
            comparison_operator = '='
            value = clause

        if fieldname in cls.absolute_fields:
            return fieldname, comparison_operator, value

        if fieldname in cls.fields:
            fieldname = "%s.%s" % (cls.name, fieldname,)
            return fieldname, comparison_operator, value

    @classmethod
    def get_query(cls, *args, **kwargs):

        constraints = []
        values = []

        for key, value in kwargs.items():
            fieldname, comparison_operator, value = cls.whitelist_clause(key, value)
            constraints.append("%s  %s  %%s" % (fieldname, comparison_operator,))
            values.append(value)

        fields = ",\n{indent}".join(cls.absolute_fields)
        where  = " AND \n{indent}".join(constraints)

        query = "SELECT\n{indent}" + fields + "\nFROM\n{indent}" + cls.name
        if where:
            query = query + "\nWHERE\n{indent}" + where
        return query.format(indent='    '), values

    @classmethod
    def get_kwargs(cls, **kwargs):
        return [cls.whitelist_clause(key, value) for (key, value,) in kwargs.items()]

    @classmethod
    def get_records(cls, *args, **kwargs):
        query, values = cls.get_query(*args, **kwargs)
        return cls.run_query(query, values)


class AlternateStock(Table):
    database = "booktown"
    name = "alternate_stock"
    fields = ('isbn', 'cost', 'retail', 'stock')
    absolute_fields = ('alternate_stock.isbn',
                       'alternate_stock.cost',
                       'alternate_stock.retail',
                       'alternate_stock.stock')


def main(reactor):
    #ass = AlternateStock()
    AlternateStock.timing = True

    s = time.time()
    x,y= AlternateStock.get_query()
    print time.time() -s
    print x
    print y
    print "\n------\n"
    s = time.time()
    x,y= AlternateStock.get_query(isbn='13212312312312')
    print time.time() -s
    print x
    print y

    def show(result):
        print "SHOW: %s" % (result,)
        for row in result:
            print row

    df = AlternateStock.initialize_db_connection_pool()
    df.addCallback(lambda x: AlternateStock.get_records(isbn='hoopla'))
    df.addCallback(show)
    df.addCallback(lambda x: AlternateStock.get_records(isbn='hoopla'))
    df.addCallback(show)
    df.addCallback(lambda x: AlternateStock.get_records(isbn='hoopla'))
    df.addCallback(show)
    df.addCallback(lambda x: AlternateStock.get_records(isbn='hoopla'))
    df.addCallback(show)
    return df


if __name__ == "__main__":
    task.react(main)

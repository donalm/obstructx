#!/usr/bin/env python

from twisted.web import resource
from twisted.web import server


from obstructx import db_introspect
from obstructx import db_pool
from obstructx import log

logger = log.get_logger()


class Root(resource.Resource):

    def q(self):
        logger.error("Q")
        self.pool = db_pool.Pool("booktown")
        df = self.pool.start()
        return df

    def render_GET(self, request):
        logger.error("render_GET")

        df = self.build_result_list(request)
        return server.NOT_DONE_YET

    def build_result_list(self, request):
        logger.error("build_result_list")
        df = self.q()
        df.addCallback(self.get_tables)
        df.addCallback(self.display_tables, request)
        return df

    def eb(self, f):
        logger.error(f.getBriefTraceback())
        return f

    def get_tables(self, *args):
        logger.error("get_tables")
        query = db_introspect.queries["list_tables"]
        return self.pool.runQuery(query)

    def display_tables(self, tables, request):
        logger.error("display_tables")

        lines = []
        for table in tables:
            lines.append("""<li><a href="/table/{table}" title="View table details">{table}</a></li>""".format(table=table.table_name))

        lines = "\n".join(lines)

        request.write("<html>Tables<ul>{lines}</ul><html>".format(lines=lines))
        request.finish()

    def getChild(self, name, request):
        logger.error("getChild: %s path:%s  uri:%s   responseHeaders:%s" % (name, request.path, request.uri, request.responseHeaders,))

        fragments = request.path.lstrip("/").split("/")
        l = len(fragments)
        if fragments[0].lower() == 'table':
            if l == 2:
                return Table(fragments)
            if l == 3:
                return Column(fragments)
        if name == "":
            return self
        return resource.Resource.getChild(self, name, request)


class Table(resource.Resource):

    def __init__(self, fragments):
        resource.Resource.__init__(self)
        self.fragments = fragments
        self.table = fragments[1]

    def q(self):
        logger.error("Q")
        self.pool = db_pool.Pool("booktown")
        df = self.pool.start()
        return df

    def render_GET(self, request):
        logger.error("render_GET: Fragments: %s" % (self.fragments,))

        df = self.build_result_list(request)
        return server.NOT_DONE_YET

    def get_columns(self, *args):
        logger.error("get_columns")
        try:
            query = db_introspect.queries["list_table_columns"]
        except Exception, e:
            logger.error(str(db_introspect.queries.keys()))
        return self.pool.runQuery(query, (self.table,))

    def display_columns(self, columns, request):
        logger.error("display_columns")

        lines = []
        for column in columns:
            lines.append("""<li><a href="/table/{table}/{column}" title="View column details">{column}</a></li>""".format(table=self.table, column=column.column_name))

        lines = "\n".join(lines)

        request.write("<html>columns<ul>{lines}</ul><html>".format(lines=lines))
        request.finish()

    def eb(self, f):
        logger.error(f.getBriefTraceback())
        return f

    def build_result_list(self, request):
        logger.error("build_result_list")
        df = self.q()
        df.addCallback(self.get_columns)
        df.addCallback(self.display_columns, request)
        df.addErrback(self.eb)
        return df

    def getChild(self, name, request):
        logger.error("getChild 2: %s %s" % (name, request,))
        return self

class Column(Table):

    def __init__(self, fragments):
        Table.__init__(self, fragments)
        self.column = fragments[2]

    def build_result_list(self, request):
        logger.error("build_result_list")
        df = self.q()
        df.addCallback(self.get_column)
        df.addCallback(self.display_column, request)
        df.addErrback(self.eb)
        return df

    def get_column(self, *args):
        try:
            query = db_introspect.queries["list_table_columns"]
        except Exception, e:
            logger.error(str(db_introspect.queries.keys()))
        return self.pool.runQuery(query, (self.table,))

    def display_column(self, columns, request):
        logger.error("display_column")

        lines = []
        nav = """<a href="/table/{table}" title="View table details">{table}</a>""".format(table=self.table,)
        for column in columns:
            if not column.column_name == self.column:
                continue
            record = vars(column)
            keys = record.keys()
            for key in keys:
                lines.append("""<tr><td>{key}:</td><td>{value}</td></tr>""".format(key=key, value=record.get(key)))

        lines = "\n".join(lines)

        request.write("<html>{nav}<br/>column details<table>{lines}</table><html>".format(lines=lines, nav=nav))
        request.finish()

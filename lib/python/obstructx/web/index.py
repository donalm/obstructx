#!/usr/bin/env python

from twisted.web import resource
from twisted.web import server


from obstructx import db_introspect
from obstructx import db_pool

class Root(resource.Resource):

    def q(self):
        print("Q")
        self.pool = db_pool.Pool("booktown")
        df = self.pool.start()
        return df

    def render_GET(self, request):
        print("render_GET")

        df = self.build_tables_list(request)
        return server.NOT_DONE_YET

    def build_tables_list(self, request):
        print("build_tables_list")
        df = self.q()
        df.addCallback(self.get_tables)
        df.addCallback(self.display_tables, request)
        return df

    def eb(self, f):
        print f.getBriefTraceback()
        return f

    def get_tables(self, *args):
        print("get_tables")
        query = db_introspect.queries["list_tables"]
        return self.pool.runQuery(query)

    def display_tables(self, tables, request):
        print("display_tables")

        lines = []
        for table in tables:
            lines.append("""<li><a href="/table/{table}" title="View table details">{table}</a></li>""".format(table=table.table_name))

        lines = "\n".join(lines)

        request.write("<html>Tables<ul>{lines}</ul><html>".format(lines=lines))
        request.finish()

    def getChild(self, name, request):
        print("getChild: %s %s" % (name, request,))
        if name == "":
            return self
        return resource.Resource.getChild(self, name, request)


class Table(resource.Resource):

    def q(self):
        print("Q")
        self.pool = db_pool.Pool("booktown")
        df = self.pool.start()
        return df

    def render_GET(self, request):
        print("render_GET")

        df = self.build_tables_list(request)
        return server.NOT_DONE_YET

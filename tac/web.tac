#!/usr/bin/env python

from obstructx.log import get_logger
from twisted.application import internet, service
from twisted.python import log
from twisted.web import server
from twisted.web import resource
from twisted.internet import reactor


appname = "obstructx"

class Root(resource.Resource):
    def render_GET(self, request):
        print("render_GET")
        return "<html>Hello, world!</html>"

    def getChild(self, name, request):
        print("getChild: %s %s" % (name, request,))
        if name == "":
            return self
        return resource.Resource.getChild(self, name, request)

class Simple(resource.Resource):
    #isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world 2!</html>"

root = Root()
root.putChild("hoops", Simple())

logger = get_logger(appname)
logger.error("TEST - TAC FILE")

observer = log.PythonLoggingObserver(loggerName=appname)
application = service.Application(appname)
application.setComponent(log.ILogObserver, observer.emit)

site = server.Site(root)
sc = service.IServiceCollection(application)
i = internet.TCPServer(8080, site)
i.setServiceParent(sc)

#!/usr/bin/env python

from twisted.application import internet, service
from twisted.python import log
from twisted.web import server
from twisted.web import resource
from twisted.internet import reactor

from obstructx import config
from obstructx.log import get_logger
from obstructx.web import index

appname = "obstructx"
config.Config.init(appname)

class Simple(resource.Resource):
    #isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world 2!: %s</html>" % (request.path,)

root = index.Root()
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

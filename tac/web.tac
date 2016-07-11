#!/usr/bin/env python

from twisted.application import internet, service
from twisted.python import log
from twisted.web import server
from twisted.web import resource
from twisted.internet import reactor

appname = "obstructx"
from obstructx import config
config.Config.init()

from obstructx.log import get_logger
logger = get_logger(appname)

from obstructx.web import index


class Simple(resource.Resource):
    #isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world 2!: %s</html>" % (request.path,)

root = index.Root()
root.putChild("hoops", Simple())

observer = log.PythonLoggingObserver(loggerName=appname)
application = service.Application(appname)
application.setComponent(log.ILogObserver, observer.emit)

site = server.Site(root)
sc = service.IServiceCollection(application)
i = internet.TCPServer(8080, site)
i.setServiceParent(sc)

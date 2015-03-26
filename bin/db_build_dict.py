#!/usr/bin/env python

import json
from twisted.python import log
from collections import OrderedDict

appname = "obstructx"
from obstructx import config
config.Config.init(appname)

from obstructx.log import get_logger
logger = get_logger(appname)
logger.error("OBSTRUCTX DATABASE SCHEMA TRAWLER")

from twisted.internet import reactor
from twisted.internet import defer

from obstructx import db_introspect
from obstructx import db_pool
from obstructx import log
from obstructx import db_build_dict

logger = log.get_logger()


def eb(f):
    logger.error(f.getBriefTraceback())

def stop(x):
    reactor.stop()
    data = json.dumps(db_build_dict.Inquisitor.data, indent=4)
    print(data)
    fh = open("/tmp/database.json", "w")
    fh.write(data)
    fh.close()

def main():
    inquisitor = db_build_dict.Inquisitor()
    df = inquisitor.get_database_metadata('booktown')
    df.addErrback(eb)
    df.addBoth(stop)


if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()

#!/usr/bin/env python

import sys
import json
import argparse
from twisted.python import log
from collections import OrderedDict

appname = "obstructx"
from obstructx import config
config.Config.init()

from obstructx.log import get_logger
logger = get_logger(appname)
logger.error("OBSTRUCTX DATABASE SCHEMA TRAWLER")

from twisted.internet import reactor
from twisted.internet import defer

from obstructx import log
from obstructx import db_build_dict

logger = log.get_logger()


def eb(f):
    logger.error(f.getBriefTraceback())

def stop(x, database_name, json_filename):
    reactor.stop()
    data = json.dumps(db_build_dict.Inquisitor.data[database_name], indent=4, sort_keys=True)
    fh = open(json_filename, "w")
    fh.write(data)
    fh.close()
    print("JSON file created at " + json_filename)

def main(database_name, json_filename):
    inquisitor = db_build_dict.Inquisitor(database_name)
    df = inquisitor.get_database_metadata()
    df.addErrback(eb)
    df.addBoth(stop, database_name, json_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Parse a PostgreSQL database schema into JSON.',
            usage="db_build_dict [-h] DATABASE"
        )
    parser.add_argument('database_name', metavar="DATABASE", type=str,
                        help='The name of the database')

    parser.add_argument('json_filename', metavar="FILEPATH", type=str,
                        help='A path to write the JSON file')

    args = parser.parse_args()

    reactor.callWhenRunning(main, args.database_name, args.json_filename)
    reactor.run()

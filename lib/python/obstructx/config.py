#!/usr/bin/env python
"""
This module gets the application's config from project/etc
We can't log in here, as the logging module has to import
config before it can configure itself to start logging
"""

import os
import json
from twisted.python.modules import getModule

BASEDIR=os.environ.get("BASEDIR")


class Config(object):
    data = {}

    @classmethod
    def init(cls, appname):
        if cls.data.get(appname):
            return

        cls.refresh(appname)
        return None

    @classmethod
    def refresh(cls, appname):
        json_config_file = os.path.join(BASEDIR, "etc/config_data.json")
        print(json_config_file)
        fh = open(json_config_file, 'r')
        try:
            cls.data[appname] = json.load(fh)
        except Exception, e:
            raise
        finally:
            fh.close()

    @classmethod
    def get(cls, appname, key):
        cls.init(appname)
        return cls.data.get(appname, {}).get(key)


if __name__ == '__main__':
    c = Config()
    print c.get('database')

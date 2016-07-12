#!/usr/bin/env python
"""
This module gets the application's config from project/etc
We can't use the log in this file, as the logging module has to import config
before it can configure itself to start logging
"""

import os
import json

BASEDIR=os.environ.get("BASEDIR")

class Config(object):
    data = None

    @classmethod
    def init(cls):
        if cls.data is None:
            cls.refresh()

    @classmethod
    def refresh(cls):
        json_config_file = os.path.join(BASEDIR, "etc/config_data.json")
        fh = open(json_config_file, 'r')
        try:
            cls.data = json.load(fh)
        except Exception, e:
            raise
        finally:
            fh.close()

    @classmethod
    def get(cls, key):
        cls.init()
        return cls.data.get(key)


if __name__ == '__main__':
    c = Config()
    print c.get('database')

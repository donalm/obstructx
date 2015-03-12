#!/usr/bin/env python
"""
This module gets the application's config from project/etc
We can't log in here, as the logging module has to import
config before it can configure itself to start logging
"""

import os
import json
from twisted.python.modules import getModule



class Config(object):
    data = {}

    @classmethod
    def init(cls):
        if cls.data:
            return

        cls.refresh()

    @classmethod
    def refresh(cls):
        """
        Go back to the filesystem and re-read the config file
        """
        try:
            filepath = getModule(__name__).filePath
            basedir = filepath.parent().parent().parent().parent().path
        except Exception, e:
            print("Failed to get project basedir: %s" % (e,))
            raise

        json_config_file = os.path.join(basedir, "etc/config_data.json")
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

#!/usr/bin/env python

import os
from .config import Config
from logging.handlers import TimedRotatingFileHandler

import logging

def get_logger(appname):
    config = Config()
    log_config         = config.get(appname, "log")
    log_level          = log_config.get("level")
    log_path_templates = log_config.get("paths")
    log_path           = get_log_path(appname, log_path_templates)

    formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(message)s    [%(process)d:%(pathname)s:%(lineno)d]')

    trfh = TimedRotatingFileHandler(log_path, when='D', interval=1, backupCount=5, encoding='utf-8')
    trfh.setFormatter(formatter)
    logger = logging.getLogger(appname)
    logger.addHandler(trfh)
    logger.error("trfh")
    logger.setLevel(logging.DEBUG)
    return logger

def get_log_path(appname, log_path_templates):
    for log_path_template in log_path_templates:
        try:
            log_path = log_path_template.format(appname=appname)
            try:
                os.makedirs(os.path.dirname(log_path), 0755)
            except OSError, e:
                if e.errno != 17:
                    # We can ignore a 'directory exists' error
                    raise

            fh = open(log_path, 'a')
            fh.write("-- starting up --")
            fh.close()
            return log_path
        except Exception, e:
            pass

    raise Exception("Failed to find a writeable log path in config")

#!/usr/bin/env python

import os
import shutil
import tempfile
from twisted.trial import unittest

from obstructx import versionup

class DirectoryHelper(object):
    temp_directories = []

    @classmethod
    def make_directory(cls):
        cls.temp_directories.append(tempfile.mkdtemp(prefix="versionup_test"))
        return cls.temp_directories[-1]

    @classmethod
    def cleanup(cls):
        for d in cls.temp_directories[:]:
            try:
                cls.temp_directories.remove(d)
                shutil.rmtree(d)
            except Exception, e:
                pass
        
    

class VersionUpTests(unittest.TestCase):
    def test_get_latest(self):
        basedir = DirectoryHelper.make_directory()
        template_name = test_template
        new_directory = versionup.VersionUp.create_next_directory(template_name, basedir=basedir)
        self.assertEqual(new_directory, os.path.join(basedir, template_name, "0000")
        new_directory = versionup.VersionUp.create_next_directory(template_name, basedir=basedir)
        self.assertEqual(new_directory, os.path.join(basedir, template_name, "0001")

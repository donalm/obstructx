#!/usr/bin/env python

import json
from twisted.python.filepath import FilePath

def main():
    contents = FilePath(__file__).sibling("config_data.json").getContent()
    try:
        json.loads(contents)
    except Exception, e:
        print("\nERROR: Not valid JSON: %s\n" % (e,))
        raise
    else:
        print("JSON is valid")


if __name__ == '__main__':
    main()

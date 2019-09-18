#!/usr/bin/env python3
import re
import logging
import xml.etree.ElementTree as ET


NAMESPACES = {'bcf': "https://sourceforge.net/projects/biblatex"}


def get_keys(filename):
    parser = ET.parse(filename)
    root = parser.getroot()
    return {item.text for item in root.findall('.//bcf:citekey', NAMESPACES)}


def get_items_from_bib(keys, filename):
    with open(filename, 'r') as f:
        contents = f.read()
    regex = re.compile(
        r"""
        ^@ \w+ \{ (%s),$\n          # KEY
          .*?                    # BODY
        ^\}$""" % '|'.join(keys),
        re.MULTILINE | re.VERBOSE | re.DOTALL)
    for match in regex.finditer(contents):
        string = match.group(0)
        logging.info("Found %s", string.split('\n')[0])
        yield string


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <bcf-file> <bibfile...>")
        sys.exit(1)
    bcf_file = sys.argv[1]
    bibfiles = sys.argv[2:]
    keys = get_keys(bcf_file)
    print(f"% This file is managed by {sys.argv[0]} and should not be edited!")
    for bibfile in bibfiles:
        for item in get_items_from_bib(keys, 'cryptobib/crypto.bib'):
            print(item)
            print()

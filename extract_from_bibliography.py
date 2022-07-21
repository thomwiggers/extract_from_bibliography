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
        ^@ \w+ \{ (?P<key>%s),$\n          # KEY
          .*?                    # BODY
        ^\}$""" % '|'.join(map(re.escape, keys)),
        re.MULTILINE | re.VERBOSE | re.DOTALL)
    for match in regex.finditer(contents):
        key = match.group("key")
        item = match.group(0)
        logging.info("Found %s", item.split('\n')[0])
        yield key, item


if __name__ == "__main__":
    logging.basicConfig()

    import sys
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <bcf-file> <bibfile...>")
        sys.exit(1)
    bcf_file = sys.argv[1]
    bibfiles = sys.argv[2:]
    keys = get_keys(bcf_file)
    found_items = dict()
    print(f"% This file is managed by {sys.argv[0]} and should not be edited!")

    for bibfile in bibfiles:
        for key, item in get_items_from_bib(keys, bibfile):
            if key not in found_items:
                found_items[key] = {"content": item, "file": bibfile, "also_found": []}
            else:
                logging.warning("Already printed %s before, second definition found in %s", key, bibfile)
                found_items[key]["also_found"].append({"file": bibfile, "content": item})

    for key, item in found_items.items():
        print(f"% Found in {item['file']}")
        print(item["content"])
        print()
        for second_item in item["also_found"]:
            print(f"% Also found in {second_item['file']}")
            for line in second_item["content"].splitlines():
                print(f"% {line}")
            print()

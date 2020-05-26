#!/usr/bin/env python

import random
import json
import os
import sys
import re
import requests
from copy import deepcopy

here = os.path.abspath(os.path.dirname(__file__))


def load_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


# Load the sites lookup to generate urls for
cookies = load_json(os.path.join(here, "url-cookies.json"))
counts = load_json(os.path.join(here, "url-counts.json"))
fullresults = load_json(os.path.join(here, "url-header-results-cookies.json"))
results = load_json(os.path.join(here, "url-header-results.json"))


def main():

    print("What kind of server do the sites use?")
    server_counts = dict()
    for name, meta in results.items():
        if "server" in meta["_store"]:
            # Get rid of any verison string
            server = meta["_store"]["server"][1].split("/")[0].lower()
            if server not in server_counts:
                server_counts[server] = 0
            server_counts[server] += 1
    server_counts = sorted(server_counts.items(), key=lambda x: x[1], reverse=True)
    print(json.dumps(dict(server_counts), indent=4))

    print("\n\n Which sites have the most headers?")
    header_counts = dict()
    for name, meta in results.items():
        header_counts[name] = len(meta["_store"])
    header_counts = sorted(header_counts.items(), key=lambda x: x[1], reverse=True)
    print(json.dumps(dict(header_counts), indent=4))

    print("\n\nWhat about powered-by?")
    powered_by = dict()
    for name, meta in results.items():
        if "x-powered-by" in meta["_store"]:
            by = meta["_store"]["x-powered-by"][1].split("/")[0].strip()
            if by not in powered_by:
                powered_by[by] = 0
            powered_by[by] += 1
    powered_by = sorted(powered_by.items(), key=lambda x: x[1], reverse=True)
    print(json.dumps(dict(powered_by), indent=4))


if __name__ == "__main__":
    main()

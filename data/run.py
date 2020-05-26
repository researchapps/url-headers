#!/usr/bin/env python

import random
import json
import os
import re
import requests
from copy import deepcopy

here = os.path.abspath(os.path.dirname(__file__))


def load_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def save_json(obj, filename):
    with open(filename, "w") as fd:
        fd.write(json.dumps(obj, indent=4))
    return filename


def read_file(filename, lines=True, strip_newlines=True):
    with open(filename, "r") as fd:
        if lines:
            content = fd.readlines()
            if strip_newlines:
                content = [x.strip() for x in content]
        else:
            content = fd.read()
    return content


# Load the sites lookup
url_file = os.environ.get("INPUT_URLS", os.path.join(here, "urls.txt"))
urls = read_file(url_file, lines=True)


def get_user_agent():
    """
    Return a randomly chosen user agent for requests

    Returns:
        user agent string to include with User-Agent.
    """
    agents = [
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/57.0.2987.110 "
            "Safari/537.36"
        ),  # chrome
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.79 "
            "Safari/537.36"
        ),  # chrome
        (
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) "
            "Gecko/20100101 "
            "Firefox/55.0"
        ),  # firefox
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.91 "
            "Safari/537.36"
        ),  # chrome
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/62.0.3202.89 "
            "Safari/537.36"
        ),  # chrome
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/63.0.3239.108 "
            "Safari/537.36"
        ),  # chrome
    ]
    return random.choice(agents)


def main():
    counts = {}
    results = {}

    for url in urls:
        if url in results:
            continue
        try:
            print(f"Parsing {url}")
            response = requests.get(url, headers={"User-Agent": get_user_agent()})
        except:
            response = None
            pass

        if not response:
            print(f"Issue parsing {url}")
            continue

        results[url] = deepcopy(response.headers.__dict__)

        # iterate through the headers
        for header, value in response.headers.items():

            # make all lowercase for consistency
            header = header.lower()

            if header not in counts:
                counts[header] = 0
            counts[header] += 1

    # Sort by value
    counts = {
        k: v for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True)
    }

    # Save results with cookies (won't be put into version control)
    save_json(results, os.path.join(here, "url-header-results-cookies.json"))

    # Let's count cookies too!
    cookies = {}

    # Clean up cookies to only include names
    for url, meta in results.items():
        if "set-cookie" in meta["_store"]:
            cookie = meta["_store"]["set-cookie"][1]
            cookie_name = meta["_store"]["set-cookie"][0]
            cookie = list(set([c.split("=")[0].strip() for c in cookie.split(";")]))
            meta["_store"]["set-cookie"] = [cookie_name, cookie]
            for c in cookie:
                if len(c) > 100:
                    continue
                if c not in cookies:
                    cookies[c] = 0
                cookies[c] += 1

    # Prepare for data frame import
    headers = [{"name": key, "count": value} for key, value in counts.items()]

    # Save results to file
    save_json(counts, os.path.join(here, "url-counts.json"))
    save_json(cookies, os.path.join(here, "url-cookies.json"))
    save_json(headers, os.path.join(here, "url-header-counts.json"))
    save_json(results, os.path.join(here, "url-header-results.json"))


if __name__ == "__main__":
    main()

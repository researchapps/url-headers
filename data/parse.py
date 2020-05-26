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


def save_html(content, filename):
    with open(filename, "w") as fd:
        fd.write(content)
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


# These are the urls we need to get
port = os.environ.get("INPUT_PORT", "5000")
baseurl = "http://localhost:%s/" % port

# Load the sites lookup to generate urls for
url_file = os.environ.get("INPUT_URLS", os.path.join(here, "urls.txt"))
sites = read_file(url_file, lines=True)
cookies = load_json(os.path.join(here, "url-cookies.json"))
counts = load_json(os.path.join(here, "url-counts.json"))


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


def main(outdir):

    # Keep a record of pages created
    links = {
        "home": "index.html",
        "cookies": "cookies/index.html",
        "sites": {},
        "headers": {},
        "cookies": {},
    }

    # Create subfolders for cookies, and site
    for dirname in ["cookies", "site", "header"]:
        if not os.path.exists(os.path.join(outdir, dirname)):
            os.mkdir(os.path.join(outdir, dirname))

    # Generate primary cookies / home page
    response = requests.get(f"{baseurl}")
    save_html(response.text, os.path.join(outdir, "index.html"))
    response = requests.get(f"{baseurl}cookies")
    save_html(response.text, os.path.join(outdir, "cookies", "index.html"))

    # Generate site-specific urls
    for url in sites:

        # Add page for site
        prefix = url.replace("https://", "", 1)
        output_dir = os.path.join(outdir, "site", prefix)
        links["sites"][prefix] = os.path.join("site", prefix + "/")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "index.html")
        if not os.path.exists(output_file):
            response = requests.get(f"{baseurl}site/{prefix}")
            if response.status_code != 200:
                print(f"Problem parsing {url}")
                continue
            save_html(response.text, output_file)

    # Create a page for each cookie
    for cookie in cookies:
        output_dir = os.path.join(outdir, "cookies", cookie)
        links["cookies"][cookie] = os.path.join("cookies", cookie + "/")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "index.html")
        if not os.path.exists(output_file):
            response = requests.get(f"{baseurl}cookies/{cookie}")
            if response.status_code != 200:
                print(f"Problem parsing cookie url {cookie}")
                continue
            save_html(response.text, output_file)

    # Create a page for each header
    for header in counts:
        output_dir = os.path.join(outdir, "header", header)
        links["headers"][header] = os.path.join("header", header + "/")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, "index.html")
        if not os.path.exists(output_file):
            response = requests.get(f"{baseurl}header/{header}")
            if response.status_code != 200:
                print(f"Problem parsing header url {header}")
                continue
            save_html(response.text, output_file)

    # Write a readme
    readme = """# HTML Headers\n This is a static version of the flask application to 
inspect html headers. The following links were derived:\n\n"""

    for name, link in links.items():
        if isinstance(link, str):
            readme += " - [%s](%s)\n" % (name, link)
        elif isinstance(link, dict):
            readme += "\n## %s\n\n" % name.capitalize()
            for item, sublink in link.items():
                readme += " - [%s](%s)\n" % (item, sublink)
            readme += "\n\n"
    save_html(readme, os.path.join(outdir, "README.md"))


if __name__ == "__main__":
    outdir = "docs"
    if len(sys.argv) > 1:
        outdir = sys.argv[1]
    main(os.path.abspath(outdir))

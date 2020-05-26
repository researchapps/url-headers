"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from flask import Flask, flash, url_for, redirect
from flask import render_template
from datetime import time
import json
import random
import string


def read_json(filename):
    """helper function to load json data on app load"""
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def generate_key():
    punctuation = "!#$%&()*+,-./:;<=>?@^_{|}~"
    choices = string.ascii_letters + string.digits + punctuation
    selected = [random.SystemRandom().choice(choices) for _ in range(50)]
    return "".join(selected)


# Data loaded once on init
counts = read_json("data/url-counts.json")
cookies = read_json("data/url-cookies.json")
results = read_json("data/url-header-results.json")

# Instantiate the flask app
app = Flask(__name__)
app.secret_key = generate_key()


@app.route("/")
def index():
    """The index (home) view shows a bar chart of headers (Y) by counts (X)
    """
    legend = "Header Counts"
    labels = list(counts.keys())
    values = list(counts.values())
    return render_template("barchart.html", values=values, labels=labels, legend=legend)


@app.route("/url-headers/cookies/")
def cookielist():
    """An equivalent table, but we use cookies instead.
    """
    legend = "Cookie Counts"
    labels = list(cookies.keys())
    values = list(cookies.values())
    return render_template(
        "barchart.html", values=values, labels=labels, legend=legend, title="Cookies"
    )


@app.route("/url-headers/header/<name>/")
def header(name):

    # The header must be known
    if name not in counts:
        flash(f"{name} is not a valid header value.")
        return redirect(url_for("index"))

    name = name.lower()

    # Collect site specific variables
    sites = dict()
    for site, values in results.items():
        if name in values["_store"]:
            value = values["_store"][name]
            if isinstance(value[1], list):
                value[1] = ", ".join(value[1]).strip()
            value[1] = str(value[1].replace('"', "'"))
            sites[site] = {"value": value, "site": results[site]}

    return render_template("header.html", values=sites, name=name.upper())


@app.route("/url-headers/site/<path:name>/")
def site(name):

    # Add https back
    name = "https://%s" % name

    # The header must be known
    if name not in results:
        flash(f"{name} is not a valid site.")
        return redirect(url_for("index"))

    values = {
        k: str(v[1]).replace('"', "'") for k, v in results[name]["_store"].items()
    }
    name = name.lower()
    return render_template("site.html", name=name, values=values, nexturl="header")


@app.route("/url-headers/cookies/<name>/")
def cookie(name):

    # The header must be known
    if name not in cookies:
        flash(f"{name} is not a valid cookie value.")
        return redirect(url_for("cookielist"))

    # Collect site specific variables
    sites = dict()
    for site, values in results.items():
        if (
            "set-cookie" in values["_store"]
            and name in values["_store"]["set-cookie"][1]
        ):
            sites[site] = {"value": "*", "site": results[site]}

    return render_template(
        "header.html", values=sites, name=name.upper(), title="Cookie"
    )


if __name__ == "__main__":
    app.run(debug=True)

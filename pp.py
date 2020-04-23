#!/usr/bin/env python3

# ********************************************************
# Script validates if paper title was published or not.
#
# Handles reading input file and checking against
# Google to determine if previously published or not.
# If able to process successfully will print results
# to standard out.
#
# python3 pp.py [<input-file>|<title]>
#
# input-file: XLS or CVS of papers' corresponding titles to search
# title: individual paper title (string) to search on
#
# Example: python3 pp.py "Curing Cancer with Bleach"
#
# If successful exit code is 0
# If fails exit code is > 0
# ********************************************************

import requests
import os, sys
import urllib.parse
from bs4 import BeautifulSoup

def err(s=None):
    """
    Converts string to bytes & Outputs to stderr
    """
    if not s:
        return
    s= s + "\n"
    os.write(2, s.encode())

def is_valid_file(fname=None):
    if not fname:
        return False
    fname = fname.strip()
    return os.path.isfile(fname)

def search(paper_title=None):
    global SEARCH_URL
    global USER_AGENT
    results = []

    if not paper_title:
        return results

    # encode query string param before search
    params = {'q': paper_title}
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = SEARCH_URL + query
    print(url)

    # desktop user-agent; expected by google in HTTP header
    headers = {"user-agent" : USER_AGENT}
    resp = requests.get(url, headers=headers)

    # check if valid response
    if resp.status_code != 200:
        err("Failed - unsuccessful response from Google status code: " + str(resp.status_code))
        return results

    # parse HTTP response and pull out search results
    soup = BeautifulSoup(resp.content, "html.parser")

    for g in soup.find_all('div', class_='r'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            title = g.find('h3').text
            item = {
                "title": title,
                "link": link
            }
            results.append(item)
    print(results)

def main():
    global SEARCH_URL
    global USER_AGENT

    if len(sys.argv) < 2:
        err("Invalid input arguments")
        sys.exit(1)

    titles = []
    input = sys.argv[1]
    print(input)
    if is_valid_file(input):
        # read input file
        pass # read files
    else:
        # invalid file treat cmd line arg as title to search directly for
        titles.append(input)

    # search on title
    for title in titles:
        search(title)

    # direct much on title

    # no direct match fuzzy match
    sys.exit(0)

# ----------------------------------------------------------------------
# M A I N  L O G I C
# ----------------------------------------------------------------------
SEARCH_URL = "https://google.com/search?"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

if __name__ == "__main__":
    main()
    sys.exit(0)

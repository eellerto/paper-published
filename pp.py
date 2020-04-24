#!/usr/bin/env python3

# ********************************************************
# Script validates if paper title was published or not.
#
# Handles reading input file and checking against
# Google to determine if previously published or not.
# If able to process successfully will print results
# to standard out.
#
# python3 pp.py [<excel-input-file>|<title]>
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
import io, os, sys
import puremagic
import urllib.parse
import xlrd
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

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
    #print(url)

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
    return results

def is_filetype(filename=None, search_str=None):
    """
    Applies magic byte (header) inspection to determine if of search file type.
    """
    if not search_str:
        return False
    results = puremagic.magic_file(filename)
    for result in results:
        if search_str.lower() in result.name.lower():
            return True
    return False

def xls_to_xlsx(filename=None):
    """
    Attempts to convert legacy XLS (Excel) file to XLSX (newer) version for processing
    Needed b/c Cognos is garbage and sends corrupted legacy XLS files via download.
    """
    xls_file= io.open(filename, "r", encoding="utf-16")
    data = xls_file.readlines()
    # create and save a new Excel workbook
    # https://medium.com/@jerilkuriakose/recover-corrupt-excel-file-xls-or-xlsx-using-python-2eea6bb07aae
    pass

def read_xlsx(filename=None):
    """
    Reads file contents and returns a list of pairs including
    each manuscript id and corresponding manuscript title.
    """
    results = []
    if not filename:
        return results
    # TODO append file read
    # find column header w/ manuscript's id and title
    return results

def main():
    global SEARCH_URL
    global USER_AGENT

    if len(sys.argv) < 2:
        err("Invalid input arguments: " + sys.argv[0] + " [<excel-input-file>|<paper-title>]")
        sys.exit(1)

    # TODO check file type
    # if XLS convert to XLSX (corrupt cannot read via XLRD)
    # See https://medium.com/@jerilkuriakose/recover-corrupt-excel-file-xls-or-xlsx-using-python-2eea6bb07aae

    titles = []
    input = sys.argv[1]

    if is_valid_file(input):
        if is_filetype(input, "Microsoft Excel") is False:
            # possibly correct file via Cognos and XLS try to convert to XLSX
            print("Convert to XLSX")
            #xls_to_xlsx(input)
        # read input file
        data = read_xlsx(input)
        print(data)
    else:
        # invalid file treat cmd line arg as title to search directly for
        titles.append(input)

    # search on title - only initial top 10 results from Google
    hdr_shown = False
    for title in titles:
        results = search(title)
        #print(results)

        # check direct or partial ratio match on title
        for result in results:
            if title in result["title"] is False:
                continue

            direct = fuzz.ratio(title, result["title"])
            partial = fuzz.partial_ratio(title, result["title"])

            # output results
            if not hdr_shown:
                print("Paper Title,", "Search Title,", "Direct Match,", "Partial Match,", "Link")
                hdr_shown = True
            print("%s,%s,%.2f,%.2f,%s" % (title, result["title"], direct, partial, result["link"]))

    sys.exit(0)

# ----------------------------------------------------------------------
# M A I N  L O G I C
# ----------------------------------------------------------------------
SEARCH_URL = "https://google.com/search?"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

if __name__ == "__main__":
    main()
    sys.exit(0)

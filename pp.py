#!/usr/bin/env python3

# ********************************************************
# Script validates if paper title was published or not.
#
# Handles rcading input file and checking against
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
import io, os, sys, csv, time
import puremagic
import urllib.parse
import xlrd, mmap
import xlsxwriter as xs
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

def extract_xlsx(fname=None, search_hdrs=None):
    """
    Reads file contents and returns a list of pairs including
    each manuscript id and corresponding manuscript title.
    """
    results = []

    if fname is None or search_hdrs is None:
        err("Invalid CSV extraction for filename and column headers: " + fname + " ".join(search_hdrs))
        return results

    # extract corresponding data rows to columns for specific headers
    wb = xlrd.open_workbook(fname)
    ws = wb.sheet_by_index(0)

    # find index headers occur
    headers = []
    for i in range(len(ws.row(0))):
        if ws.row(0)[i].value in search_hdrs:
            item = {
                "header": ws.row(0)[i].value,
                "index": i
            }
            headers.append(item)

    # extract data after first row
    results = []
    for i in range(1, ws.nrows):
        result = {}
        for hdr in headers:
            #print(hdr.get("header"))
            #print(ws.row(i)[hdr.get("index")].value)
            item = {
                hdr.get("header"): ws.row(i)[hdr.get("index")].value
            }
            result.update(item)
        results.append(result)

    #print(results)
    return results

def extract_csv(fname=None, search_hdrs=None):
    '''
    Reads a CSV file and extracts all rows for column header names requested.
    Returns a list of dictionary with column name and corresponding row value in matrix
    '''
    results = []

    if fname is None or search_hdrs is None:
        err("Invalid CSV extraction for filename and column headers: " + fname + " ".join(search_hdrs))
        return results

    result = {}
    # extract corresponding data rows to columns for specific headers
    with open(fname, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line in reader:
            result = dict((k, line[k]) for k in search_hdrs if k in line)
            #print(result)
            results.append(result)

    return results

# ----------------------------------------------------------------------
# M A I N  L O G I C
# ----------------------------------------------------------------------

def main():
    global SEARCH_URL
    global USER_AGENT
    global FILE_SEARCH_HDRS
    global TITLE

    if len(sys.argv) < 2:
        err("Invalid input arguments: " + sys.argv[0] + " [<input-file>|<paper-title>]")
        sys.exit(1)

    search_records = []
    input = sys.argv[1]

    if is_valid_file(input):
        if input.endswith('.csv'):
            data = extract_csv(input, FILE_SEARCH_HDRS)
        elif input.endswith('.xlsx'):
            data = extract_xlsx(input, FILE_SEARCH_HDRS)
        else:
            err("Unsupport file type - cannot convert: " + input)
            sys.exit(2)
        search_records = data
    else:
        # invalid file not exist - treat cmd line arg as title to search directly via Google
        item = {
            ID: "NA",
            TITLE: input
        }
        search_records.append(item)

    # search on title - only initial top 10 results from Google
    hdr_shown = False
    results = []

    # output results to XLSX file
    wb = xs.Workbook("paper-published.xlsx")    # TODO timestamp file unique
    ws = wb.add_worksheet()

    for rec in search_records:
        #print("Searching: " + rec[ID] + "-" + rec[TITLE])
        results = search(rec[TITLE])
        time.sleep(THROTTLE_SECS)   # avoid being blocked by google - rate limit calls

        # check direct or partial ratio match on title
        for result in results:
            if rec[TITLE] in result["title"] is False:
                continue

            direct = fuzz.ratio(rec[TITLE], result["title"])
            partial = fuzz.partial_ratio(rec[TITLE], result["title"])

            # output results
            if not hdr_shown:
                print("Paper ID,", "Paper Title,", "Search Title,", "Direct Match,", "Partial Match,", "Link")
                ws.write(0, 0, "Paper ID")
                ws.write(0, 1, "Paper Title")
                ws.write(0, 2, "Search Title")
                ws.write(0, 3, "Direct Match")
                ws.write(0, 4, "Partial Match")
                ws.write(0, 5, "Link")
                hdr_shown = True
            print("%s,\"%s\",\"%s\",%.2f,%.2f,%s" % (rec[ID], rec[TITLE], result["title"], direct, partial, result["link"]))

    wb.close()

    sys.exit(0)

# ==========================
# Global Variables
# ==========================
SEARCH_URL = "https://google.com/search?"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
ID = "Manuscript ID"
TITLE = "Manuscript Title"
FILE_SEARCH_HDRS = [
    ID,
    TITLE
]
THROTTLE_SECS = 1

if __name__ == "__main__":
    main()
    sys.exit(0)

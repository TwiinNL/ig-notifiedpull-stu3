#!/usr/bin/env python3
"""Tests of the Publication Request part of .github/scripts/check-qa.py, on fragments of qa.html
in the layout of IG Publisher 3.0.0 (renderers/PublicationChecker.java:60-100). Run from the repo
root, no build needed:  python3 test/check-qa.test.py"""
import importlib.util
import os
import sys
import tempfile

spec = importlib.util.spec_from_file_location("check_qa", ".github/scripts/check-qa.py")
check_qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_qa)

ERR = ' <img src="icon-error.gif" height="16px" alt="ERROR!" width="16px"/>'
WARN = ' <img src="icon-warning.png" alt="WARNING" height="16px" width="16px"/>'
INFO = ' <img src="information.png" height="16px" width="16px"/>'
SUMMARY = ('<table class="grid">\r\n <tr><td>package-id</td><td>nl.twiin.x</td></tr>\r\n'
           ' <tr><td>RelatedIgs</td><td>(None Found)</td></tr>\r\n</table>\r\n')
# A failing request has no rows for the checks that failed, only RelatedIgs.
SUMMARY_FAILING = '<table class="grid">\r\n <tr><td>RelatedIgs</td><td>(None Found)</td></tr>\r\n</table>\r\n'


def page(cell):
    return ('<table> <tr><td>Language Info:</td><td>x</td></tr>\r\n <tr><td><a href="https://c/">'
            'Publication Request</a>:</td><td>' + cell + '</td></tr>\r\n'
            ' <tr><td>Supressed Messages:</td><td>none</td></tr></table>')


def parse(html):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    try:
        return check_qa.publication_request(f.name)
    finally:
        os.unlink(f.name)


failed = False


def check(name, ok):
    global failed
    print(("ok   " if ok else "FAIL ") + name)
    failed = failed or not ok


check("all good", parse(page(SUMMARY + "No Messages found - all good")) == [])
check("one error",
      parse(page(SUMMARY + "No publication request category found" + ERR)) ==
      [("error", "No publication request category found")])
check("failing request with only RelatedIgs in the summary",
      parse(page(SUMMARY_FAILING + "<ul><li>Version 1 has already been published" + WARN + "</li>\r\n<li>Not first" + ERR + "</li>\r\n</ul>\r\n")) ==
      [("warning", "Version 1 has already been published"), ("error", "Not first")])
check("one warning",
      parse(page(SUMMARY + "Version 1 has already been published" + WARN)) ==
      [("warning", "Version 1 has already been published")])
check("list of messages, with markup and entities",
      parse(page(SUMMARY + "<ul><li><span title=\"x\">This IG has never been published</span>" + INFO +
                 "</li>\r\n<li>Version a &amp; b" + WARN + "</li>\r\n<li>Bad" + ERR + "</li>\r\n</ul>\r\n")) ==
      [("info", "This IG has never been published"), ("warning", "Version a & b"), ("error", "Bad")])
check("message without a known icon counts as error",
      parse(page(SUMMARY + "<ul><li>One</li><li>Two" + WARN + "</li></ul>")) ==
      [("error", "One"), ("warning", "Two")])
for name, html in [
    ("no row", "<table></table>"),
    ("row not closed", "<tr><td>Publication Request</a>:</td><td>" + SUMMARY),
    ("request not checked (no summary)", page("No output package found - can't check publication details" + WARN)),
    ("empty message", page(SUMMARY + "<ul><li>" + ERR + "</li></ul>")),
]:
    try:
        parse(html)
        check(name + " raises", False)
    except check_qa.PublicationRequestError:
        check(name + " raises", True)
sys.exit(1 if failed else 0)

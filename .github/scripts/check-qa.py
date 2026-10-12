#!/usr/bin/env python3
"""Fail on every publisher error, and every Publication Request error or warning, that is not
listed in known-errors.txt.

Three sources, because the publisher reports validation errors in qa.xml, errors from checking
the generated HTML (e.g. WCAG heading checks) only in qa.txt and qa.json, and the findings of
the publication request check only in qa.html:
- output/qa.xml (a Bundle of OperationOutcomes). Each error/fatal issue becomes one line
  "<location>: <message>", where location is the issue's expression (e.g.
  ImplementationGuide/<id>), or else the file name.
- output/qa.txt. Each "ERROR:" / "FATAL:" line becomes "<location>: <message>", with the
  absolute path of the output folder replaced by "output/" so the lines do not depend on
  the machine.
- output/qa.html, the row "Publication Request". PublicationChecker.check() builds that cell as
  an HTML string (IG Publisher 3.0.0, renderers/PublicationChecker.java:60-100; severity is an
  icon at the end of each message, mkError/mkWarning/mkInfo at :490-499) and Publisher.java:441
  passes it to ValidationPresenter, which puts it only in the qa.html header
  (ValidationPresenter.java:1116). It is in none of qa.xml, qa.txt and qa.json, and not in
  "errs". Each error or warning becomes one line "Publication Request: <message>"; information
  messages are ignored. Only checked when the repository has a publication-request.json: the
  section must then be there, show that the request was read (the row RelatedIgs of its summary)
  and be readable, or the check fails.
The errors of qa.xml and qa.txt, counted once when both report them, must equal "errs" in
output/qa.json. Lines are compared exactly with the non-comment lines of known-errors.txt.
"""
import html as htmllib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

NS = {"f": "http://hl7.org/fhir"}
FILE_EXT = "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"


def val(el, path):
    found = el.find(path, NS)
    return found.get("value") if found is not None else None


def errors(qa_xml):
    result = []
    for outcome in ET.parse(qa_xml).getroot().iter("{http://hl7.org/fhir}OperationOutcome"):
        file_ext = next((e for e in outcome.findall("f:extension", NS) if e.get("url") == FILE_EXT), None)
        file_name = os.path.basename(val(file_ext, "f:valueString") or "") if file_ext is not None else ""
        for issue in outcome.findall("f:issue", NS):
            if val(issue, "f:severity") not in ("error", "fatal"):
                continue
            location = val(issue, "f:expression") or file_name or "n/a"
            message = " ".join((val(issue, "f:details/f:text") or "").split())
            result.append(f"{location}: {message}")
    return result


def txt_errors(qa_txt):
    output_dir = os.path.abspath("output") + os.sep
    result = []
    with open(qa_txt, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"(?:ERROR|FATAL): (.*)", line.rstrip("\n"))
            if m:
                result.append(" ".join(m.group(1).replace(output_dir, "output/").split()))
    return result


PUB_LOCATION = "Publication Request"
PUB_ROW = 'Publication Request</a>:</td><td>'
PUB_ALL_GOOD = "No Messages found - all good"


class PublicationRequestError(Exception):
    pass


def publication_request(qa_html):
    """Returns the (severity, message) pairs of the Publication Request row of qa.html.

    severity is "error", "warning" or "info", from the icon the publisher puts after each
    message; a message without a known icon counts as an error. Raises PublicationRequestError
    when the row is missing or not in the layout of IG Publisher 3.0.0."""
    with open(qa_html, encoding="utf-8") as f:
        page = f.read()
    start = page.find(PUB_ROW)
    if start < 0:
        raise PublicationRequestError("no row 'Publication Request' in qa.html")
    cell = page[start + len(PUB_ROW):]
    summary = ""
    if cell.startswith('<table class="grid">'):
        end = cell.find("</table>")
        if end < 0:
            raise PublicationRequestError("the table of the publication request is not closed")
        end += len("</table>")
        summary, cell = cell[:end], cell[end:]
    end = cell.find("</td></tr>")
    if end < 0:
        raise PublicationRequestError("the row 'Publication Request' is not closed")
    cell = cell[:end].strip()
    # The summary only gets a row for a check that passed, so a failing request may have no
    # package-id; RelatedIgs is added whenever the request was read (PublicationChecker.java:60-66).
    if "<td>RelatedIgs</td>" not in summary:
        raise PublicationRequestError(
            "the request was not checked (no RelatedIgs row in its summary); "
            "the publisher found no output package or no publication-request.json")
    if cell == PUB_ALL_GOOD:
        return []
    items = re.findall(r"<li>(.*?)</li>", cell, re.S) if cell.startswith("<ul>") else [cell]
    result = []
    for item in items:
        if 'alt="ERROR!"' in item:
            severity = "error"
        elif 'alt="WARNING"' in item:
            severity = "warning"
        elif "information.png" in item:
            severity = "info"
        else:
            severity = "error"
        message = " ".join(htmllib.unescape(re.sub(r"<[^>]+>", "", item)).split())
        if not message:
            raise PublicationRequestError("an empty message in the row 'Publication Request'")
        result.append((severity, message))
    return result


def main():
    from_xml = errors("output/qa.xml")
    from_txt = txt_errors("output/qa.txt")
    # qa.txt repeats the errors of qa.xml; the union counts each error once.
    found = list((Counter(from_xml) | Counter(from_txt)).elements())
    pub = []
    pub_failed = False
    if os.path.exists("publication-request.json"):
        try:
            pub = [f"{PUB_LOCATION}: {m}" for s, m in publication_request("output/qa.html") if s != "info"]
        except PublicationRequestError as e:
            print(f"::error::Publication Request in output/qa.html cannot be checked: {e}")
            pub_failed = True
    else:
        print("::notice::no publication-request.json in this repository; Publication Request not checked")
    with open("output/qa.json") as f:
        expected = json.load(f)["errs"]
    if len(found) != expected:
        print(f"::error::qa.xml has {len(from_xml)} and qa.txt has {len(from_txt)} error(s), "
              f"together {len(found)}, but qa.json reports errs={expected}; "
              "the QA output layout may have changed")
        return 1
    with open("known-errors.txt") as f:
        known = [l.rstrip("\n") for l in f if l.strip() and not l.startswith("#")]
    unknown = [e for e in found if e not in known]
    unknown_pub = [e for e in pub if e not in known]
    for e in found + pub:
        print(("KNOWN   " if e in known else "UNKNOWN ") + e)
    for k in known:
        if k not in found + pub:
            print(f"::notice::known-errors.txt entry no longer occurs: {k}")
    failed = pub_failed
    if unknown:
        print(f"::error::IG build has {len(unknown)} error(s) not listed in known-errors.txt; see qa.html in the ig-output artifact")
        failed = True
    if unknown_pub:
        print(f"::error::Publication Request has {len(unknown_pub)} error(s) or warning(s) not listed in "
              "known-errors.txt (see the row 'Publication Request' in qa.html in the ig-output artifact, "
              "and publication-request.json): " + "; ".join(unknown_pub))
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

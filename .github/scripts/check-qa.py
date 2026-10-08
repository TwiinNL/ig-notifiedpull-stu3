#!/usr/bin/env python3
"""Fail on every publisher error that is not listed in known-errors.txt.

Source: output/qa.xml (a Bundle of OperationOutcomes). Each error/fatal issue becomes
one line "<location>: <message>", where location is the issue's expression (e.g.
ImplementationGuide/<id>), or else the file name. Lines are compared exactly with the
non-comment lines of known-errors.txt. The error count must equal "errs" in output/qa.json.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

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


def main():
    found = errors("output/qa.xml")
    with open("output/qa.json") as f:
        expected = json.load(f)["errs"]
    if len(found) != expected:
        print(f"::error::qa.xml has {len(found)} error(s) but qa.json reports errs={expected}; "
              "the QA output layout may have changed")
        return 1
    with open("known-errors.txt") as f:
        known = [l.rstrip("\n") for l in f if l.strip() and not l.startswith("#")]
    unknown = [e for e in found if e not in known]
    for e in found:
        print(("KNOWN   " if e in known else "UNKNOWN ") + e)
    for k in known:
        if k not in found:
            print(f"::notice::known-errors.txt entry no longer occurs: {k}")
    if unknown:
        print(f"::error::IG build has {len(unknown)} error(s) not listed in known-errors.txt; see qa.html in the ig-output artifact")
        return 1
    return 0


sys.exit(main())

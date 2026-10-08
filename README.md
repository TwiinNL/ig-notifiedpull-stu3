# ig-notifiedpull-stu3

FHIR STU3 (3.0.2) implementation guide for Notified Pull in the Twiin Afsprakenstelsel.

- Package id: `nl.twiin.fhir.stu3.notifiedpull`
- Canonical: https://fhir.twiin.nl/ig/notifiedpull-stu3
- Version: 0.1.0
- Publisher: Twiin

Built with the HL7 IG Publisher on handwritten JSON (no SUSHI).

The ImplementationGuide resource is written in R4 structure (with `fhirVersion: ["3.0.2"]`) because the publisher only reads the IG resource as R4/R5.

TODO: pin the template version in `ig.ini` (currently `fhir.base.template#current`) before the first release.

## Build

```sh
./_updatePublisher.sh   # download/update the IG Publisher
./_genonce.sh           # build; output in output/ (see output/qa.html)
```

Requires Java and Jekyll (no SUSHI: the source is handwritten JSON).

## CI

`.github/workflows/build.yml` runs on pull requests and pushes to `main`: install of Java and Jekyll, download of IG Publisher 3.0.0 (pinned), build, upload of `output/` (including `qa.html`) as artifact `ig-output`.

The build fails on every publisher error that is not listed in [known-errors.txt](known-errors.txt) (see [known-issues.md](known-issues.md)). The publisher exit code cannot be used for this: it exits with 0 on a build whose `qa.html` lists errors (see [ig-core](https://github.com/TwiinNL/ig-core)). Warnings and hints do not fail the build. Errors cannot be suppressed via `input/ignoreWarnings.txt`.

`.github/scripts/check-qa.py` reads the individual errors from `output/qa.xml`, a FHIR Bundle of OperationOutcomes written by the publisher. Chosen over the alternatives because it is structured (severity, message and expression as separate elements): `qa.txt` and `qa-eslintcompact.txt` are text for humans, and they carry absolute local paths or no location. Each error becomes one line `<location>: <message>`, with the issue's `expression` as location (file name if there is none), and must match a line in `known-errors.txt` exactly. Matching is on text and location, not on count. As a cross-check the script requires the number of errors in `qa.xml` to equal `errs` in `output/qa.json`, and fails otherwise.

Neither file's layout is documented as far as I could verify; both were inspected with IG Publisher 3.0.0, which is why the CI pins that version (`PUBLISHER_VERSION` in the workflow). On every publisher update, re-check that `qa.xml` still lists the same errors as `qa.html`. Entries in `known-errors.txt` that no longer occur are reported as a notice.

The template is not pinned: `ig.ini` uses `fhir.base.template#current`. A template change can alter the text of an error message, so an allowlisted error then no longer matches. The CI fails deliberately until `known-errors.txt` is updated (and `known-issues.md` re-checked).

## License

- IG content: CC BY-SA 4.0 (SPDX: `CC-BY-SA-4.0`), see [LICENSE](LICENSE).
- Code (scripts): TBD.
- `_updatePublisher.*` and `_genonce.*` are copied unmodified from [HL7/ig-publisher-scripts](https://github.com/HL7/ig-publisher-scripts) (main). That repository contains no license file and its README states no license (GitHub API reports `license: null`), so their license is unknown; clarify with HL7 before publishing.

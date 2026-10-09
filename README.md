# ig-notifiedpull-stu3

FHIR STU3 (3.0.2) implementation guide for Notified Pull in the Twiin Afsprakenstelsel.

- Package id: `nl.twiin.fhir.stu3.notifiedpull`
- Canonical: https://fhir.twiin.nl/ig/notifiedpull-stu3
- Version: 0.1.0
- Publisher: Twiin

Built with the HL7 IG Publisher on handwritten JSON (no SUSHI).

The ImplementationGuide resource is written in R4 structure (with `fhirVersion: ["3.0.2"]`) because the publisher only reads the IG resource as R4/R5.

## Build

```sh
./_updatePublisher.sh   # download/update the IG Publisher
./_genonce.sh           # build; output in output/ (see output/qa.html)
```

Requires Java and Jekyll (no SUSHI: the source is handwritten JSON); Node only for the test of the language redirect.

The template is pinned to `fhir2.base.template#0.1.0`. `fhir.base.template` is no longer supported and the IG Publisher will refuse IGs that depend on it, see the [FHIR security notice of 17 March 2026](https://fhir.org/guides/security-notices/2026-03-npm-dependencies.html). `fhir2.base.template` builds all pages into `output/en/`; the pages in the root of `output/` are redirect stubs. This template version has two bugs, worked around in this repository: see [known-issues.md](known-issues.md).

This IG has `jurisdiction` NL; the template does not put the flag `assets/images/nld.svg` in `output/en/`, where the pages look for it ([HL7/ig-template-base2 issue #16](https://github.com/HL7/ig-template-base2/issues/16)). `input/images/assets/images/nld.svg` is a workaround; see [known-issues.md](known-issues.md).

## CI

`.github/workflows/build.yml` runs on pull requests and pushes to `main`: install of Java, Jekyll and Node, download of IG Publisher 3.0.0 (pinned), build, upload of `output/` (including `qa.html`) as artifact `ig-output`.

The runner is pinned to `ubuntu-24.04` (not `ubuntu-latest`), so a change of the GitHub-hosted image does not alter the build unnoticed. Moving to a newer Ubuntu gets its own PR.

The build fails on every publisher error that is not listed in [known-errors.txt](known-errors.txt) (see [known-issues.md](known-issues.md)). The publisher exit code cannot be used for this: it exits with 0 on a build whose `qa.html` lists errors (see [ig-core](https://github.com/TwiinNL/ig-core)). Warnings and hints do not fail the build. Errors cannot be suppressed via `input/ignoreWarnings.txt`.

`.github/scripts/check-qa.py` reads the errors from two files. `output/qa.xml` is a FHIR Bundle of OperationOutcomes written by the publisher; it is structured (severity, message and expression as separate elements), and each error becomes one line `<location>: <message>`, with the issue's `expression` as location (file name if there is none). `output/qa.txt` also lists the errors of the HTML check (for example the WCAG heading check on the generated pages), which `qa.xml` does not contain (`qa.json` only counts them); each `ERROR:` line becomes one line `<location>: <message>`, with the absolute path of `output/` replaced by `output/`. Every line must match a line in `known-errors.txt` exactly. Matching is on text and location, not on count. As a cross-check the script requires the errors of both files, counted once when both list them, to equal `errs` in `output/qa.json`, and fails otherwise.

The step "Test language redirect" runs `node test/lang-redirects.test.js` after the build: it checks that the redirect script in `output/` is our override of the template file, that `output/en/assets/images/nld.svg` exists, and that browsers with language `nl`, `nl-NL`, `de`, `en` and `en-US` are all sent to `en/<page>`, with query string and fragment kept. The override (`input/images/assets/js/lang-redirects.js`) is a source file of the IG, so every build from this repository applies it, including the build for publication with `-go-publish`; that build has not been run for this change, so check `output/assets/js/lang-redirects.js` (and the copy in `output/en/`) before publishing. See [known-issues.md](known-issues.md).

Neither file's layout is documented as far as I could verify; both were inspected with IG Publisher 3.0.0, which is why the CI pins that version (`PUBLISHER_VERSION` in the workflow). On every publisher update, re-check that `qa.xml` and `qa.txt` together still list the same errors as `qa.html`. Entries in `known-errors.txt` that no longer occur are reported as a notice.

A template change can alter the text of an error message, so an allowlisted error then no longer matches. The CI fails deliberately until `known-errors.txt` is updated (and `known-issues.md` re-checked). That is why the template is pinned.

## License

- IG content: CC BY-SA 4.0 (SPDX: `CC-BY-SA-4.0`), see [LICENSE](LICENSE).
- Code (scripts): TBD.
- `_updatePublisher.*` and `_genonce.*` are copied unmodified from [HL7/ig-publisher-scripts](https://github.com/HL7/ig-publisher-scripts) (main). That repository contains no license file and its README states no license (GitHub API reports `license: null`), so their license is unknown; clarify with HL7 before publishing.

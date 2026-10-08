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

Requires Java and Jekyll.

## License

- IG content: CC BY-SA 4.0 (SPDX: `CC-BY-SA-4.0`), see [LICENSE](LICENSE).
- Code (scripts): TBD.
- `_updatePublisher.*` and `_genonce.*` are copied unmodified from [HL7/ig-publisher-scripts](https://github.com/HL7/ig-publisher-scripts) (main). That repository contains no license file and its README states no license (GitHub API reports `license: null`), so their license is unknown; clarify with HL7 before publishing.

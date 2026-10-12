# Known issues

Errors reported in `output/qa.html` that do not originate from this repository's files.
Nothing is suppressed: `input/ignoreWarnings.txt` contains no entries.
All 9 errors are allowlisted in [known-errors.txt](known-errors.txt) (issues 1-9), which the CI check (`.github/scripts/check-qa.py`) compares against `output/qa.xml` and `output/qa.txt`. Messages are English: `ImplementationGuide.language` is `en`, which takes precedence over the `nl_NL` the publisher would infer from `ImplementationGuide.jurisdiction=NL` (`PublisherBase.inferDefaultNarrativeLang`, tag 3.0.0). Without `language`, the messages are Dutch and the allowlist would no longer match.

Evidence applies to: IG Publisher 3.0.0 (Git# 7d1c5ae624df, built 2026-10-08), template
`twiin.base.template#0.1.1` (on `fhir2.base.template#0.1.0`, package date 20250706040134), `hl7.fhir.r3.core#3.0.2`,
`hl7.fhir.uv.tools.r3#1.3.0`, `hl7.terminology.r3#7.4.0`. Result: 9 errors, 24 warnings. Issues 1-9
were checked with `fhir.base.template#current` (package date 20260708163541: 9 errors, 16 warnings);
the text and location of these 9 errors in `qa.xml` is identical with `fhir2.base.template#0.1.0` and `twiin.base.template#0.1.1`.

## Why not suppressed

The publisher does not suppress per-file errors via `ignoreWarnings.txt`. Source
(`ValidationPresenter.filterMessages`, HL7/fhir-ig-publisher master): file messages are filtered with
`canSuppressErrors=false`; a matching error only gets a comment. Verified on the installed version:
patterns for `eld-12`, `implementationguide-dependency-comment` and `structuredefinition-fhir-type`
left the error count at 9.

## Issues

### 1. `implementationguide-dependency-comment` not allowed on `ImplementationGuide.dependency[0]`

- Origin: publisher. The source IG has no `dependsOn`. `template/onLoad-ig-working.json` has none;
  `template/onGenerate-ig-working.json` has `dependsOn[hl7tx]` with the comment "Automatically
  added as a dependency - all IGs depend on HL7 Terminology".
- The STU3-format output IG puts this extension (from tools#1.3.0) on `dependency`, where it is not allowed.

### 2-3. `structuredefinition-fhir-type` unknown on `StructureDefinition.snapshot.element[1].type[0]` (extension + its `.url`)

- Origin: snapshot generation. `Task.id` has `type: [{code: "id"}]` in `hl7.fhir.r3.core#3.0.2`; our
  generated snapshot has the same plus the extension. Our differential contains no `type`.
- The code path in the publisher library was not identified.

### 4-9. `eld-12` on `Task.statusReason`, `Task.businessStatus`, `Task.code`, `Task.reason`, `Task.input.type`, `Task.output.type`

- Origin: STU3 core data with the validator. In our snapshot the `binding` of these six elements is
  identical to `hl7.fhir.r3.core#3.0.2` `StructureDefinition-Task.json` (example strength, no `valueSet`).
  Our differential only touches `Task.owner`.
- Why `eld-12` fails on an absent `valueSet` is not verified (suspected FHIRPath evaluation of an empty collection).

## Not fixed by `twiin.base.template#0.1.1`

Applies to: `twiin.base.template#0.1.1` (based on `fhir2.base.template#0.1.0`) with IG Publisher 3.0.0. The template fixes the redirect to `en/` for non-English browsers, the empty release label, the flag `nld.svg` missing in `output/en/` ([HL7/ig-template-base2 issue #16](https://github.com/HL7/ig-template-base2/issues/16)), the doubled `<h2 id="root">` on profile history pages and the not well formed profile pages (see its [README](https://github.com/TwiinNL/ig-template)); this repository has no workarounds for those any more. What remains, the same with `fhir2.base.template#0.1.0` alone:

- `searchform.html` has its own markup that the publisher reports as not well formed: 8 warnings for `output/searchform.html` and 8 for `output/en/searchform.html` (16 in total, not allowlisted, warnings do not fail the build).
- Profile history pages are not in the page list of the publisher, so their breadcrumb bar is empty and the heading has no section number.

# Known issues

Errors reported in `output/qa.html` that do not originate from this repository's files.
Nothing is suppressed: `input/ignoreWarnings.txt` contains no entries.
All 10 errors are allowlisted in [known-errors.txt](known-errors.txt) (issues 1-9 and the template error at the end), which the CI check (`.github/scripts/check-qa.py`) compares against `output/qa.xml` and `output/qa.txt`. Messages are English: `ImplementationGuide.language` is `en`, which takes precedence over the `nl_NL` the publisher would infer from `ImplementationGuide.jurisdiction=NL` (`PublisherBase.inferDefaultNarrativeLang`, tag 3.0.0). Without `language`, the messages are Dutch and the allowlist would no longer match.

Evidence applies to: IG Publisher 3.0.0 (Git# 7d1c5ae624df, built 2026-10-08), template
`fhir2.base.template#0.1.0` (package date 20250706040134), `hl7.fhir.r3.core#3.0.2`,
`hl7.fhir.uv.tools.r3#1.3.0`, `hl7.terminology.r3#7.4.0`. Result: 10 errors, 31 warnings. Issues 1-9
were checked with `fhir.base.template#current` (package date 20260708163541: 9 errors, 16 warnings);
the text and location of these 9 errors in `qa.xml` is identical with `fhir2.base.template#0.1.0`.

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

## Template `fhir2.base.template#0.1.0`

Applies to: `fhir2.base.template#0.1.0` (the only version on packages2.fhir.org, 2026-10-09) with IG Publisher 3.0.0. The two bugs in the first and third section are fixed on the `main` branch of [HL7/ig-template-base2](https://github.com/HL7/ig-template-base2) but not in a published version; `package.json` there still says 0.1.0. The missing flag (second section) is [issue #16](https://github.com/HL7/ig-template-base2/issues/16), open on 2026-10-09 without a fix.

### Redirect stops after the first language

The template builds every page into `output/en/` and leaves a stub page in the root of `output/` that loads `assets/js/lang-redirects.js`. In 0.1.0 the `return;` in the loop of `doRedirect()` sits outside the `if`, so a browser whose language is not `en` (for example `nl`, `nl-NL`, `de`) is not redirected and stays on the empty stub page. Workaround: `input/images/assets/js/lang-redirects.js` is the file from HL7/ig-template-base2 `main`, copied verbatim (sha-256 `8a4dec2d77c9dff3a2b67f3574f0aef17f69e68812833550519c9cb2857e527d`). Source commits: [3c6dc8c9](https://github.com/HL7/ig-template-base2/commit/3c6dc8c9) ("Fix redirect for non-EN browsers", the `return` fix) and [28239381](https://github.com/HL7/ig-template-base2/commit/28239381151925bb4794b69c1c5738fdcb4b3ef6) ("Update lang-redirects.js", keeps `search` and `hash` in the redirect), checked on `main` at 2c669969 (2026-10-09). The override can go as soon as a template release after 0.1.0 contains these commits and `ig.ini` uses it: delete `input/images/assets/js/lang-redirects.js` and the "Test language redirect" step if the template's own file passes `test/lang-redirects.test.js`.

The publisher copies `input/images/` over the template's `content/`, so both `output/assets/js/lang-redirects.js` and `output/en/assets/js/lang-redirects.js` are this file. `test/lang-redirects.test.js` checks that, and runs the redirect for `nl`, `nl-NL`, `de`, `en` and `en-US`, and with a query string and a fragment (CI step "Test language redirect"). This is observed behaviour of the publisher, not documented; the test fails if it stops working. The override is a source file of the IG, so every build from this repository applies it, including the publication build (`-go-publish`). That build has not been run for this change; run `node test/lang-redirects.test.js` on its output before publishing.

The sha-256 of the faulty template file is `7ea6ae46a27c877dc47cc7ac0df4cc05f01b8debcbeec66db372da7577e92383`.

### Flag `nld.svg` missing in `output/en/`

This IG has `jurisdiction` NL. Every page shows the flag as `assets/images/nld.svg`, relative to the page, so as `output/en/assets/images/nld.svg`. The build writes the file only to `output/assets/images/nld.svg`. Without a workaround the build reports 12 broken links (`The image source 'assets/images/nld.svg' cannot be resolved`, one per page; they are listed as `ERROR:` in `qa.txt` but are not counted in `errs`). This is [HL7/ig-template-base2 issue #16](https://github.com/HL7/ig-template-base2/issues/16).

Workaround: `input/images/assets/images/nld.svg`, a file written for this repository (not copied from anywhere): an SVG with `viewBox="0 0 9 6"` and three horizontal bands of equal height, red (`#AE1C28`), white and blue (`#21468B`), the Dutch flag. It is part of the IG source and falls under the licence of the IG content (CC BY-SA 4.0, see [LICENSE](LICENSE)). The publisher copies it to `output/en/assets/images/`, where the build writes none. It does not replace the file that the build writes to `output/assets/images/nld.svg`: there the build's own file is kept (checked: different sha-256), but nothing links to that location from `en/`. With the workaround the build has 0 broken links. `test/lang-redirects.test.js` checks that `output/en/assets/images/nld.svg` equals the source file (not the one the build writes), so it shows when this stops working.

Remove `input/images/assets/images/nld.svg` and the flag check in `test/lang-redirects.test.js` when a template version that puts the flag in `output/en/` is used: the build then has 0 broken links without the file.


### Release label not shown in the page header

Without a workaround the header shows `<version> - ` without the `releaselabel` parameter in `input/ImplementationGuide-nl.twiin.fhir.stu3.notifiedpull.json`. Cause: `includes/fragment-pagebegin.html:64` of the template reads `site.data.info.releaselabellang[include.lang]` (`include.lang` is `en` there), but `_data/info.json`, written by `scripts/onGenerate.genJson.xslt:71-83`, only has `releaselabel`. The script writes a fixed list of keys, so no IG parameter can supply `releaselabellang`. Fixed upstream in [HL7/ig-template-base2 6fc5321](https://github.com/HL7/ig-template-base2/commit/6fc5321) (2025-11-20, reads `site.data.fhir.releaseLabellang`), not in a published version.

Workaround: `input/includes/fragment-pagebegin.html` is the template file of 0.1.0 (sha-256 `431379c0d2dabaa855c2d57f051b08e9f0d00cb23bdf70447845bf63170996f9`), copied verbatim with only line 64 changed to `{% assign status = site.data.info.releaselabel %}`. The publisher puts `input/includes/` over the template's includes.

The CI step "Test release label" (`test/release-label.test.js`) checks that every page in `output/en/` with the template header (`<div id="ig-status">`) shows the label, and fails if `template/includes/fragment-pagebegin.html` is no longer the 0.1.0 file: then the override must be reviewed, because it would replace a newer template file. `searchform.html` has its own header from the template and never shows the label; it is not checked.

Remove the override and the CI step when `ig.ini` points to a template version that contains 6fc5321 and the label appears without the override.

### Two `<h2 id="root">` on the profile history page

Applies to: `StructureDefinition-notifiedpull-task.profile.history.html`. The template's `layouts/layout-profile-history.html` has two `<h2 id="root">` lines in a row, and the second is not closed (fixed on `main` in [5b8c9667](https://github.com/HL7/ig-template-base2/commit/5b8c9667)). The publisher's WCAG check reports it as an error, listed in `qa.txt` and `qa.json` but not in `qa.xml`. Allowlisted in [known-errors.txt](known-errors.txt) (location `output/en/StructureDefinition-notifiedpull-task.profile.history.html`, message `The page has more than one top level heading: <h2> (no text) … (WCAG compliance test)`). Remove the line when the template is fixed. A new profile adds a line.

The same template files give 15 warnings that are not allowlisted: `The html source is not well formed` (14 messages: 8 on `searchform.html`, 1 on the profile page, 5 on its history page) and `duplicate element ids: root` (1, history page).

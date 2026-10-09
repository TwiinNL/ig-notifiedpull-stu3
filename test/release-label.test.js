#!/usr/bin/env node
// Checks that the release label is shown in the header of the IG pages, and that the template file
// the override in input/includes/ is based on has not changed. After a build, run from the repo root:
//   node test/release-label.test.js
// See known-issues.md, "Release label not shown in the page header".
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const LABEL = "normative only when referenced by the Twiin afsprakenstelsel";
const OVERRIDE = "input/includes/fragment-pagebegin.html";
const TEMPLATE_ORIGINAL = "template/includes/fragment-pagebegin.html";
// SHA-256 of the file in fhir2.base.template#0.1.0, the version the override is copied from.
const TEMPLATE_ORIGINAL_SHA256 = "431379c0d2dabaa855c2d57f051b08e9f0d00cb23bdf70447845bf63170996f9";
const PAGES = "output/en";

const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
let failed = false;
const fail = (msg) => { console.log(`::error::${msg}`); failed = true; };

if (!fs.existsSync(TEMPLATE_ORIGINAL)) {
  fail(`${TEMPLATE_ORIGINAL} is missing; run the build first`);
} else if (sha256(TEMPLATE_ORIGINAL) !== TEMPLATE_ORIGINAL_SHA256) {
  fail(`${TEMPLATE_ORIGINAL} differs from the fhir2.base.template#0.1.0 version: review ${OVERRIDE} (copy it again or remove it)`);
}

let checked = 0;
for (const name of fs.readdirSync(PAGES).filter((f) => f.endsWith(".html")).sort()) {
  const html = fs.readFileSync(path.join(PAGES, name), "utf8");
  // Header from fragment-pagebegin.html; searchform.html and the qa pages have their own header.
  const status = html.match(/<div id="ig-status">[\s\S]*?<\/div>/);
  if (!status) continue;
  checked++;
  if (!status[0].includes(LABEL)) fail(`${PAGES}/${name}: release label not in the page header`);
}
if (checked === 0) fail(`no pages with a header found in ${PAGES}`);
console.log(`${checked} pages checked`);
process.exit(failed ? 1 : 0);

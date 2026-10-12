#!/usr/bin/env node
// Checks that the release label is shown in the header of the IG pages. The header comes from
// twiin.base.template; whether its file is the right one is checked in the template repository,
// here only what the build delivers. After a build, run from the repo root:
//   node test/release-label.test.js
const fs = require("fs");
const path = require("path");

const LABEL = "normative only when referenced by the Twiin afsprakenstelsel"; // parameter releaselabel in the IG JSON
const PAGES = "output/en";

let failed = false;
const fail = (msg) => { console.log(`::error::${msg}`); failed = true; };

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

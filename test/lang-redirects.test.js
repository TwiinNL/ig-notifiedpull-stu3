#!/usr/bin/env node
// Checks the language redirect of the published stub pages: every browser language ends up on
// en/<page>, and query string and fragment are kept. After a build, run from the repo root:
//   node test/lang-redirects.test.js
// The script comes from twiin.base.template; whether it is the right file is checked in the
// template repository, here only what the build delivers.
const fs = require("fs");

const OUTPUT_COPIES = ["output/assets/js/lang-redirects.js", "output/en/assets/js/lang-redirects.js"];

let failed = false;
const fail = (msg) => { console.log(`::error::${msg}`); failed = true; };

// Only in this repository: the IG has jurisdiction NL; every page in output/en/ looks for the flag
// assets/images/nld.svg there. The template delivers it; the test checks that the build has it.
for (const flag of ["output/assets/images/nld.svg", "output/en/assets/images/nld.svg"]) {
  if (!fs.existsSync(flag)) fail(`${flag} is missing`);
}

for (const copy of OUTPUT_COPIES) {
  if (!fs.existsSync(copy)) { fail(`${copy} is missing`); continue; }
  const src = fs.readFileSync(copy, "utf8");
  // [language, pathname, search, hash, expected]
  const cases = [
    ["nl", "/ig/notifications/index.html", "", "", "en/index.html"],
    ["nl-NL", "/ig/notifications/artifacts.html", "", "", "en/artifacts.html"],
    ["de", "/ig/notifications/index.html", "", "", "en/index.html"],
    ["en", "/ig/notifications/StructureDefinition-twiin-subscription.html", "", "", "en/StructureDefinition-twiin-subscription.html"],
    ["en-US", "/ig/notifications/index.html", "", "", "en/index.html"],
    ["nl", "/ig/notifications/index.html", "?a=1&b=2", "#section", "en/index.html?a=1&b=2#section"],
    ["en-US", "/ig/notifications/artifacts.html", "", "#table", "en/artifacts.html#table"],
    ["de", "/ig/notifications/artifacts.html", "?q=x", "", "en/artifacts.html?q=x"],
  ];
  for (const [language, pathname, search, hash, expected] of cases) {
    const targets = [];
    const window = { location: { pathname, search, hash, replace: (url) => targets.push(url) } };
    new Function("langs", "navigator", "window", src)(["en"], { language }, window);
    const ok = targets.length === 1 && targets[0] === expected;
    console.log(`${ok ? "ok  " : "FAIL"} ${copy} ${language} ${pathname}${search}${hash} -> ${targets.join(", ") || "(no redirect)"}`);
    if (!ok) failed = true;
  }
}
process.exit(failed ? 1 : 0);

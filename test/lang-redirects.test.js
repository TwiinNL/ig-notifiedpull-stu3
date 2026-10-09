#!/usr/bin/env node
// Checks the language redirect of the published stub pages: every browser language ends up on
// en/<page>, and query string and fragment are kept. After a build, run from the repo root:
//   node test/lang-redirects.test.js
// See known-issues.md, "Template 0.1.0 redirect stops after the first language".
const fs = require("fs");
const crypto = require("crypto");

const OVERRIDE = "input/images/assets/js/lang-redirects.js";
const OUTPUT_COPIES = ["output/assets/js/lang-redirects.js", "output/en/assets/js/lang-redirects.js"];
const TEMPLATE_ORIGINAL = "template/content/assets/js/lang-redirects.js";
// SHA-256 of the file in fhir2.base.template#0.1.0, the known faulty version.
const TEMPLATE_ORIGINAL_SHA256 = "7ea6ae46a27c877dc47cc7ac0df4cc05f01b8debcbeec66db372da7577e92383";

const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
let failed = false;
const fail = (msg) => { console.log(`::error::${msg}`); failed = true; };

if (fs.existsSync(TEMPLATE_ORIGINAL) && sha256(TEMPLATE_ORIGINAL) !== TEMPLATE_ORIGINAL_SHA256) {
  console.log(`::notice::${TEMPLATE_ORIGINAL} differs from the 0.1.0 version; check whether ${OVERRIDE} is still needed`);
}

// Only in this repository: the IG has jurisdiction NL, and the template does not put the flag
// assets/images/nld.svg in output/en/, where every page looks for it.
const FLAG = "input/images/assets/images/nld.svg";
for (const copy of ["output/assets/images/nld.svg", "output/en/assets/images/nld.svg"]) {
  if (!fs.existsSync(copy)) fail(`${copy} is missing`);
  else if (sha256(copy) !== sha256(FLAG)) fail(`${copy} is not ${FLAG}`);
}

for (const copy of OUTPUT_COPIES) {
  if (!fs.existsSync(copy)) { fail(`${copy} is missing`); continue; }
  if (sha256(copy) !== sha256(OVERRIDE)) {
    fail(`${copy} is not ${OVERRIDE}: the override of the template file did not take effect`);
    continue;
  }
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

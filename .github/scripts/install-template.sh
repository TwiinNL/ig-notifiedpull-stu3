#!/usr/bin/env bash
# Installs twiin.base.template, the template named in ig.ini, into the FHIR package cache,
# where the publisher looks for it. The template is not on the FHIR package registry; it is the
# .tgz asset of a release of TwiinNL/ig-template. Always installs from a fresh download: checks
# the pinned sha-256 (fails on a mismatch) and replaces whatever is in the package cache (also a
# restored cache entry). Run before the build, in CI and locally. See README.md.
set -euo pipefail

cache="${FHIR_PACKAGE_CACHE:-$HOME/.fhir/packages}"
name=twiin.base.template
version=0.1.1
sha=e95e60fa5b463cadd4ef34ad4b6c0dcee32fa05d02bfd649b4ff90960d22b123
url="https://github.com/TwiinNL/ig-template/releases/download/v$version/$name-$version.tgz"

# ig.ini decides which template a build uses; this script must install that one.
if ! grep -qxF "template = $name#$version" "$(dirname "$0")/../../ig.ini"; then
  echo "::error::ig.ini does not say 'template = $name#$version'; update this script and ig.ini together" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -sSfL -o "$tmp/template.tgz" "$url"
actual="$(shasum -a 256 "$tmp/template.tgz" | cut -d' ' -f1)"
if [ "$actual" != "$sha" ]; then
  echo "::error::$name#$version: sha-256 $actual, expected $sha ($url)" >&2
  exit 1
fi

dir="$cache/$name#$version"
rm -rf "$dir"
mkdir -p "$dir"
tar xzf "$tmp/template.tgz" -C "$dir"
echo "Installed $name#$version (sha-256 $sha)"

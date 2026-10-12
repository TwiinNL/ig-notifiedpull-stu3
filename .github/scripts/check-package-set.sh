#!/usr/bin/env bash
# Fails when the packages in the local FHIR package cache (~/.fhir/packages) after a build
# differ from .github/fhir-packages.lock, in either direction. The lock file is part of the
# cache key, so a restored cache holds exactly the locked set; this check makes a build with
# a cache and a build without one fail on the same drift (a floating dependency such as
# "latest" that moved, a changed dependency, a new transitive package) instead of the cache
# hiding it. After an intended change: replace the lock file with the list printed below.
set -euo pipefail

cache="${FHIR_PACKAGE_CACHE:-$HOME/.fhir/packages}"
lock="$(cd "$(dirname "$0")/.." && pwd)/fhir-packages.lock"
now="$(mktemp)"
trap 'rm -f "$now"' EXIT

# The publisher installs the IG's own build as <packageId>#dev. That is build output, not a
# dependency: remove it so that it is never saved to the cache or restored from it.
find "$cache" -mindepth 1 -maxdepth 1 -type d -name '*#dev' -exec rm -rf {} +

find "$cache" -mindepth 1 -maxdepth 1 -type d -name '*#*' -exec basename {} \; | LC_ALL=C sort > "$now"
echo "Packages in $cache:"
cat "$now"

if ! diff -u "$lock" "$now"; then
  echo "::error::Package set differs from .github/fhir-packages.lock (see the diff above)"
  exit 1
fi
echo "Package set matches .github/fhir-packages.lock"

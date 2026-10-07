#!/usr/bin/env python3
"""Repack a directory into a valid .pcio archive.

Usage:
    python3 pcio_pack.py <dir> <out.pcio>

Writes a ZIP with STORE (no compression), root-level metadata files first, then
userassets/, matching what playingcards.io produces. Validates that the required
files are present and that widgets.json parses.

Stdlib only.
"""
import argparse
import json
import os
import sys
import zipfile

REQUIRED = ["schemaVersion", "widgets.json"]


def main():
    ap = argparse.ArgumentParser(description="Repack a directory into a .pcio.")
    ap.add_argument("src_dir", help="directory produced by pcio_unpack.py")
    ap.add_argument("out", help="output .pcio path")
    args = ap.parse_args()

    for req in REQUIRED:
        if not os.path.exists(os.path.join(args.src_dir, req)):
            sys.exit("Missing required file: %s" % req)

    # Validate widgets.json parses before packing.
    with open(os.path.join(args.src_dir, "widgets.json"), encoding="utf-8") as f:
        widgets = json.load(f)
    if not isinstance(widgets, list):
        sys.exit("widgets.json is not a JSON array")

    # Collect members; root files before userassets/ (order is cosmetic).
    members = []
    for root, _, files in os.walk(args.src_dir):
        for fn in files:
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, args.src_dir)
            members.append((full, arc))
    members.sort(key=lambda t: (t[1].startswith("userassets/"), t[1]))

    with zipfile.ZipFile(args.out, "w", compression=zipfile.ZIP_STORED) as z:
        for full, arc in members:
            z.write(full, arc)

    # Validate the result.
    with zipfile.ZipFile(args.out) as z:
        if z.testzip() is not None:
            sys.exit("Repacked archive failed integrity check")
        _ = json.loads(z.read("widgets.json"))

    print("Packed %s -> %s" % (args.src_dir, args.out))
    print("  size: %d bytes, entries: %d, widgets: %d"
          % (os.path.getsize(args.out), len(members), len(widgets)))


if __name__ == "__main__":
    main()

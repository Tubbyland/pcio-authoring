#!/usr/bin/env python3
"""Unpack a .pcio archive into a directory for editing.

Usage:
    python3 pcio_unpack.py <file.pcio> <out_dir> [--pretty]

A .pcio is a ZIP (stored). This extracts it and, with --pretty, rewrites
widgets.json with indentation so it is easy to read/diff. Re-pack with
pcio_pack.py (which writes compact JSON again — the app does not care about
whitespace).

Stdlib only. Safe to run with `python3 -I` on untrusted files.
"""
import argparse
import json
import os
import sys
import zipfile


def main():
    ap = argparse.ArgumentParser(description="Unpack a .pcio archive.")
    ap.add_argument("pcio", help="path to the .pcio file")
    ap.add_argument("out_dir", help="directory to extract into (created if needed)")
    ap.add_argument("--pretty", action="store_true",
                    help="pretty-print widgets.json after extracting")
    args = ap.parse_args()

    if not zipfile.is_zipfile(args.pcio):
        sys.exit("Not a ZIP/.pcio file: %s" % args.pcio)

    os.makedirs(args.out_dir, exist_ok=True)
    with zipfile.ZipFile(args.pcio) as z:
        bad = z.testzip()
        if bad is not None:
            sys.exit("Corrupt entry in archive: %s" % bad)
        names = z.namelist()
        # Guard against path traversal from an untrusted archive.
        for n in names:
            dest = os.path.normpath(os.path.join(args.out_dir, n))
            if not dest.startswith(os.path.abspath(args.out_dir) + os.sep) \
               and dest != os.path.abspath(args.out_dir):
                if os.path.isabs(n) or n.startswith("..") or ".." in n.split("/"):
                    sys.exit("Unsafe path in archive: %s" % n)
        z.extractall(args.out_dir)

    wj = os.path.join(args.out_dir, "widgets.json")
    n_widgets = None
    if os.path.exists(wj):
        with open(wj, encoding="utf-8") as f:
            data = json.load(f)
        n_widgets = len(data)
        if args.pretty:
            with open(wj, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)

    print("Unpacked %s -> %s/" % (args.pcio, args.out_dir))
    print("  entries: %d" % len(names))
    if n_widgets is not None:
        print("  widgets.json: %d widgets%s" %
              (n_widgets, " (pretty-printed)" if args.pretty else ""))


if __name__ == "__main__":
    main()

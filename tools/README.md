# Tools

Stdlib-only Python 3 scripts. No dependencies.

## Unpack
```bash
python3 pcio_unpack.py table.pcio work/ --pretty
```
Extracts the archive into `work/` and (with `--pretty`) indents `widgets.json`
for reading/diffing. Includes a path-traversal guard for untrusted files.

## Pack
```bash
python3 pcio_pack.py work/ table-v2.pcio
```
Re-zips `work/` into a valid `.pcio` (STORE compression, correct structure),
after checking the required files exist and `widgets.json` parses.

## Typical loop
```bash
python3 pcio_unpack.py table.pcio work/ --pretty
#   ...edit work/widgets.json (by hand, or with a small script)...
python3 pcio_pack.py work/ table-v2.pcio
#   import table-v2.pcio into a NEW room at https://playingcards.io/import
```

## Editing by script
`widgets.json` is a flat list of dicts. Load it, index by `id`
(`byid = {w["id"]: w for w in data}`), mutate, and dump compact
(`json.dump(data, f, ensure_ascii=False, separators=(",", ":"))`). See
`../examples/you-cheated/MAPPING.md` for concrete edits.

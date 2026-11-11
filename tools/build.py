#!/usr/bin/env python3 -I
"""Build registry/devices.json - the ONE file netplex downloads ("Update device list") and ships
inside each release. Run tools/validate.py first; this refuses to build from a tree that fails it.

  python3 tools/build.py            write registry/devices.json
  python3 tools/build.py --check    exit 1 if the committed file is stale (run before merging)

Layout of the output (schema 2): `devices` = every key -> its settings (an alias carries a copy
of its target's settings), `meta` = key -> {source, alias_of?, group?}. The per-field reason notes stay
in the device files (they are for people, not for the box).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate  # noqa: E402

ROOT = validate.ROOT
OUT = os.path.join(ROOT, "registry", "devices.json")
NOTES = os.path.join(ROOT, "registry", "notes.json")


def build(docs):
    devices, meta = {}, {}
    for key in sorted(docs):
        d = docs[key]
        tgt = docs[d["alias_of"]] if "alias_of" in d else d
        devices[key] = tgt["settings"]
        meta[key] = {"source": d["source"], **({"alias_of": d["alias_of"]} if "alias_of" in d else {}),
                     **({"group": d["group"]} if "group" in d else {})}
    return {"schema": 2, "devices": devices, "meta": meta}


def build_notes(docs):
    """key -> {tested, reasons}: the written evidence (rule #59 reasons) for people and for the
    platform's own drift test; kept out of devices.json so the downloaded list stays small."""
    return {k: {"tested": d.get("tested") or "", "reasons": d.get("reasons") or {}}
            for k, d in sorted(docs.items()) if "alias_of" not in d and (d.get("tested") or d.get("reasons"))}


def main():
    probs, docs = validate.check_tree()
    if probs:
        print("\n".join(probs))
        print("build refused: fix the problems above")
        return 1
    text = json.dumps(build(docs), indent=0, sort_keys=True, separators=(",", ":")) + "\n"
    notes = json.dumps(build_notes(docs), indent=0, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        cur = open(OUT).read() if os.path.exists(OUT) else ""
        curn = open(NOTES, encoding="utf-8").read() if os.path.exists(NOTES) else ""
        if cur != text or curn != notes:
            print("STALE: registry/devices.json or notes.json - run python3 tools/build.py and commit them")
            return 1
        print("registry/devices.json up to date")
        return 0
    open(OUT, "w").write(text)
    open(NOTES, "w", encoding="utf-8").write(notes)
    print("wrote", OUT, len(docs), "devices", len(text), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

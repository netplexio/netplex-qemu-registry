#!/usr/bin/env python3 -I
"""Validate the device database. Maintainers run this LOCALLY before merging a pull request
(no CI runs on push/PR by design).   python3 tools/validate.py [--quiet]

Checks: file name = key, folder = vendor, `source` allowed, every setting is a known field with a
value from the closed lists in schema/vocab.json (or a strict range/pattern), no free-text QEMU
arguments, no unknown fields, no binaries/links to images, aliases point at a real device.
Exit 0 = clean, 1 = problems (each printed as `path: reason`).
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
MACHINE_RE = re.compile(r"^(pc|q35)(-[A-Za-z0-9._]{1,40})?$")
CPU_RE = re.compile(r"^[A-Za-z0-9_+,=.-]{1,200}$")
DISK_FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SOURCES = ("netplex-tested", "community")
GROUPS = ("tool-node", "windows", "vrnetlab")  # which family of runtime a netplex-tested device belongs to
NEVER = ("qemu_extra_args",)
URL_LIKE = re.compile(r"(https?://|ftp://|magnet:|\.(qcow2|vmdk|iso|ova|img|tar|zip)\b)", re.I)
TEXT_FIELDS = ("vendor", "role", "image", "description", "notes", "min_enforcement_msg",
               "config_console_reason", "category")


def rng(lo, hi):
    return lambda v: isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def text(v, n=1000):
    return isinstance(v, str) and len(v) <= n and v.isprintable()


def checkers(voc):
    def enum(f, none=False):
        return lambda v: (none and v is None) or v in voc[f]
    c = {
        "emulator": enum("emulator"), "console": enum("console"), "nic": enum("nic", True),
        "disk_bus": enum("disk_bus", True),
        "machine": lambda v: isinstance(v, str) and (v in voc["machine"] or bool(MACHINE_RE.match(v))),
        "qemu_arch": enum("qemu_arch"), "qemu_version_default": enum("qemu_version"),
        "qemu_version_compatible": lambda v: isinstance(v, list) and all(x in voc["qemu_version"] for x in v),
        "node_class": enum("node_class"), "config_dialect": enum("config_dialect"),
        "day0_channel": enum("day0_channel"), "platform": enum("platform"),
        "microvm_engine": enum("microvm_engine"), "firmware": enum("firmware"),
        "boot_order": lambda v: isinstance(v, list) and all(x in voc["boot_order"] for x in v),
        "cpu_model": lambda v: isinstance(v, str) and bool(CPU_RE.match(v)),
        "console_init": lambda v: isinstance(v, str) and len(v) <= 16,
        "config_console": lambda v: v in ("none",), "kvm": lambda v: isinstance(v, bool),
        "console_port_mode": lambda v: v in ("normal", "none", "spare"), "console_spare_ports": rng(1, 3),
        "video": enum("video"), "tpm": enum("tpm"), "usb": enum("usb"), "serial_type": enum("serial_type"),
        "accel": enum("accel"), "disk_gb": enum("disk_gb"),
        "virtio_extras": lambda v: isinstance(v, bool), "min_enforcement": lambda v: isinstance(v, bool),
        "min_ram_mb": rng(16, 1048576), "default_ram_mb": rng(64, 1048576),
        "recommended_ram_mb": rng(64, 1048576), "max_ram_mb": rng(64, 1048576),
        "cpu": rng(1, 64), "max_cpu": rng(1, 64), "interfaces": rng(0, 64), "boot_timeout_sec": rng(1, 3600),
        "cpu_quota_period_us": rng(1000, 1000000),
        "cpu_quota_burst": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v <= 100,
        "reserved_interfaces": lambda v: isinstance(v, list) and len(v) <= 64 and all(
            isinstance(x, dict) and all(isinstance(a, str) and len(a) <= 40 and isinstance(b, str)
                                        and len(b) <= 80 and b.isprintable() for a, b in x.items()) for x in v),
        "extra_disks": lambda v: isinstance(v, list) and len(v) <= 8 and all(
            (isinstance(x, str) and DISK_FILE_RE.match(x)) or
            (isinstance(x, dict) and set(x) <= {"name", "device", "bus", "readonly"}
             and isinstance(x.get("name"), str) and DISK_FILE_RE.match(x["name"])
             and x.get("device", "disk") in ("disk", "cdrom") and x.get("bus", "virtio") in voc["disk_bus"]
             and isinstance(x.get("readonly", False), bool)) for x in v),
    }
    for f in TEXT_FIELDS:
        c[f] = text
    return c


def slug(v):
    return re.sub(r"[^a-z0-9._-]+", "-", (v or "other").lower()).strip("-") or "other"


def check_tree(root=ROOT):
    """-> (problems, docs); docs = {key: parsed file}."""
    problems, docs = [], {}
    meta = json.load(open(os.path.join(root, "schema", "vocab.json")))
    voc, known = meta["vocab"], set(meta["fields"])
    chk = checkers(voc)
    base = os.path.join(root, "devices")
    for vendor in sorted(os.listdir(base)):
        vdir = os.path.join(base, vendor)
        if not os.path.isdir(vdir):
            problems.append(f"devices/{vendor}: only vendor folders belong here")
            continue
        for fn in sorted(os.listdir(vdir)):
            rel = f"devices/{vendor}/{fn}"
            if not fn.endswith(".json"):
                problems.append(f"{rel}: only .json device files are accepted (no binaries, no images)")
                continue
            try:
                doc = json.load(open(os.path.join(vdir, fn), encoding="utf-8"))
            except ValueError as e:
                problems.append(f"{rel}: not valid JSON ({e})")
                continue
            key = fn[:-5]
            if not isinstance(doc, dict) or doc.get("key") != key or not KEY_RE.match(key):
                problems.append(f"{rel}: `key` must equal the file name ({key}) and be lowercase a-z 0-9 . _ -")
                continue
            if key in docs:
                problems.append(f"{rel}: duplicate key {key}")
            docs[key] = doc
            extra = set(doc) - {"key", "source", "tested", "reasons", "settings", "alias_of", "group"}
            if extra:
                problems.append(f"{rel}: unknown top-level field(s) {sorted(extra)}")
            if doc.get("source") not in SOURCES:
                problems.append(f"{rel}: source must be one of {SOURCES}")
            if doc.get("group") is not None and doc["group"] not in GROUPS:
                problems.append(f"{rel}: group must be one of {GROUPS}")
            if "alias_of" in doc:
                if "settings" in doc:
                    problems.append(f"{rel}: an alias has no settings of its own")
                continue
            st = doc.get("settings")
            if not isinstance(st, dict) or not st:
                problems.append(f"{rel}: settings missing")
                continue
            if slug(st.get("vendor")) != vendor:
                problems.append(f"{rel}: folder must be the vendor ({slug(st.get('vendor'))})")
            for f, v in st.items():
                if f in NEVER:
                    problems.append(f"{rel}: {f} (free-text launch arguments) is never accepted")
                elif f not in known:
                    problems.append(f"{rel}: unknown setting {f}")
                elif not chk[f](v):
                    problems.append(f"{rel}: bad value for {f}: {str(v)[:60]!r}")
            lo, de, hi = st.get("min_ram_mb"), st.get("default_ram_mb"), st.get("max_ram_mb")
            if (lo and de and lo > de) or (de and hi and de > hi):
                problems.append(f"{rel}: ram min/default/max out of order")
            for f in (doc.get("reasons") or {}):
                if f not in st:
                    problems.append(f"{rel}: reason for a field the device does not set ({f})")
            if doc.get("source") == "community" and URL_LIKE.search(
                    json.dumps(doc.get("reasons") or {}) + str(doc.get("tested") or "")):
                problems.append(f"{rel}: no download links or image file names in notes")
    for key, doc in docs.items():
        t = doc.get("alias_of")
        if t is not None and (t not in docs or "alias_of" in docs[t]):
            problems.append(f"devices/*/{key}.json: alias_of {t!r} must be a real, non-alias device")
    return problems, docs


if __name__ == "__main__":
    probs, docs = check_tree()
    for p in probs:
        print(p)
    if not probs and "--quiet" not in sys.argv:
        print(f"OK - {len(docs)} devices")
    sys.exit(1 if probs else 0)

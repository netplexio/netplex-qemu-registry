# netplex device settings database

**The one public, netplex-approved list of default settings for network and appliance devices — QEMU and every other runtime — so any image you add to [netplex](https://netplex.io) starts with settings that are known to work.**

It holds **498 devices** (150 with written evidence): `devices/<vendor>/<device>.json`, one file per device. Every runtime is covered: `qemu`, `iol`, `dynamips`, `docker`, `lxc`, `microvm`, `namespace` and vrnetlab-wrapped appliances.

> Every value is a **default, not a lock.** The user can override any setting per node in netplex.

## Who decides what is in it

Anyone can **propose** a change (fork, edit one file, open a pull request — see [CONTRIBUTING.md](CONTRIBUTING.md)). Only **members of the netplexio organisation can merge**, so only netplex-approved content ever reaches users. The approved database is the **single source of truth**: netplex's own tested settings live here too, not in the product's code.

| `source` | Meaning |
|---|---|
| `netplex-tested` | netplex's own profile, reasoned against the vendor's documentation or EVE-NG, with the written evidence (`tested`, `reasons`) beside the field that deviates |
| `community` | accepted from a pull request; a good default, not necessarily boot-verified |

## How netplex uses it

1. **Every netplex release carries a snapshot** of this database (built from one pinned commit with `make device-db-sync`). It works forever, offline and air-gapped; nothing is fetched at start-up.
2. **"Update device list"** (Library → device bar, off by default; optional weekly) downloads [`registry/devices.json`](registry/devices.json) from this repo, checks every field against closed lists and **applies it on top of the snapshot — the approved database wins**, for new devices and for changed ones. A file with one bad value is refused as a whole. Offline = one calm line, the snapshot keeps working.
3. Free-text launch arguments (`qemu_extra_args`) are **never** accepted from this database.

## Layout

```
devices/<vendor>/<key>.json   one device (or an alias of one)
schema/vocab.json             the closed lists the values must come from
tools/validate.py             check the whole tree (run it before every merge)
tools/build.py                build registry/devices.json + registry/notes.json
registry/devices.json         the file netplex downloads (generated - do not edit)
registry/notes.json           the written evidence per device (generated)
ALIASES.md                    why some image names share one entry
SCHEMA.md                     field reference
```

## Credits

The community part of the original list was built from the public work of **[GNS3](https://gns3.com/)** and its **[appliance registry](https://github.com/GNS3/gns3-registry)** (GPL). Thank you.

## Honesty note

Only the `netplex-tested` entries carry evidence; a `community` default may be imperfect for a specific build. If one is wrong for your image, that is exactly the pull request we want.

## License

**[GPL v3](LICENSE)**.

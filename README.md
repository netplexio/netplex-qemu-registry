# netplex QEMU Device Registry

**Community-maintained default launch parameters for network & appliance QEMU images — so any image you drop into [netplex](https://netplex.io) boots with sensible defaults out of the box.**

This registry maps a device name to its QEMU **defaults** — console type, machine type, NIC model, vCPU, RAM, arch — in one simple JSON file: [`registry/qemu-defaults.json`](registry/qemu-defaults.json). It currently ships **343 devices**.

> Every value here is a **default, not a lock.** netplex applies these when you add a matching image, and you can override any parameter per node. Curated, hand-verified profiles inside netplex always take precedence over this registry.

## 🤝 Help us make this the most collaborative networking-image registry in the world

**Got an image we don't cover yet, or a default that's wrong?** Two ways to help — both very welcome:

1. **Just tell us.** Open an [issue](../../issues/new) with the image name and, if you know them, its console/NIC/machine/RAM. We'll add it.
2. **Send a PR (best!).** Fork this repo → edit `registry/qemu-defaults.json` → open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md). One new key = one merged PR = one more device that "just works" for everyone.

No contribution is too small. A single corrected NIC model or a one-line new device helps every netplex user who adds that image next.

## 📄 Format

Each entry is keyed by a normalized device slug:

```json
"fortigate": {
  "console": "telnet",
  "machine": "pc",
  "nic_model": "virtio-net-pci",
  "cpu": 1,
  "ram_mb": 1024,
  "interfaces": 10,
  "arch": "x86_64",
  "vendor": "fortinet",
  "category": "firewall"
}
```

Full field reference: [SCHEMA.md](SCHEMA.md).

## 🙏 Credits & thanks

netplex stands on the shoulders of the open networking-emulation community. This registry's
initial device set was built from the outstanding public work of:

- **[GNS3](https://gns3.com/)** and the **[GNS3 appliance registry](https://github.com/GNS3/gns3-registry)** — for their open, GPL-licensed appliance definitions.

Thank you to the GNS3 project and its community for the immense effort behind cataloguing how
these images boot. This registry is netplex's own, independently-formatted data, released under
the same license, and we hope it gives back to the same community.


## ✅ Honesty note

These are community-contributed **defaults**. Only a subset have been live-boot-verified with a real image on real hardware — a default may be imperfect for a specific build. If one's wrong for your image, that's exactly the kind of PR we'd love. Overrides always let you fix it locally in the meantime.

## License

Released under **[GPL v3](LICENSE)** — the same copyleft license as the community sources this
draws on, so contributions and forks stay free and open for everyone. Fork it, improve it, ship
it; keep it GPL and pass the freedom on.

## A note on the data

This is a **blended, independently-reformatted** dataset of *factual* QEMU launch parameters
(console type, machine type, NIC model, vCPU, RAM) — the kind of "how does this image boot"
facts that aren't anyone's private property. It's built from the public GNS3 appliance registry into netplex's own schema and normalized, then grown by our own testing and by your
contributions. Where a value has been confirmed by actually booting the image, all the better;
where it hasn't, it's a community best-guess you can improve.

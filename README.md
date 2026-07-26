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

netplex stands on the shoulders of the open networking-emulation community. The initial seed of default parameters was informed by the outstanding, hard-won device knowledge published by:

- **[EVE-NG](https://www.eve-ng.net/)** — for their extensive vendor device templates.
- **[GNS3](https://gns3.com/)** and the **[GNS3 appliance registry](https://github.com/GNS3/gns3-registry)** — for their public appliance definitions.

Thank you to both projects and their communities for the immense effort that goes into cataloguing how these images boot. This registry is netplex's own, independently-formatted data, and we hope it gives back to the same community.

## ✅ Honesty note

These are community-contributed **defaults**. Only a subset have been live-boot-verified with a real image on real hardware — a default may be imperfect for a specific build. If one's wrong for your image, that's exactly the kind of PR we'd love. Overrides always let you fix it locally in the meantime.

## License

The data in this repository is released under [CC0-1.0](LICENSE) (public domain dedication) — use it, fork it, ship it, anywhere, no attribution required. We *ask* for contributions back, but never require it.

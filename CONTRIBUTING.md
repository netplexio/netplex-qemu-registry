# Contributing

Thank you for helping grow the netplex QEMU registry! 🎉

## Add or fix a device (PR)

1. **Fork** this repo and create a branch.
2. Edit **`registry/qemu-defaults.json`**. Add (or correct) one entry, keyed by a lowercase, dash-separated device slug (e.g. `cisco-asav`, `fortigate`, `mikrotik-chr`):
   ```json
   "your-device": {
     "console": "telnet",        // "telnet" | "vnc" | "rdp"  (VGA-only guests need "vnc")
     "machine": "pc",            // qemu -machine type (e.g. "pc", "pc-1.0", "q35"); optional
     "nic_model": "virtio-net-pci", // e1000 | virtio-net-pci | vmxnet3 | e1000-82545em ...
     "cpu": 1,                   // default vCPUs
     "ram_mb": 1024,             // default RAM in MB
     "interfaces": 4,            // default NIC count; optional
     "arch": "x86_64",           // optional (default x86_64)
     "vendor": "your-vendor",    // lowercase vendor slug; optional
     "category": "router"        // router | switch | firewall | guest | ...; optional
   }
   ```
3. Keep the file **valid JSON**, keys **sorted** (`python -m json.tool --sort-keys` helps), one device per key.
4. Open a **pull request**. Tell us in the description whether you've actually booted the image with these values — "verified live" entries are gold, but unverified best-guesses are welcome too (just say so).

## Don't want to PR?

Open an [issue](../../issues/new) with the image name and whatever you know. We'll take it from there.

## Guidelines

- **One device per entry.** No duplicates.
- **VGA-only guests** (framebuffer, no serial console) → `"console": "vnc"`, or their console is a black screen.
- **Defaults, not dogma.** These are starting points netplex users can override. Prefer the most broadly-correct value.
- Be kind. This is a community effort. 💙

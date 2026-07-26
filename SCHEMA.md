# Schema — `registry/qemu-defaults.json`

A flat JSON object: `{ "<device-slug>": { <fields> }, ... }`. All fields are optional except that an entry should carry at least a `console`.

| Field        | Type   | Meaning |
|--------------|--------|---------|
| `console`    | string | Console channel: `telnet` (serial CLI), `vnc` (VGA/GUI guests), `rdp`. |
| `machine`    | string | QEMU `-machine type=` (e.g. `pc`, `pc-1.0`, `q35`). Omit for the netplex default. |
| `nic_model`  | string | QEMU NIC model: `e1000`, `virtio-net-pci`, `vmxnet3`, `e1000-82545em`, … |
| `cpu`        | int    | Default vCPU count. |
| `ram_mb`     | int    | Default RAM in MB. |
| `interfaces` | int    | Default number of data NICs. |
| `arch`       | string | Guest arch (default `x86_64`). |
| `display`    | string | `serial` or `vga` (derived hint). |
| `vendor`     | string | Lowercase vendor slug (used for icon/grouping in netplex). |
| `category`   | string | `router`, `switch`, `firewall`, `guest`, … |

**Matching:** netplex normalizes an uploaded image's name and matches it against these slugs (longest token wins). A matched entry supplies defaults **only when netplex has no hand-curated profile** for that image; curated profiles always win. Everything here is user-overridable per node.

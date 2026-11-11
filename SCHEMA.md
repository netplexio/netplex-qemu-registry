# Schema

## Device file — `devices/<vendor>/<key>.json`

```json
{
 "key": "fortigate",
 "source": "community",
 "tested": "optional text: what was booted/measured",
 "reasons": { "default_ram_mb": "why this value differs from EVE-NG / the datasheet" },
 "settings": { "emulator": "qemu", "vendor": "fortinet", "console": "telnet", "default_ram_mb": 2048, "cpu": 1 }
}
```

An **alias** (another image name for the same device) has no settings of its own:
`{ "key": "fortinet", "source": "netplex-tested", "alias_of": "fortinet-fortigate" }`.

| Top-level field | Rule |
|---|---|
| `key` | lowercase `a-z 0-9 . _ -`, max 64, equals the file name |
| `source` | `netplex-tested` or `community` |
| `tested`, `reasons` | free text for people (no links or image names); `reasons` keys must be settings the device sets |
| `settings` | the device's defaults (below) |
| `alias_of` | key of a real, non-alias device |
| `group` | optional: `tool-node`, `windows` or `vrnetlab` |

## Settings

Every value comes from a **closed list** (`schema/vocab.json`) or a strict range. Unknown fields and any free-text launch argument fail validation.

| Setting | Allowed |
|---|---|
| `emulator` | qemu, docker, dynamips, iol, lxc, microvm, namespace |
| `vendor`, `role`, `image`, `description`, `notes`, `category`, `min_enforcement_msg`, `config_console_reason` | printable text up to 1000 characters |
| `console` `nic` `disk_bus` `machine` `qemu_arch` `qemu_version_default` `qemu_version_compatible` `node_class` `config_dialect` `day0_channel` `platform` `microvm_engine` `firmware` `boot_order` `video` `tpm` `usb` `serial_type` `accel` `disk_gb` | a value from the matching list in `schema/vocab.json` (`machine` also `pc` / `q35` with a version suffix) |
| `cpu_model` | `[A-Za-z0-9_+,=.-]`, up to 200 characters |
| `min_ram_mb` `default_ram_mb` `recommended_ram_mb` `max_ram_mb` | integers 16 to 1048576 (default/recommended/max at least 64); min <= default <= max |
| `cpu` `max_cpu` `interfaces` | integers (cpu 1-64, interfaces 0-64) |
| `boot_timeout_sec` | 1 to 3600 |
| `kvm` `virtio_extras` `min_enforcement` | true / false |
| `console_init` | up to 16 characters |
| `console_port_mode` `console_spare_ports` | normal / none / spare; 1-3 |
| `cpu_quota_period_us` `cpu_quota_burst` | 1000-1000000; above 0 and at most 100 |
| `reserved_interfaces` `extra_disks` | short lists of plain name/label objects or file names (never a path) |
| `config_console` | `none` |

`registry/devices.json` (generated) is `{"schema": 2, "devices": {key: settings}, "meta": {key: {source, alias_of?, group?}}}` — the file netplex downloads.

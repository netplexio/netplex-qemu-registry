# Why these names are aliases

Lifted verbatim (comment marks removed) from the Python table the platform used before this database existed. An alias file (`alias_of`) means several image names share ONE device entry.

Real Cisco chassis model numbers for the c1700/c2600 Dynamips platform families - "c1700"/
"c2600" are dynamips's own generic PLATFORM labels (`-P 1700`), never how a real image is
named; real images carry the actual chassis model (c1710, c2620, ...). get_profile() matches
by substring, so without these aliases a real chassis-named image never matched its platform's
profile at all and silently fell through to the locked 256MB generic Dynamips fallback in
_build_hardware_defaults - found live 2026-07-12, "c1710-bk9no3r2sy-mz.124-23.image" got
ram=256/256 instead of the real c1700 profile's ram=96/160 + NIC default. Aliased to the SAME
dict object (not a copy) because dynamips itself caps RAM per-PLATFORM, not per-chassis - see
node-manager/providers/dynamips_provider.py's `_C1700_CHASSIS`/`_C2600_CHASSIS`/
`_PLATFORM_MAX_RAM_MB` (one cap for the whole "1700"/"2600" platform, chassis-blind) - so this
introduces no new guess, just recognises the chassis names the runtime already treats as
platform "1700"/"2600". c3600 family chassis (c3620/c3640/c3660) already have their own
dedicated profile entries above and need no alias.

Bare/shorter real image-filename aliases - same problem one level up from the DATA_IFACE_NAMING
bare aliases below: 'timos'/'fortinet'/'mikrotik'/'xrv-k9' are real images on this system with
NO PROFILES match at all (not even the wrong one) under their compound-key vendor/product
name, so get_profile() never even reached this file's own data_iface_fmt merge logic for
them - found 2026-07-29 auditing the full live image library after the DATA_IFACE_NAMING-only
fix silently failed to reach these 4 (get_profile() returns the generic/imported-default
fallback before ever consulting DATA_IFACE_NAMING when PROFILES itself has no match).

vManage profile reachability fix (device audit 2026-07-18, device_id 87f65fe6, image name
"vtmanage-iptela-vmanage"):

get_profile()/get_profile_key() match ONLY by substring of the PROFILES key against the
image's own filename - there is no vendor-aware prefixing anywhere in the call chain
(image-manager/main.py's _build_hardware_defaults passes record.name verbatim;
node-manager/providers/qemu.py passes node.image/base_image_path verbatim). Real vendor
image names never contain the literal substring "cisco" (confirmed live: detector.py's own
VENDOR_PATTERNS comment and netplex-verification's image-marathon manifest, which ships an
actual downloaded folder named "vtmanage/vtmanage-iptela-vmanage-19.1.0/" - no "cisco-"
anywhere in the leaf name). So the profile used to be keyed "cisco-vtmgmt", which required
the filename to contain "ciscovtmgmt" - a substring that can NEVER occur in a real vManage
image name - making the whole profile permanently unreachable, not just for the "vtmanage"
spelling variant. Every device booted from a real vManage image silently fell through to
GENERIC_KVM_PROFILE (512MB default / 256MB min, 1 vCPU) instead of vManage's real 16GB min /
32GB recommended, 4 vCPU minimum (min_enforcement_msg above) - vManage crash-loops under
that little RAM, the same failure shape as the isrv/NX-OS "GENERIC_KVM_PROFILE starves a
heavyweight platform" bugs already documented earlier in this file.

Fixed by renaming the key to the bare, actually-reachable "vtmgmt" above, and aliasing
"vtmanage" (Cisco's own labhub uses both spellings for the same product - detector.py's
VENDOR_PATTERNS already recognises both as NodeVendor.VIPTELA, fixed 2026-07-11) to the
SAME dict object (not a copy) since it is the exact same product/build.

REL-43 fix (production-readiness audit 2026-08-05, docs/status/PRODUCTION-READINESS-WAR-ROOM.md):
the "14 other cisco-*-prefixed PROFILES keys" flagged in the NOTE this replaces were NEVER
actually fixed on another branch - verified live 2026-08-08 by loading this module and
diffing every "cisco-*" PROFILES key against get_profile_key() reachability: exactly 10 of
the 15 cisco-*-prefixed keys had no reachable bare-name twin (cisco-catc, cisco-catcontrol,
cisco-catmanager, cisco-catvalid, cisco-dnac, cisco-fmc, cisco-ftd, cisco-cat8000v,
cisco-csr1000vng, cisco-nxosv9k), of which 7 carry min_enforcement=True
(catc/catcontrol/catmanager/catvalid/dnac/fmc/ftd) - so FTDv (8GB), FMC (28GB) and DNAC
(32GB) could start on the 512MB GENERIC_KVM_PROFILE default with NO admission-control
diagnostic (node-manager/main.py's `if _profile and _profile.get("min_enforcement")` guard
at ~line 714 never fires because get_profile() never resolves to these keys in the first
place) and crash-loop silently. The other 4 unreachable keys (cisco-iosv, cisco-iosvl2,
cisco-xrv9k, cisco-asav) were harmless dead weight - byte-identical duplicates of an
already-reachable bare twin ("iosv"/"iosvl2"/"xrv9k"/"asav") - but still a divergence risk
(an edit to one silently never affects real boots through the other). cisco-xrv was already
fixed correctly (aliased to "xrv" below).

Fix: real vendor image names never contain the literal substring "cisco" (see the vManage
case above), so every "cisco-X" key is aliased/merged onto the bare, real-filename-matching
key X - the SAME dict object, not a copy, so there is exactly one place to update RAM/CPU
per product going forward. Real filenames confirmed via image-manager/detector.py's own
VENDOR_PATTERNS + docstring table: catc1k/catc8k/catc-edge -> "catc", catcontrol-* ->
"catcontrol", catmanager-* -> "catmanager", catvalid-* -> "catvalid", dnac-* -> "dnac",
fmc-*/fmc7-* -> "fmc", ftdv-*/ftd7-* -> "ftd" (substring of "ftdv"), csr1000vng-* ->
"csr1000vng", nxosv9k-* -> "nxosv9k". The 4 harmless duplicates are merged onto their
existing bare twin object (dedup, no behaviour change - both already resolved to
byte-identical specs).

cisco-cat8000v additionally gets merged into "catalyst8000v" (not a fresh alias) - it was
ALREADY a duplicate of that key (see catalyst8000v's own comment above, "duplicate-key
pattern... this key and that one are the same product under two image naming conventions"),
which is exactly A7d's fragmentation report (catalyst8000v listed as one of the P2 items
that "fragment for the same rule-drift reason" as the IOL library/palette count mismatch).
A THIRD real vendor filename convention for the same product was found undocumented in
PROFILES entirely while investigating this (detector.py's own docstring: "Catalyst 8000v
c8000v- c8000v-universalk9_8G_serial.17.15.01a.qcow2") - that exact vendor-documented
filename matched NO PROFILES key at all before this fix (confirmed: get_profile_key()
returned None), so a "c8000v-named" import silently fell to GENERIC_KVM_PROFILE the same as
the two now-fixed conventions. Added as a third alias onto the same merged object.
sourcefire-* real filenames match the bare "sourcefire" token (detector.py VENDOR_PATTERNS),
same aliasing rule as the rest of this block - W1 audit 2026-08-30.
Wave 38 row 38.4 (2026-09-16): real image filenames the project owner sourced for this device
family are "vmxvcp-24.4R1.9-domestic-VCP"/"vmxvfp-24.4R1.9-domestic-VFP" - bare, no
"juniper-" prefix - so without these aliases _match_profile_key() (a plain
prefix/substring match, see its own docstring) could never reach the "juniper-vmxvcp"/
"juniper-vmxvfp" profiles above and both images would silently fall through to
GENERIC_KVM_PROFILE, same class of gap this whole alias block already fixes for every
other vendor above (e.g. "nxosv9k" -> "cisco-nxosv9k").
NPX-1179 (found 2026-09-19 booting every Juniper image through the real platform): an image
stored under a vendor directory ("/netplex/images/qemu/juniper/vqfxre-15.1/hda.qcow2") is
looked up by node-manager as the whole PATH, where the longest key wins - and "juniper-<x>" /
the bare "juniper" vendor key out-lengthed the bare product key ("vmx", "vqfxre", ...), so
the node got a DIFFERENT profile than the Library's by-NAME hardware defaults: no pinned QEMU
version (system QEMU instead of the profile's 2.12.0/4.1.0), the wrong cpu/RAM floor and a
480s boot timeout for a guest that needs ~950s. "juniper-vsrx"/"juniper-vsrxng"/
"juniper-vqfxre" used to be separate hand-copied dicts and had drifted; every "juniper-<x>"
path key is now the SAME object as its product entry, so the two lookups can never disagree.
NPX-1265 (Wave 17): "olive" (legacy Junos 12.1 Olive image; EVE-NG has no olive template) had no
key, so by NAME it resolved to GENERIC (512 MB) and node-manager then bumped it to the by-path
"juniper" profile's recommended 4096. Alias to the same "juniper" profile the by-path lookup uses,
so name and path give identical hardware (2048 MB default), no drift.
NPX-1035 (Wave 21 close, 2026-09-11): csr1000vng-ucmk9-16.12.3-sdwan and
csr1000vng-ucmk9-16.12.4a-sdwan (Cisco Catalyst SD-WAN / IOS-XE cEdge - the "ucmk9"
crypto/SD-WAN-capable image package, distinct from the plain "-universalk9" build the
"csr1000vng"/"cisco-csr1000vng" keys above already cover correctly) matched only the
bare "csr1000vng" key before this fix, which carries no config_dialect override and so
silently fell through to vendor "cisco" - the plain IOS dialect. Live-proved on
<test-vm> (see VENDOR_CLI["cisco-sdwan"]'s own comment in node-manager/node_config.py
for the full transcript): this image ships with its SD-WAN control-plane already
running, so IOS's "configure terminal" is refused ("This command is not supported") and
every config line typed afterward lands as EXEC gibberish ("% Invalid input detected at
'^' marker") - the same failure shape as NPX-818's vtedge/vtbond/vtsmart fix, a
different Cisco product hitting the same "vendor string is not specific enough" bug.
Hardware defaults are otherwise identical to the plain build (same qemu boot profile),
so this entry copies "cisco-csr1000vng" verbatim and only adds the dialect override -
keyed as "csr1000vng-ucmk9" (16 characters after normalization) rather than the shorter
"csr1000vng" (10) so it wins get_profile()'s longest-match rule without touching the
non-SD-WAN "csr1000vng-universalk9"/"cisco-csr1000vng-*" images, which do not contain
the "ucmk9" token anywhere in their real catalog names (confirmed against the live
image library - only these two SD-WAN images use it).
NPX-5053C: the SD-WAN (controller-mode) build bootstraps differently (ciscosdwan_cloud_init.cfg); CVAC is only
live-proven on the universalk9 image, so the ucmk9 copy stays untagged until a live boot proves it (#22).
Wave 17: Device name aliases (device names that match image dirs but need profile mapping)
# Notes carried over from the tool-node, Windows and vrnetlab tables

## tool_node_profiles.py (comments, verbatim)

Cisco pyATS tool node (taxonomy "cisco-tool-pyats", image
ciscotestautomation/pyats:latest-full). No EVE-NG/GNS3 template exists for it
(rule #59 - nothing to match), so the numbers rest on live evidence: on the
generic 512 MB Docker default a single built-in device_health job against ONE
IOL router hit 488/512 MB and NodeMonitor OOM-restarted the node mid-run
(NPX-926, 2026-09-26, VM <test-vm>) - every built-in job failed with a 502.
nmap Network Scanner node - driven by the Studio Network Scanner panel
via an in-container agent (docker-exec curl). Endpoint, not a router.
Key MUST stay "-tool-" to match taxonomy's docker_image (get_profile
matches on the normalized image name; "-edu-" here = no profile).

cpu bumped 1 -> 2 (2026-08-14, 4th pass on 111-scanner-advanced.spec.ts's "OS
detect chip" flake, after d880e56a's curl-budget bump alone didn't hold under a
busy nightly run - confirmed live in the archived run, e.g. the neighbouring
"Service/version chip" -sV case in the same file took 8.9-9.0 MINUTES for a
top-100-port localhost scan that is CPU-bound work of a few seconds unconstrained
- a scale of slowdown a bigger curl -m budget can't paper over). Root cause (rule
25): `docker exec curl` and this container's own uvicorn control agent both run
IN THE SAME cgroup as the nmap subprocess they're serving/proxying to (that
scoping itself is correct - exec always joins the target container's cgroup) -
under Linux CFS bandwidth control a 1-vCPU hard quota means once nmap's CPU-bound
burst (-O/-sV/-T5/NSE) exhausts the quota within a period, EVERY process in the
cgroup is throttled together, including the trivial GET /scan dict-read the agent
is trying to answer. Widening the client-side curl -m window (d880e56a) raises
the bar the request has to clear but does nothing to relieve the throttling
itself, so on a sufficiently busy host it will always eventually blow whatever
number is chosen. Giving the container a genuine 2nd vCPU (matching the existing
keysight-ixia-c-one precedent just above - cpu=2 specifically so control-plane
traffic isn't starved by the workload it's driving) means nmap's ~1-core burst no
longer needs to consume the WHOLE quota, leaving real spare CFS bandwidth each
period for the agent's own HTTP handling and the exec'd curl - the structural fix
for the resource contention, not another guess at the wait-budget number.
NPX-1000 (6th of the 7 tools to get NPX-994's mechanism, after bandwidth
tester, traffic-gen, traffic-rx, multicast-gen and multicast-rx): eth0
stays this node's normal data interface (drawn/wired by the user like
any other port); eth1 is the fixed, profile-declared OOB web-access
port - never a user-assignable data link, only ever cabled to a Cloud
gateway (see shared.models.ReservedInterface/check_reserved_interface_link).
NPX-2557: console server. No EVE-NG/GNS3 template exists for it (rule #59 -
nothing to match; EVE-NG models console access as per-node telnet ports only).
The container just holds the interfaces; node-manager's ts_relay publishes one
TCP port per cabled device and relays it to that device's serial console.
eth0 = uplink (cable it to a Cloud node to reach the ports from outside the lab),
eth1..eth16 = the 16 device ports.
Packet Capture node - authentic Wireshark, streamed over RDP. "console": "rdp"
is the ONE line that activates docker_provider.py's already-generic RDP-bridge
auto-detection (rt.rdp_port -> guacd) - no per-image console-pipeline code
needed (see docs/platform/packet-capture-wireshark-handoff.md §5 + the
packet-capture-wireshark-tool implementation plan). Resource baseline from
EVE-NG's own eve-wireshark.yml (verified live via SSH to <eveng-box>,
2026-08-14): cpu:1, ram:1024 - a full xrdp+xfce+Wireshark session, heavier
than this group's other cpu:1/ram:128-384 CLI-agent tools.
NPX-996 (2nd of the 7 tools to get NPX-994's mechanism, after bandwidth
tester): eth0 stays this node's normal data interface (drawn/wired by the
user like any other port); eth1 is the fixed, profile-declared OOB web-access
port - never a user-assignable data link, only ever cabled to a Cloud gateway
(see shared.models.ReservedInterface/check_reserved_interface_link).
NPX-998 (4th of the 7 tools to get NPX-994's mechanism, after bandwidth
tester, traffic-gen and traffic-rx): eth0 stays this node's normal data
interface (drawn/wired by the user like any other port); eth1 is the fixed,
profile-declared OOB web-access port - never a user-assignable data link,
only ever cabled to a Cloud gateway (see
shared.models.ReservedInterface/check_reserved_interface_link).
NPX-999 (5th of the 7 tools to get NPX-994's mechanism, after bandwidth
tester, traffic-gen, traffic-rx and multicast-gen): eth0 stays this node's
normal data interface (drawn/wired by the user like any other port); eth1
is the fixed, profile-declared OOB web-access port - never a
user-assignable data link, only ever cabled to a Cloud gateway (see
shared.models.ReservedInterface/check_reserved_interface_link).
Wave 9 B1 (2026-08-26): taxonomy.py had this tool (docker_image
"netplex-tool-traffic-rx:latest") but PROFILES had no entry, so
_match_profile_key() found nothing and get_profile() silently fell back to
GENERIC_KVM_PROFILE for a Docker-only tool. Shape mirrors multicast-rx (a
unicast measurement/receiver container, same emulator/role/console story) -
no multicast-only fields (e.g. group-membership) apply here, so nothing was
dropped from that template.
NPX-997 (3rd of the 7 tools to get NPX-994's mechanism, after bandwidth
tester and traffic-gen): eth0 stays this node's normal data interface
(drawn/wired by the user like any other port); eth1 is the fixed,
profile-declared OOB web-access port - never a user-assignable data
link, only ever cabled to a Cloud gateway (see
shared.models.ReservedInterface/check_reserved_interface_link).
AAA lab node: FreeRADIUS + tac_plus + OpenLDAP + the control agent in one
container. Heavier than the measurement tools (three daemons), so 512MB is
the recommended default (FreeRADIUS docs suggest 512MB-1GB; a small slapd dir
fits well under that). Key MUST stay "-tool-" to match taxonomy's docker_image.
Row 9.7 (T10): iperf3-based bandwidth tester, one image serves both Client and
Reflector roles (mode picked in-panel). Shape mirrors traffic-rx/multicast-rx -
a lightweight measurement container, Docker-only, no console beyond docker-exec.
NPX-994: eth0 stays this node's normal data interface (drawn/wired by the
user like any other port); eth1 is the fixed, profile-declared OOB web-access
port - never a user-assignable data link, only ever cabled to a Cloud gateway
(see shared.models.ReservedInterface/check_reserved_interface_link). This is
the FIRST of the 7 built-in tool nodes to get this - proof-of-mechanism only,
the other 6 (AAA Server, Traffic Gen/Rx, Multicast Gen/Rx, Network Scanner)
get the same one-line addition once the mechanism is proven end to end.
T12 (NPX-942, Wave 23 SS23.6): RFC 2544 benchmark tester. ONE node, TWO
fixed data ports (eth0=Tx/port 1, eth1=Rx/port 2, one process/one clock -
see the war-room design's "why this beats two nodes" - a second container
would need an in-band peer-stats channel THROUGH the device under test,
polluting the exact thing being measured). Per NPX-992's later addition
(carried into SS23.14.9 row 23.F.1), a THIRD port eth2 is reserved for the
gateway-only OOB web UI, same mechanism netplex-tool-bandwidth already
proved (reserved_interfaces below) - never a user-assignable data link.
Image built+proven on VM 600 (infra/edu-images/Dockerfile.rfc2544-tester,
tagged by infra/edu-images/build-all.sh's PLATFORM_TOOLS loop as
netplex-tool-rfc2544-tester:latest). Key MUST stay "-tool-" to match
taxonomy's docker_image, same convention as every sibling tool node.
Heavier than the lightweight Python measurement tools (96-192MB): this is
a compiled Go binary doing its own AF_PACKET PACKET_MMAP TX_RING/RX_RING
packet I/O (not a Python send loop), and the design explicitly targets
multi-Mpps on veth - real packet buffers/rings cost real memory, and the
datapath wants a core mostly to itself to avoid scheduling jitter
polluting the CLOCK_MONOTONIC_RAW latency stamps. 256MB/2 CPU is a
deliberately generous-but-not-invented estimate for that workload, not
the ~96-192MB/1 CPU the iperf3/nmap/radius tools need.
NPX-642, Wave 23: ITU-T Y.1564 Ethernet service activation tester.
Same two-fixed-data-port + reserved OOB-web-port shape as
netplex-tool-rfc2544-tester above (eth0=Tx/port 1, eth1=Rx/port 2,
eth2=gateway-only OOB web UI) - and the SAME underlying image
bytes, since both tools are the one Go binary (see taxonomy.py's
own comment on this key for why no separate Dockerfile/build
exists - only a second `docker tag`, needed because `image` is the
only reliable signal StudioConsole.tsx's node-type detectors have,
see that file's own comment). Resource sizing copied from the
rfc2544 entry for the same reason (same binary, same AF_PACKET
PACKET_MMAP datapath under the hood) - not independently
re-derived.

## windows_profiles.py (comments, verbatim)

── Windows (NPX-631, project owner decision 2026-10-02) ────────────────────────────
Copied field-for-field from EVE-NG's real templates (root@<eveng-box>:/opt/unetlab/
html/templates/intel/win.yml + winserver.yml, rule #33): qemu 4.1.0, machine pc, 1 vCPU,
ram 4096 (client) / 8192 (server), 1 NIC, console vnc (a graphical desktop - EVE's
`console: vnc`), no NIC/disk model in the template -> EVE's own defaults e1000 + ide
(same reading as the timos entry below; Windows has no virtio drivers out of the box).
EVE's -cpu strings are copied verbatim (client: pcid + Hyper-V enlightenments; server:
host,+fsgsbase). NOT live-boot-verified: the project owner waived the boot test (no Windows image
will be supplied; rule #13 exemption by named decision, 2026-10-02).
Written deviations (rule #59), all because the same thing is already provided by netplex:
  -vga std / -usbdevice tablet : libvirt domain always carries a VGA video device
    (qemu.py _graphics_xml) and a VNC pointer, so no raw flag is needed (and -usbdevice
    is not on the qemu_extra_args allowlist, which is host-safety, not ours to widen).
  -boot order=cd / dc : netplex's own boot_order control owns boot order per node.
  ethernet: 1 : the template's NIC count is per-node here (the user draws the links), not a profile field.
  virtio-win-drivers.img floppy : a host-path -drive, refused by the same allowlist;
    netplex ships no such image. Windows on e1000/ide does not need it.

## vrnetlab_profiles.py (comments, verbatim)

Cisco CSR1000v via vrnetlab (cisco/csr1000v/Makefile -> IMG_REPOSITORY "vrnetlab/cisco_csr1000v").
Before this entry the imported image resolved to the generic profile (vendor "generic", 512 MB)
while the nested CSR needs 4096 MB. Values mirror the native "csr1000v" entry (rule #59) and
upstream csr launch.py (ram=4096; the wrapper fixes the inner -smp itself, so cpu=1 is the real
setting, not a choice). boot_timeout_sec: measured ~34 min cold boot on a 1-vCPU test VM
(nested QEMU) - budgeted at 45 min.

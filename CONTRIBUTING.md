# Contributing

Thank you for helping! One device = one small file = one pull request.

## Change or add a device

1. **Fork** this repo.
2. Edit **one file**: `devices/<vendor>/<key>.json` (copy a similar device for a new one). The `key` is a lowercase slug (`a-z 0-9 . _ -`) and equals the file name; the folder is the vendor (`settings.vendor`).
3. Check it **locally**: `python3 tools/validate.py` (must print `OK`), then `python3 tools/build.py` and commit the two generated files in `registry/`.
4. Open a **pull request**. Say in the description whether you booted the image with these values ("verified live" is gold; an honest best-guess is welcome too) and where the numbers come from (vendor datasheet, EVE-NG template, your own boot).

A value that differs from what EVE-NG or the vendor documents needs a written reason in `reasons.<field>` of the same file. Evidence beats opinion.

## What we check

- `validate.py` is clean: known fields only, every value from the closed lists in `schema/vocab.json` or inside its range, RAM `min <= default <= max`, folder = vendor, file name = key.
- The numbers make sense for the device and are not copied blindly from somewhere else.
- `registry/` was rebuilt (`build.py --check` passes).

Validation is a **local script that maintainers run before merging** — we run no automated workflows on pushes or pull requests.

## What is never accepted

- **Free-text launch arguments** — no `qemu_extra_args`, no command lines, no shell fragments. Settings are choices from closed lists and numbers.
- **Binaries and image files**, or links to images, licences or keys (and especially to pirated images). Only `.json` device files belong here.
- Unknown fields, new top-level files, or edits to `registry/*.json` that `build.py` would not produce.

## Who can merge

Only members of the netplexio organisation can merge (this is how a public repository works by default: everyone may fork and propose, only members with write access merge). Maintainers run `python3 tools/validate.py && python3 tools/build.py --check` before every merge.

## Not a developer?

Open an [issue](../../issues/new) with the image name and whatever you know about its console, NIC, RAM and CPU.

# EN-only asset migration

- Rewrote 42 generated `module/**/assets.py` modules to scalar EN properties.
- Copied every file selected by the former EN mapping from a fallback server directory into the corresponding `assets/en/...` path before deletion.
- Updated `dev_tools/button_extract.py` so `assets/en` is the sole generator source.
- Removed `assets/cn`, `assets/jp`, and `assets/tw` only after reference and existence checks passed.

Some EN assets are visually language-neutral geometry or icon templates that historically lived under `assets/cn`; their bytes were preserved under EN paths rather than discarded.

# EN-only unique-content migration

| Source | Section | Unique? | Relevant to EN? | Action | English destination |
|---|---|---:|---:|---|---|
| `README.md` (CN) | Device support link | Yes | Partly | Keep only the general emulator requirement; drop CN-only wiki dependency | `README.md` Installation |
| `README.md` (CN) | ADB/uiautomator2 instability known issue | Yes | Yes | Translate and retain | `README.md` Known issues |
| `README.md` (CN) | Related projects: FGO-py and StarRailCopilot | Yes | No operational value | Omit from the concise fork README; attribution is unaffected | n/a |
| `README.md` (CN) | QQ/Bilibili contacts | Yes | No | Remove as CN-community-only contact information | n/a |
| `README_jp.md` | Installation and scheduler descriptions | No | Yes | English equivalent already exists; do not duplicate | `README.md` |
| `README_jp.md` | JP support credits | Yes as attribution | Yes | Preserve in English acknowledgements | `README.md` Acknowledgements |
| Localized GUI bundles | User-facing translations | Yes | No | Delete after retaining English keys | `module/config/i18n/en-US.json` |
| Localized runtime comments | General algorithm notes | Case-by-case | Yes when algorithmic | Translate or retain English comments during simplification | Relevant Python module |

No unique general-purpose CN/JP/TW technical procedure was deleted without an English equivalent. Server-specific APK, mirror, endpoint, locale, and troubleshooting instructions are intentionally not migrated.

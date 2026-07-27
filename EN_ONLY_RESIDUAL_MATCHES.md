# EN-only residual-match audit

No unallowlisted removed package, locale, dispatch, asset-path, AzurStats, or CN-infrastructure matches remain in committed text sources.

## Intentionally retained legacy names

- Campaign directories ending in `_cn` are shared map implementations and are not treated as active CN client support.
- The generic OCR property/model named `cnocr` remains because EN code uses it for general digit/Latin OCR. JP/TW-specific models were removed.
- `UNSUPPORTED_PACKAGE` contains removed package IDs only to reject them with a clear error.
- Contributor names, game proper nouns, Git history, and license/attribution are preserved.
- Temporary migration scripts and GitHub Actions workflows were removed before the final branch was pushed.

## CJK residual classification

| Path | Classification |
|---|---|
| `bin/cnocr_models/cnocr/label_cn.txt` | Shared OCR model data used by the EN runtime; not regional client support. |
| `config/template.maa.json` | External submodule/template protocol data; outside Azur Lane CN/JP/TW runtime selection. |
| `en_only_removal_manifest.csv` | Audit manifest preserving original paths and classifications. |
| `module/device/connection.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/connection_attr.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/method/ldopengl.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/platform/emulator_windows.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/platform/platform_windows.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/tactical/tactical_class.py` | Game proper nouns/shared recognition data; not regional client support. |
| `submodule/AlasMaaBridge/module/config/argument/args.json` | External bridge protocol data; outside Azur Lane regional runtime selection. |
| `submodule/AlasMaaBridge/module/config/argument/argument.yaml` | External bridge protocol data; outside Azur Lane regional runtime selection. |
| `submodule/AlasMaaBridge/module/config/config_generated.py` | External bridge protocol data; outside Azur Lane regional runtime selection. |
| `submodule/AlasMaaBridge/module/config/i18n/en-US.json` | English display strings plus opaque external protocol identifiers. |
| `submodule/AlasMaaBridge/module/handler/handler.py` | External bridge protocol identifiers required for compatibility. |

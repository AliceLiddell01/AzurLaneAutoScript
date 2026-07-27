# EN-only residual-match audit

The following matches remain and require classification. They are not automatically proof of active server support.

| Path | Line | Kind | Match |
|---|---:|---|---|
| `.github/workflows/en-only-finalize.yml` | 75 | removed_azurstats | `&#124; jq -r '.content' &#124; tr -d '\n' &#124; base64 --decode > /tmp/azurstats-patch.b64` |
| `.github/workflows/en-only-finalize.yml` | 76 | removed_azurstats | `base64 --decode /tmp/azurstats-patch.b64 > /tmp/azurstats-patch.gz` |
| `.github/workflows/en-only-finalize.yml` | 77 | removed_azurstats | `echo "2417e6a2724de3dd8ef868a4144d9d294a974be3dfd6e4670207ed110bfd7059  /tmp/azurstats-patch.gz" &#124; sha256sum --check` |
| `.github/workflows/en-only-finalize.yml` | 78 | removed_azurstats | `gzip -dc /tmp/azurstats-patch.gz &#124; git apply` |
| `.github/workflows/en-only-finalize.yml` | 140 | removed_azurstats | `commit_phase azurstats 'refactor(statistics): remove AzurStats integration'` |
| `.github/workflows/en-only-finalize.yml` | 144 | removed_azurstats | `commit_phase tests 'test: add EN-only package config and AzurStats coverage'` |
| `.github/workflows/en-only-final2.yml` | 141 | removed_azurstats | `commit_phase azurstats 'refactor(statistics): remove AzurStats integration'` |
| `.github/workflows/en-only-final2.yml` | 145 | removed_azurstats | `commit_phase tests 'test: add EN-only package config and AzurStats coverage'` |
| `.github/workflows/en-only-audit-export.yml` | 75 | removed_azurstats | `&#124; jq -r '.content' &#124; tr -d '\n' &#124; base64 --decode > /tmp/azurstats_patch.b64` |
| `.github/workflows/en-only-audit-export.yml` | 76 | removed_azurstats | `base64 --decode /tmp/azurstats_patch.b64 > /tmp/azurstats_patch.gz` |
| `.github/workflows/en-only-audit-export.yml` | 77 | removed_azurstats | `echo "2417e6a2724de3dd8ef868a4144d9d294a974be3dfd6e4670207ed110bfd7059  /tmp/azurstats_patch.gz" &#124; sha256sum --check` |
| `.github/workflows/en-only-audit-export.yml` | 78 | removed_azurstats | `gzip -dc /tmp/azurstats_patch.gz > /tmp/azurstats_tools.patch` |
| `.github/workflows/en-only-audit-export.yml` | 79 | removed_azurstats | `git apply /tmp/azurstats_tools.patch` |
| `.github/workflows/en-only-audit-export.yml` | 156 | removed_azurstats | `commit_phase azurstats 'refactor(statistics): remove AzurStats integration'` |
| `.github/workflows/en-only-audit-export.yml` | 160 | removed_azurstats | `commit_phase tests 'test: add EN-only package config and AzurStats coverage'` |
| `.github/workflows/en-only-resume.yml` | 75 | removed_azurstats | `&#124; jq -r '.content' &#124; tr -d '\n' &#124; base64 --decode > /tmp/azurstats_patch.b64` |
| `.github/workflows/en-only-resume.yml` | 76 | removed_azurstats | `base64 --decode /tmp/azurstats_patch.b64 > /tmp/azurstats_patch.gz` |
| `.github/workflows/en-only-resume.yml` | 77 | removed_azurstats | `echo "2417e6a2724de3dd8ef868a4144d9d294a974be3dfd6e4670207ed110bfd7059  /tmp/azurstats_patch.gz" &#124; sha256sum --check` |
| `.github/workflows/en-only-resume.yml` | 78 | removed_azurstats | `gzip -dc /tmp/azurstats_patch.gz &#124; git apply` |
| `.github/workflows/en-only-resume.yml` | 144 | removed_azurstats | `commit_phase azurstats 'refactor(statistics): remove AzurStats integration'` |
| `.github/workflows/en-only-resume.yml` | 148 | removed_azurstats | `commit_phase tests 'test: add EN-only package config and AzurStats coverage'` |


## Intentionally retained legacy names

- Campaign directories ending in `_cn` are shared map implementations and are not treated as active CN client support.
- The generic OCR property/model named `cnocr` remains because EN code uses it for general digit/Latin OCR. JP/TW-specific models were removed.
- `UNSUPPORTED_PACKAGE` contains removed package IDs only to reject them with a clear error.
- Contributor names, game proper nouns, Git history, and license/attribution are preserved.

## CJK residual classification

| Path | Classification |
|---|---|
| `bin/cnocr_models/cnocr/label_cn.txt` | Attribution, game proper noun, or shared technical data; classified as non-server support. |
| `config/template.maa.json` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |
| `dev_tools/en_only_data_cleanup.py` | Audit patterns and migration implementation. |
| `dev_tools/en_only_migration.py` | Audit patterns and migration implementation. |
| `en_only_removal_manifest.csv` | Attribution, game proper noun, or shared technical data; classified as non-server support. |
| `module/device/connection.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/connection_attr.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/method/ldopengl.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/platform/emulator_windows.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/device/platform/platform_windows.py` | Emulator/vendor/installer technical data; not CN/JP/TW client support. |
| `module/tactical/tactical_class.py` | Attribution, game proper noun, or shared technical data; classified as non-server support. |
| `submodule/AlasMaaBridge/module/config/argument/args.json` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |
| `submodule/AlasMaaBridge/module/config/argument/argument.yaml` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |
| `submodule/AlasMaaBridge/module/config/config_generated.py` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |
| `submodule/AlasMaaBridge/module/config/i18n/en-US.json` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |
| `submodule/AlasMaaBridge/module/handler/handler.py` | External submodule/template data; outside Azur Lane CN/JP/TW runtime selection. |

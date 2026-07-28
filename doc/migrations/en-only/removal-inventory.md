# EN-only removal inventory

## Baseline

- Fork `master`: `5e0453a6349c273efb558fc583da55e11f938248`
- Upstream `master`: `5e0453a6349c273efb558fc583da55e11f938248`
- Working branch: `refactor/en-only-remove-cn-jp-tw`
- Python: `not recorded`
- Node: `not recorded`
- npm: `not recorded`
- pnpm: `not available`
- Baseline compile/import check: passed before functional changes; pre-existing `SyntaxWarning` messages were recorded separately.

## Inventory summary

| Kind | Matched files |
|---|---:|
| asset | 45 |
| build_or_deploy | 22 |
| campaign | 37 |
| config | 20 |
| documentation | 5 |
| gui_locale | 4 |
| other | 22 |
| runtime | 138 |

The detailed, machine-readable manifest remains in [`../../../en_only_removal_manifest.csv`](../../../en_only_removal_manifest.csv). A match is not an instruction to delete: campaign data, attribution, and shared geometry/assets are reviewed before action.
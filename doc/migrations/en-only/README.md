# EN-only migration archive

This directory contains the evidence and handoff material produced when the fork was converted to Azur Lane Global / EN-only operation and AzurStats integration was removed.

These documents are **historical migration records**, not the active modernization roadmap. Current work belongs in [`../../roadmap/`](../../roadmap/).

## Documents

- [`changelog.md`](changelog.md) — concise summary of the completed EN-only migration.
- [`azurstats-removal.md`](azurstats-removal.md) — removed upload surface and retained local recording behaviour.
- [`configuration.md`](configuration.md) — accepted EN-only configuration values and migration behaviour.
- [`assets.md`](assets.md) — asset-tree consolidation and generated asset changes.
- [`unique-content.md`](unique-content.md) — disposition of unique content from localized documentation.
- [`wiki-handoff.md`](wiki-handoff.md) — manual follow-up required for the separate GitHub Wiki.
- [`removal-inventory.md`](removal-inventory.md) — baseline and high-level inventory counts.
- [`residual-match-audit.md`](residual-match-audit.md) — intentionally retained historical names and residual classifications.
- [`validation-report.md`](validation-report.md) — checks performed during the migration and their historical limitations.

The machine-readable inventory remains at [`../../../en_only_removal_manifest.csv`](../../../en_only_removal_manifest.csv) until a later data-file cleanup work package moves it with tooling that preserves and validates the complete file.

## Interpretation rules

- `PASS` statements in the historical validation report describe the recorded migration environment, not the current branch state.
- Skipped webapp checks and unavailable real-device checks are not current validation.
- Campaign directories containing `_cn` or `_tw` require runtime-reference analysis before removal.
- The generic `cnocr` model name may refer to shared OCR assets used by the EN runtime.
- Historical repository and Wiki content was not automatically rewritten.
# Project documentation

This directory contains durable project documentation that should not live in the repository root.

## Active work

- [`roadmap/`](roadmap/) — active modernization roadmap, milestones, and audit remediation tracking.

## Historical and completed work

- [`migrations/en-only/`](migrations/en-only/) — evidence and handoff documents from the EN-only and AzurStats-removal migration.

## Repository-wide guidance

- [`../AGENTS.md`](../AGENTS.md) — mandatory operating rules for automated agents and contributors.
- [`../README.md`](../README.md) — user-facing project overview and installation entry point.

## Documentation placement

Use these rules when adding documentation:

- Active plans, milestones, and work-package tracking belong in `roadmap/`.
- Completed migration records belong in `migrations/<migration-name>/`.
- Durable audit reports belong in `audits/` when that directory is introduced.
- README media remains in `README.assets/`.
- Only project-wide entry-point documents should remain in the repository root.

Every directory containing multiple documents should include a `README.md` index.
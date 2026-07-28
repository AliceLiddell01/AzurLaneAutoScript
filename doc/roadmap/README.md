# Modernization roadmap

This directory is the canonical planning surface for the fork's modernization programme.

## Primary objective

Move the project to **CPython 3.14.6 on Windows x86-64** while fixing the repository, security, dependency, packaging, updater, device-integration, and validation problems identified by the 2026 repository audit.

The migration is incremental. The repository must remain reviewable and the EN-only/no-AzurStats invariants must remain intact at every milestone.

## Documents

- [`python-3.14-modernization.md`](python-3.14-modernization.md) — master roadmap, dependency graph, phases, work packages, risks, and acceptance criteria.
- [`audit-remediation-register.md`](audit-remediation-register.md) — finding-by-finding status register and closure evidence requirements.

## Current programme state

- Governance and documentation structure: **IN PROGRESS**
- Runtime target: **CPython 3.14.6, standard GIL build**
- Existing production runtime baseline: **legacy and not yet reproducibly declared**
- OCR migration: **NOT STARTED**
- Reproducible toolkit/package build: **NOT STARTED**
- Authorized EN-device end-to-end validation: **BLOCKED / NOT YET PERFORMED**

## Milestone order

1. `M0` — governance and repository containment
2. `M1` — reproducible legacy baseline
3. `M2` — dependency and Python compatibility inventory
4. `M3` — Python 3.14 installable core
5. `M4` — modern core dependency stack
6. `M5` — OCR backend replacement
7. `M6` — device and ADB modernization
8. `M7` — GUI, webapp, Electron, and network hardening
9. `M8` — updater, installer, and packaging reconstruction
10. `M9` — complete automated and authorized manual validation
11. `M10` — Python 3.14.6 release candidate

A later milestone must not be declared complete while required exit criteria from an earlier milestone remain open.
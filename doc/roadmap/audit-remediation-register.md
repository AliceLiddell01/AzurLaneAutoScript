# Audit remediation register

This register normalizes the actionable findings from the repository audit performed on 2026-07-28.

The detailed audit was conducted against fork commit `6eade51dd48ab4f844a899e1a14e8e63a08c4ddb`. Finding descriptions below are concise tracking summaries rather than a replacement for the original audit evidence.

## Status vocabulary

- `OPEN` — confirmed finding with no completed remediation.
- `IN_PROGRESS` — an active work package addresses the finding.
- `BLOCKED` — remediation or validation depends on unavailable infrastructure, artifacts, or authorization.
- `MITIGATED` — immediate risk reduced, but full closure criteria are not met.
- `CLOSED` — remediation and validation evidence are complete.
- `ACCEPTED_RISK` — project owner explicitly accepts the remaining risk.

## Findings

| ID | Severity | Status | Summary | Planned milestone | Closure evidence |
|---|---|---|---|---|---|
| `ALAS-AUDIT-001` | P0 | OPEN | Default deployment/update configuration targets upstream `LmeSzinc/AzurLaneAutoScript`; updater logic can reset and pull destructively. | M0 / M8 | Fork-safe defaults, updater disabled or contained by default, disposable-repository tests, documented rollback behaviour. |
| `ALAS-AUDIT-002` | P1 | OPEN | GUI defaults can bind to `0.0.0.0` while authentication is absent when no password/key is configured. | M0 / M7 | Loopback default, explicit remote-access opt-in, authentication-state tests and documentation. |
| `ALAS-AUDIT-003` | P1 | IN_PROGRESS | No repository-wide agent/contributor governance file and no canonical documentation placement policy. | M0 | Root `AGENTS.md`, documentation index, roadmap, and review of repository links. |
| `ALAS-AUDIT-004` | P1 | OPEN | Validation documentation reports overall PASS although webapp and real-device checks were skipped or unavailable. | M1 / M9 | Result vocabulary applied, reports distinguish PASS/FAIL/BLOCKED/SKIPPED/UNKNOWN, rerun evidence. |
| `ALAS-AUDIT-005` | P1 | OPEN | Webapp `package-lock.json` is inconsistent with `package.json`, including missing direct dependencies and root metadata drift. | M1 / M7 | Clean lockfile regeneration, immutable install succeeds, lint/typecheck/test/build results recorded. |
| `ALAS-AUDIT-006` | P1 | OPEN | Windows deployment configuration contains legacy repository aliases pointing to `LmeSzinc/StarRailCopilot`. | M0 / M8 | Aliases removed or corrected, config migration tests, repository-target scan passes. |
| `ALAS-AUDIT-007` | P2 | OPEN | `alas.py` contains a stale `azur_lane_uncensored()` path importing a removed module. | M1 / M3 | Dead path removed or replaced, import/static tests and scheduler/task regression tests. |
| `ALAS-AUDIT-008` | P1 | OPEN | No durable root CI enforces Python, EN-only, generated-output, dependency, or webapp invariants. | M1 | CI workflows on pull requests, documented required checks, initial green baseline or explicit known-failure gates. |
| `ALAS-AUDIT-009` | P1 | OPEN | Runtime/toolchain contract is unclear and obsolete: Docker uses Python 3.7 while historical validation used Python 3.10.20. | M1 / M3 | Version policy, reproducible environments, Python 3.14 CI, supported-platform matrix. |
| `ALAS-AUDIT-010` | P1 | OPEN | Electron wrapper enables `nodeIntegration` and disables `contextIsolation`. | M7 | Isolated renderer, minimal preload bridge, Electron security tests and launch smoke. |
| `ALAS-AUDIT-011` | P1 | OPEN | Installer/deploy defaults may replace ADB, auto-connect, install dependencies, or install uiautomator2 without sufficiently explicit user control. | M6 / M8 | Safe defaults, explicit opt-in, dry-run/plan view, integration tests in disposable environment. |
| `ALAS-AUDIT-012` | P1 | BLOCKED | Complete toolkit/package is not reproducible from the repository; bundled Python, Git, ADB, webapp executable, and native artifacts are external. | M8 | Documented artifact sources, checksums/SBOM, scripted build, clean-VM reproduction and launch test. |
| `ALAS-AUDIT-013` | P2 | OPEN | Server checking depends on an external HTTP endpoint with unclear privacy, trust, and failure semantics. | M7 | Remove, replace, or explicitly document/disable endpoint; add timeout/failure/privacy tests. |
| `ALAS-AUDIT-014` | P1 | BLOCKED | No authorized real EN-client device/emulator smoke test validates login, OCR, package lifecycle, and representative tasks. | M9 | Approved test target, written procedure, captured evidence, failures triaged. |
| `ALAS-AUDIT-015` | P2 | OPEN | README installation flow depends on upstream documentation that may diverge from fork behaviour and packaging. | M8 / M10 | Fork-owned installation guide validated on a clean system and linked from README. |
| `ALAS-AUDIT-016` | P2 | OPEN | Residual/migration documentation is incomplete or overconfident for some historically named paths, including legacy `_tw` content discovered by later audit. | M0 / M1 | Updated classification inventory, automated residual scan, documented allowlist with runtime-reference evidence. |

## Cross-cutting Python 3.14 blockers

These blockers are tracked by the roadmap even when they are not represented by a single audit ID:

| Blocker | State | Required resolution |
|---|---|---|
| MXNet 1.x / CnOCR 1.x OCR stack | OPEN | Introduce OCR backend abstraction; migrate models/inference to a maintained Python 3.14-capable backend; validate against an EN screenshot corpus. |
| Obsolete native dependency pins | OPEN | Build a Windows wheel-availability matrix and upgrade packages in isolated groups. |
| Removed/deprecated standard-library APIs between Python 3.7 and 3.14 | OPEN | Static/import scan, compatibility patches, and tests. |
| No explicit `pyproject.toml` runtime contract | OPEN | Introduce project metadata and dependency groups after baseline inventory. |
| Legacy bundled runtime/toolkit | BLOCKED | Recover or reconstruct artifact inputs and produce a clean reproducible build. |
| ADB/uiautomator2 API drift | OPEN | Adapter-level audit and disposable emulator integration matrix. |

## Closure procedure

A finding may move to `CLOSED` only when all applicable items are present:

1. A pull request or commit implements the remediation.
2. The register links or names the validating test evidence.
3. The relevant roadmap exit criterion is satisfied.
4. Documentation reflects the new behaviour.
5. EN-only and no-AzurStats scans remain clean.
6. Skipped or blocked checks are not presented as successful.

## Current update

This documentation-reorganization work starts remediation of `ALAS-AUDIT-003`. It does not close runtime, updater, dependency, packaging, webapp, OCR, or device findings.
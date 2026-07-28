# AGENTS.md

## Purpose

This file defines the operating rules for automated coding agents and human contributors working in this repository.

The repository is an **EN-only fork of AzurLaneAutoScript**. Its long-term modernization target is **CPython 3.14.6 on Windows x86-64**, while preserving functional compatibility with the Azur Lane Global client.

These instructions apply to the entire repository unless a more specific `AGENTS.md` exists in a subdirectory.

## Repository invariants

The following rules are non-negotiable:

1. The supported game client is **Azur Lane Global / EN only**.
2. The only supported Android package is `com.YoStarEN.AzurLane`.
3. Runtime and GUI localization remain English-only unless the project owner explicitly changes scope.
4. AzurStats upload, identifiers, endpoints, branding, and upload-capable modes must not be reintroduced.
5. Local drop-image recording through `DropRecorder` may remain available.
6. Historical attribution, licensing, contributor history, and Git history must be preserved.
7. Campaign directories ending in `_cn` or `_tw` are not automatically regional-client code. Review runtime references before changing or deleting them.
8. The generic `cnocr` name may refer to shared OCR data used by the EN runtime. Do not remove it solely because of its historical name.
9. Unsupported regional package identifiers may remain only as explicit deny-list values used to produce clear EN-only diagnostics.
10. Upstream synchronization must never silently restore removed regional clients, AzurStats, unsafe updater defaults, or deleted generated outputs.

## Current modernization target

The primary modernization programme is documented in:

- `doc/roadmap/README.md`
- `doc/roadmap/python-3.14-modernization.md`
- `doc/roadmap/audit-remediation-register.md`

The target runtime is:

- CPython `3.14.6`
- standard GIL-enabled Windows x86-64 build
- reproducible dependency resolution
- reproducible application/toolkit packaging
- modern OCR backend without MXNet

Do not treat the free-threaded CPython build or experimental JIT as part of the initial migration acceptance criteria.

## Priority order

When requirements conflict, use this priority order:

1. User safety, credential safety, and repository integrity.
2. EN-only and no-AzurStats invariants.
3. Reproducible builds and explicit source-of-truth rules.
4. Runtime correctness on the supported EN client.
5. Backward-compatible configuration migration.
6. Maintainability and documentation quality.
7. Performance improvements.

## Required workflow

Before editing:

1. Read this file.
2. Read the relevant roadmap phase and audit entries.
3. Inspect the current branch, working tree, and remotes.
4. Identify whether the target file is handwritten, generated, vendored, or external.
5. Identify the narrowest meaningful validation that can prove the change.
6. Record any device, emulator, network, toolkit, or proprietary-data dependency that prevents full validation.

During editing:

1. Keep changes scoped to one work package whenever practical.
2. Do not mix repository cleanup, dependency upgrades, runtime rewrites, and generated-output refreshes without an explicit reason.
3. Update source definitions before generated outputs.
4. Preserve configuration migration paths for existing users.
5. Add or update tests for behavioural changes.
6. Update the audit-remediation register when a finding changes state.
7. Update roadmap evidence and exit criteria when a phase advances.

Before publishing:

1. Review the complete diff.
2. Confirm that no unrelated files are included.
3. Run the applicable validation matrix.
4. State which checks were run, skipped, or blocked.
5. Never call a skipped check `PASS`.
6. Use a draft pull request for incomplete migration work.

## Branch and commit policy

- Default development branches use `agent/<short-description>` or another clearly scoped project branch.
- Do not commit directly to `master` unless the project owner explicitly requests it.
- Keep commit messages terse and descriptive.
- Prefer one conceptual change per commit or a small, reviewable sequence of commits.
- Do not rewrite published history, force-push shared branches, or delete tags without explicit authorization.

## Repository layout

Keep the repository root limited to files that are genuinely project-wide entry points.

Expected root-level documents include:

- `README.md`
- `AGENTS.md`
- `LICENSE`
- dependency and build entry points
- launcher and application entry points

Project documentation belongs under `doc/`:

- `doc/migrations/` — completed or historical migrations
- `doc/roadmap/` — active plans, milestones, and remediation tracking
- `doc/audits/` — durable audit reports when added to the repository
- `doc/README.assets/` — README media already used by the project

Do not add a new root-level Markdown file for every work package. Extend an existing indexed document or add it under the correct `doc/` subdirectory.

## Documentation rules

Every documentation directory must have a `README.md` index when it contains multiple documents.

Documentation must distinguish among:

- confirmed behaviour
- intended behaviour
- unverified assumptions
- blocked validation
- historical evidence

Use exact commands, versions, paths, and commit identifiers where available.

Do not claim full validation when only static checks, imports, or unit tests were run. Real-device or emulator behaviour must be labelled separately.

## Source-of-truth rules

Generated files must not be edited as if they were canonical sources.

Known generated outputs include, but are not limited to:

- `module/config/argument/args.json`
- `module/config/config_generated.py`
- `module/config/i18n/*.json`
- `module/**/assets.py`

Before changing generated output:

1. Locate the source definition or generator.
2. Change the source.
3. Run the narrow generator intentionally.
4. Review generated drift.
5. Commit source and generated output together when both are required.

If a generator is not safe or available, document the blocked regeneration instead of hand-editing large generated files silently.

## Vendored and external code

Directories under `submodule/` are vendored content, not necessarily active Git submodules.

Before editing vendored code:

1. Determine whether the fork owns the code or mirrors another project.
2. Record the upstream source and current revision if known.
3. Prefer an adapter or isolated patch over a broad rewrite.
4. Do not apply repository-wide formatting to vendored trees.

The separately distributed `toolkit/` is not assumed reproducible from this repository until the packaging roadmap proves otherwise.

## Python 3.14 migration rules

The migration is incremental. Do not change the declared runtime to Python 3.14 until the acceptance checks for the corresponding roadmap milestone are satisfied.

Required principles:

1. Establish a reproducible baseline before upgrading dependencies.
2. Inventory imports of removed or deprecated standard-library APIs.
3. Introduce `pyproject.toml` and explicit `requires-python` deliberately.
4. Separate runtime dependencies from development, test, build, and packaging dependencies.
5. Prefer maintained packages with CPython 3.14 wheels for Windows x86-64.
6. Avoid relying on source builds for normal end-user installation.
7. Upgrade high-risk native dependencies in isolated work packages.
8. Replace MXNet-based OCR through an explicit backend abstraction and regression corpus.
9. Keep the standard GIL build as the supported target until native extensions and concurrency behaviour are validated.
10. Record compatibility shims and remove them only after all call sites migrate.

## OCR rules

OCR behaviour is core application functionality.

Do not replace the OCR stack based only on installation success. A replacement must be validated against representative EN-client screenshots covering at least:

- resource counters
- timers
- levels
- research values
- shop values
- commission durations
- combat counters
- Operation Siren screens
- server and login-related text where applicable

Any OCR migration must track:

- model format
- preprocessing
- character set
- confidence/selection logic
- latency
- packaged size
- false-positive and false-negative regressions

MXNet is considered a migration blocker, not a permanent Python 3.14 dependency target.

## Device and ADB safety

ADB, emulator, and device operations can modify external state.

Never run device-affecting commands unless the task explicitly authorizes them and a test device is clearly identified.

Potentially destructive or stateful operations include:

- installing or uninstalling APKs
- replacing ADB binaries
- starting, stopping, or restarting applications
- changing device settings
- clearing application data
- connecting to arbitrary ADB endpoints
- invoking MaaTouch/minitouch/uiautomator2 setup
- running live combat or scheduler tasks

For ordinary repository work, use mocks, fixtures, static analysis, and isolated unit tests. Mark real-device checks as manual or blocked when no authorized test target exists.

## Updater and Git safety

The application updater is a high-risk subsystem.

Required properties:

1. The default repository must point to this fork or updates must be disabled by default.
2. No updater path may silently reset the checkout to `LmeSzinc/AzurLaneAutoScript` or another repository.
3. Destructive Git operations such as `reset --hard`, forced checkout, and cleaning untracked files require explicit design review and user-facing safeguards.
4. Local modifications must not be destroyed without a clear warning and confirmation policy.
5. Updater tests must use disposable repositories or mocks, never the contributor's working checkout.

Do not run the current updater during routine validation until the containment roadmap phase is completed.

## GUI and network safety

- Development and default GUI binding should prefer loopback (`127.0.0.1`) rather than all interfaces.
- Binding to `0.0.0.0` requires an explicit user choice and documented authentication requirements.
- Authentication-disabled states must be visible and intentional.
- Do not add new telemetry, upload services, remote-control endpoints, or external health checks without explicit approval.
- External endpoints must have a documented purpose, timeout, failure mode, privacy impact, and disable path.

## Electron and webapp safety

The Electron wrapper must move toward:

- `contextIsolation: true`
- `nodeIntegration: false`
- a minimal, reviewed preload bridge
- reproducible lockfile state
- dependency versions consistent with `package.json`

Do not expose arbitrary Node.js APIs to renderer content.

When changing webapp dependencies, update and validate both `package.json` and its lockfile in the same work package.

## Validation matrix

Choose checks based on the affected surface.

### Documentation-only changes

- link/path review
- Markdown structure review
- verify moved files remain reachable from an index

### Python source changes

- targeted unit tests
- import/compile check for affected packages
- static analysis configured by the project
- configuration migration tests where applicable

### Generated configuration/assets

- source-definition review
- generator execution
- generated-drift review
- import checks for generated modules

### Dependency changes

- clean environment installation
- import smoke tests
- Windows wheel availability review
- lock/constraint drift review
- targeted runtime tests

### OCR changes

- deterministic fixture corpus
- accuracy comparison against the accepted baseline
- latency and packaged-size measurements
- representative EN-client manual smoke test when authorized

### Device-layer changes

- mock/unit tests first
- disposable emulator/device integration test only when explicitly authorized
- package detection and app lifecycle checks
- screenshot, hierarchy, click, swipe, reconnect, and error recovery checks as applicable

### Packaging and installer changes

- clean-machine or clean-VM installation
- offline/limited-network behaviour where supported
- launcher, bundled Python, ADB, native libraries, and webapp startup
- update and rollback behaviour

### Webapp/Electron changes

- dependency installation from the lockfile
- lint
- typecheck
- tests
- production build
- Electron launch smoke test where available
- security-setting verification

## Test result language

Use the following result vocabulary:

- `PASS` — the check ran and met its acceptance criteria.
- `FAIL` — the check ran and did not meet its acceptance criteria.
- `BLOCKED` — the check could not run because a required environment, device, dependency, credential, or artifact was unavailable.
- `SKIPPED` — intentionally not run and not required for the current scope.
- `UNKNOWN` — insufficient evidence exists to classify the result.

A baseline failure is not a pass. Record it as an existing failure with evidence.

## Forbidden shortcuts

Do not:

- reintroduce CN, JP, or TW runtime support accidentally through upstream merges
- reintroduce AzurStats or another upload service as a replacement
- edit only generated files while ignoring their sources
- mark tests as passing when they were skipped or unavailable
- run the updater against a contributor checkout
- run ADB/device operations without explicit authorization
- replace dependency pins blindly with the newest versions in one change
- delete historically named campaign/OCR content solely by filename
- add additional root-level migration reports without indexing them under `doc/`
- merge, release, publish packages, or rewrite history without explicit authorization

## Audit remediation tracking

Every audit finding must have one of these states in `doc/roadmap/audit-remediation-register.md`:

- `OPEN`
- `IN_PROGRESS`
- `BLOCKED`
- `MITIGATED`
- `CLOSED`
- `ACCEPTED_RISK`

Closing a finding requires:

1. a linked change or commit
2. validation evidence
3. updated documentation
4. confirmation that no EN-only or no-AzurStats invariant regressed

## Definition of done

A work package is complete only when:

- the intended behaviour is implemented
- relevant tests pass or limitations are explicitly documented
- generated outputs are synchronized where applicable
- documentation and audit tracking are updated
- repository invariants remain true
- the diff is reviewable and contains no unrelated cleanup

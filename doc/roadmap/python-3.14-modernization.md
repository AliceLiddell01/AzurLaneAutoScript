# Python 3.14.6 modernization and audit-remediation roadmap

## 1. Mission

Modernize the EN-only AzurLaneAutoScript fork from its legacy Python/toolkit stack to a reproducible **CPython 3.14.6 Windows x86-64** application while progressively remediating every confirmed repository-audit finding.

The programme must preserve:

- Azur Lane Global / EN-only runtime support
- Android package `com.YoStarEN.AzurLane`
- English-only GUI and documentation scope unless explicitly changed
- no AzurStats integration or replacement upload service
- configuration migration for existing users
- historical licensing, attribution, and contributor history
- functional OCR, scheduler, combat, campaign, and device-control behaviour

The migration is not complete when the source merely imports on Python 3.14. It is complete only when the supported application can be installed, launched, connected to an authorized EN test client, and validated through a reproducible release process.

## 2. Target state

### Runtime

- CPython `3.14.6`
- Windows x86-64 standard GIL-enabled build
- explicit `requires-python = ">=3.14,<3.15"` when the runtime milestone is ready
- no dependency on MXNet
- maintained native dependencies with published CPython 3.14 Windows wheels

### Dependency management

- canonical `pyproject.toml`
- separated runtime, test, lint, build, packaging, and optional dependency groups
- reproducible lock or constraints strategy
- clean-environment installation validation
- dependency provenance and license inventory

### Architecture

- explicit OCR backend interface
- maintained ONNX Runtime or another approved backend for packaged inference
- isolated device/ADB adapters with mockable boundaries
- safe updater with fork-owned defaults and non-destructive behaviour
- loopback-first GUI/network defaults
- hardened Electron renderer boundary

### Delivery

- reproducible Windows toolkit/application build
- documented artifact inputs and checksums
- clean-VM installation test
- automated CI plus authorized EN-device smoke validation
- fork-owned installation and troubleshooting documentation

## 3. Non-goals for the initial migration

The following are explicitly outside the first Python 3.14 release candidate:

- free-threaded CPython as the default runtime
- experimental CPython JIT as a production requirement
- restoration of CN, JP, or TW client support
- restoration of AzurStats or introduction of replacement telemetry
- broad redesign of game automation algorithms unrelated to compatibility or audit remediation
- mobile platforms other than the existing Android/emulator control model
- uncontrolled dependency upgrades solely to obtain newest versions

## 4. Programme principles

1. **Contain risk before modernization.** Fix updater/repository-target hazards before running deployment tooling.
2. **Measure the legacy baseline before changing it.** A failing baseline must be recorded, not renamed as success.
3. **Upgrade in dependency groups.** Native and framework dependencies move in isolated work packages.
4. **Keep behavioural seams.** Introduce adapters before replacing OCR, ADB, updater, and external-service implementations.
5. **Prefer wheels over source builds.** Normal Windows installation must not require a compiler toolchain.
6. **Keep generated files traceable.** Modify sources, regenerate intentionally, review drift.
7. **Treat real-device tests as controlled integration tests.** Never use an unknown personal device or contributor checkout as a disposable target.
8. **Close audit findings with evidence.** Documentation alone may mitigate a finding but does not close runtime risk.
9. **Preserve EN-only constraints continuously.** Upstream merges and generated outputs must be scanned for regional-runtime regressions.
10. **Build a release, not only a development environment.** The bundled toolkit and launcher are part of the product.

## 5. Dependency graph

The programme follows this dependency order:

```text
M0 Governance and containment
 └─> M1 Reproducible legacy baseline
      └─> M2 Compatibility and dependency inventory
           ├─> M3 Python 3.14 installable core
           │    └─> M4 Modern core dependency stack
           │         ├─> M5 OCR replacement
           │         ├─> M6 ADB/device modernization
           │         └─> M7 GUI/webapp/network hardening
           └──────────────────────────────┐
                                          v
                               M8 Packaging and updater
                                          v
                               M9 Full validation matrix
                                          v
                               M10 Python 3.14.6 RC
```

M5, M6, and M7 may progress in parallel after M4 establishes a stable shared dependency baseline. M8 cannot close until all packaged runtime surfaces are known.

## 6. Milestone M0 — governance and immediate containment

### Objective

Make the repository safe to work on and establish one canonical planning/documentation structure.

### Work packages

#### WP0.1 — repository governance

- Add root `AGENTS.md`.
- Define EN-only/no-AzurStats invariants.
- Define generated, vendored, device, updater, and validation rules.
- Add documentation placement rules.

#### WP0.2 — documentation cleanup

- Move root EN-only migration reports to `doc/migrations/en-only/`.
- Add a migration index describing historical versus active documentation.
- Add `doc/README.md`.
- Add `doc/roadmap/` and this master roadmap.
- Keep root limited to project-wide entry points.

#### WP0.3 — updater containment

- Change deployment defaults away from upstream `LmeSzinc/AzurLaneAutoScript`.
- Disable automatic update by default until updater behaviour is redesigned and tested.
- Remove or guard destructive reset/pull behaviour.
- Add a hard invariant test preventing upstream repository defaults from returning.

**Status:** IN PROGRESS — implementation and focused local validation are complete
on `agent/updater-containment`; merge review is pending.

**Evidence:**

- Canonical and platform deployment defaults point to the fork with automatic,
  periodic, and scheduled updates disabled.
- Legacy upstream URL forms and `global` migrate to the fork and persist with
  automatic updates disabled; arbitrary custom repositories remain unchanged
  and are denied updater permission.
- All main WebUI updater entry points share one fail-closed guard before
  network, Git, Pip, process-management, or reload operations.
- The update path uses only a clean-checkout, fork-remote, branch-matched
  `fetch` followed by `merge --ff-only`; it does not mutate remotes, remove lock
  files, reset the checkout, or use Git-over-CDN.
- `python -m unittest tests.test_updater_containment -v` passes focused config,
  migration, guard, disposable-Git, WebUI control-flow, and invariant tests.
- Full M8 updater, installer, rollback, release-channel, and reproducible
  packaging reconstruction remains out of scope.

#### WP0.4 — immediate network containment

- Change default GUI bind address to `127.0.0.1`.
- Make remote binding an explicit opt-in.
- Surface authentication-disabled state clearly.

#### WP0.5 — legacy alias cleanup

- Remove or correct StarRailCopilot repository aliases in Windows deployment configuration.
- Scan deployment and updater paths for stale repository targets.

### Audit coverage

- `ALAS-AUDIT-001`
- `ALAS-AUDIT-002`
- `ALAS-AUDIT-003`
- `ALAS-AUDIT-006`
- part of `ALAS-AUDIT-016`

### Exit criteria

- Root `AGENTS.md` exists and is linked from documentation.
- Migration documents are indexed under `doc/`.
- Active roadmap and audit register exist.
- No default update path points to upstream or another project.
- Automatic update is disabled or safely contained by default.
- GUI defaults to loopback.
- Static repository-target and EN-only scans pass.

## 7. Milestone M1 — reproducible legacy baseline

### Objective

Create a truthful, repeatable baseline before Python and dependency upgrades.

### Work packages

#### WP1.1 — environment capture

Record:

- current Python version actually required by the existing toolkit
- current Node/npm versions
- Windows version and architecture
- bundled Git, ADB, FFmpeg, and webapp artifacts
- environment variables and launcher assumptions
- external files absent from Git

#### WP1.2 — test result normalization

Replace ambiguous overall PASS language with per-check results:

- `PASS`
- `FAIL`
- `BLOCKED`
- `SKIPPED`
- `UNKNOWN`

Historical evidence remains historical; it must not be presented as current verification.

#### WP1.3 — root CI baseline

Add pull-request CI for checks that can run without a device:

- Python compile/import checks
- targeted unit tests
- EN-only and no-AzurStats invariant scans
- generated-output drift checks where safe
- webapp immutable install, lint, typecheck, tests, and build
- documentation path/link checks

Known baseline failures should be represented as explicit failing or quarantined checks with an owner and removal plan.

#### WP1.4 — webapp lockfile repair

- Reconcile `package.json` and `package-lock.json`.
- Regenerate the lockfile from the declared dependency graph.
- Verify clean immutable installation.
- Record dependency and build outputs.

#### WP1.5 — dead runtime path cleanup

- Remove or replace stale `azur_lane_uncensored()` code.
- Search for other imports of removed EN-only migration modules.
- Add regression tests for task discovery and dispatch.

#### WP1.6 — residual classification refresh

- Re-run the residual scan.
- Classify legacy `_cn` and `_tw` paths using runtime-reference evidence.
- Maintain an explicit allowlist with reasons.
- Update historical migration documentation without deleting shared map/OCR content by name alone.

### Audit coverage

- `ALAS-AUDIT-004`
- `ALAS-AUDIT-005`
- `ALAS-AUDIT-007`
- `ALAS-AUDIT-008`
- `ALAS-AUDIT-009`
- part of `ALAS-AUDIT-016`

### Exit criteria

- A clean checkout can run the documented baseline checks.
- Every check reports a truthful state.
- CI is active on pull requests.
- Webapp dependency state is reproducible.
- Dead removed-module entry points are gone.
- Residual-path allowlist is evidence-based.

## 8. Milestone M2 — Python 3.14 compatibility and dependency inventory

### Objective

Produce a complete migration inventory before changing the runtime contract.

### Work packages

#### WP2.1 — import and standard-library audit

Scan handwritten and vendored code for APIs removed or changed between the legacy runtime and Python 3.14, including:

- `distutils`
- `imp`
- `cgi` / `cgitb`
- `imghdr`
- `asyncore` / `asynchat`
- `telnetlib`
- deprecated importlib, asyncio, collections, inspect, typing, and pathlib patterns
- syntax and warning changes exposed by Python 3.14

Classify each match as runtime, tooling, vendored, unreachable, or generated.

#### WP2.2 — dependency ownership inventory

For every dependency, record:

- current pin and import locations
- runtime versus development role
- direct versus transitive status
- native-extension status
- Windows CPython 3.14 wheel availability
- license
- maintenance status
- known API breakage
- target version or replacement
- validation owner

#### WP2.3 — native dependency matrix

Prioritize:

- NumPy
- SciPy
- OpenCV
- Pillow
- lxml
- PyAV / FFmpeg
- cryptography-related dependencies
- ONNX Runtime or approved OCR backend
- adbutils
- uiautomator2

No package is approved merely because `pip install` succeeds.

#### WP2.4 — packaging design decision

Choose and document:

- `pyproject.toml` build backend
- dependency group format
- lock/constraints tool
- Windows artifact cache policy
- source-build policy
- version update process
- SBOM/checksum generation approach

#### WP2.5 — OCR migration design

Document the current OCR call graph, model files, preprocessing, alphabets, and result-selection behaviour.

Select one migration path:

1. ONNX Runtime backend with converted or replacement models — preferred target.
2. Modern CnOCR/PyTorch backend — acceptable only with packaged-size and accuracy justification.
3. Temporary legacy OCR sidecar — transitional only and must have a removal milestone.

### Exit criteria

- Every direct dependency has an owner and target disposition.
- Every native dependency has a Python 3.14 Windows wheel assessment.
- Removed-standard-library matches are classified.
- Packaging strategy is approved.
- OCR backend decision and regression-corpus plan are documented.

## 9. Milestone M3 — Python 3.14 installable core

### Objective

Make the non-device, non-OCR application core importable and testable on CPython 3.14.6.

### Work packages

#### WP3.1 — introduce project metadata

Add `pyproject.toml` with:

- project metadata
- provisional Python 3.14 runtime declaration on the migration branch
- separated dependency groups
- test/lint/type configuration where appropriate

Keep legacy requirement files temporarily only when they are required for transition or historical toolkit compatibility. Mark the canonical source explicitly.

#### WP3.2 — compatibility patches

- Replace removed standard-library APIs.
- Fix changed exception, coroutine, import, inspection, and path semantics.
- Remove obsolete Python 2/early Python 3 compatibility branches where proven unreachable.
- Avoid unrelated stylistic rewrites.

#### WP3.3 — configuration core

Validate:

- config loading
- option migration
- generated configuration imports
- scheduler task discovery
- EN package validation
- no-AzurStats migration behaviour

#### WP3.4 — Python 3.14 CI lane

Run:

- clean dependency installation
- compile/import checks
- unit tests not requiring native OCR/device access
- configuration generation/drift checks
- EN-only scans

### Exit criteria

- CPython 3.14.6 can install the approved core dependency set on Windows x86-64.
- Core packages import without unsupported compatibility shims.
- Core test suite passes or has explicitly owned non-runtime quarantines.
- Python 3.14 CI is required for migration pull requests.

## 10. Milestone M4 — modern core dependency stack

### Objective

Replace obsolete dependency pins while keeping behaviour reviewable.

### Upgrade groups

#### Group A — low-risk utilities

Update logging, serialization, request, date/time, CLI, and helper packages first.

Acceptance:

- import smoke tests
- targeted utility tests
- no new network behaviour

#### Group B — validation/config/web framework

Modernize Pydantic and related web/config libraries.

Strategy:

- use a temporary Pydantic V1 compatibility namespace when necessary
- migrate models incrementally to supported APIs
- add serialization and validation regression fixtures

#### Group C — image and numeric stack

Modernize NumPy, SciPy, OpenCV, Pillow, imageio, and lxml.

Acceptance:

- representative image transformations
- template matching
- color/range calculations
- geometry and map-detection tests
- no silent dtype or overflow regressions

#### Group D — video/native I/O

Modernize PyAV and FFmpeg integration.

Acceptance:

- screenshot/video decode fixtures
- packaged native library discovery
- Windows clean-environment test

### Exit criteria

- No approved runtime dependency is pinned to an unsupported legacy release solely for compatibility inertia.
- All native runtime dependencies install from approved Windows wheels or packaged artifacts.
- Numerical/image regression suite passes.
- Dependency lock/constraints are reproducible.

## 11. Milestone M5 — OCR backend replacement

### Objective

Remove MXNet/CnOCR 1.x as a blocker while preserving or improving EN-client recognition.

### Work packages

#### WP5.1 — OCR interface extraction

Create an internal backend contract covering:

- model loading
- preprocessing
- alphabet/character-set selection
- line and region recognition
- confidence/result selection
- batch behaviour
- device/provider selection

Keep calling code independent from ONNX Runtime, PyTorch, or a specific OCR library.

#### WP5.2 — regression corpus

Build a versioned corpus of authorized EN-client screenshots and expected outputs for:

- resource counters
- currencies
- timers
- levels
- research projects
- shops
- commissions
- combat counters
- Operation Siren
- login/server text where used

Include hard negatives and visually ambiguous cases.

#### WP5.3 — backend implementation

Preferred implementation:

- ONNX Runtime CPU backend
- explicit model and vocabulary versioning
- deterministic preprocessing
- packaged model checksums

#### WP5.4 — comparative validation

Compare legacy and new backends on:

- exact-match accuracy
- task-level success rate
- false-positive/false-negative rate
- latency
- memory
- package size
- startup/model-load time

#### WP5.5 — legacy removal

Remove MXNet and CnOCR 1.x only after the replacement passes accepted thresholds and authorized EN-device smoke tests.

### Exit criteria

- No MXNet runtime dependency.
- OCR fixtures pass accepted accuracy thresholds.
- Backend is packaged reproducibly.
- EN-client manual smoke confirms representative tasks.

## 12. Milestone M6 — ADB and device-layer modernization

### Objective

Update adbutils/uiautomator2 and device control without unsafe installation or hidden external-state changes.

### Work packages

#### WP6.1 — adapter inventory

Map:

- device discovery
- package detection
- connection and reconnect
- app start/stop/restart
- screenshots
- hierarchy dump
- click/swipe
- MaaTouch/minitouch
- emulator-specific paths
- ADB replacement and installation logic

#### WP6.2 — safe defaults

- Do not replace ADB automatically by default.
- Do not auto-connect to arbitrary endpoints without visible configuration.
- Do not install uiautomator2 components without explicit user action.
- Add plan/dry-run output for installer actions where practical.

#### WP6.3 — dependency/API migration

Update adbutils and uiautomator2 behind adapters, preserving existing exception translation and retry semantics intentionally.

#### WP6.4 — test matrix

Automated:

- mocked ADB protocol tests
- command construction
- package filtering
- timeout/retry behaviour
- error classification

Authorized integration:

- one documented supported emulator first
- discovery and connection
- EN package detection
- lifecycle
- screenshot/hierarchy
- click/swipe
- reconnect

Expand emulator coverage only after the first matrix is stable.

### Exit criteria

- Modern Python 3.14-capable device dependencies.
- Safe installer/device defaults.
- Mock suite passes.
- At least one authorized emulator integration path passes.

## 13. Milestone M7 — GUI, webapp, Electron, and network hardening

### Objective

Resolve exposed-network and renderer risks and make the webapp reproducible.

### Work packages

#### WP7.1 — GUI binding/authentication

- Loopback default.
- Explicit remote-bind configuration.
- Visible unauthenticated warning.
- Authentication tests.

#### WP7.2 — Electron isolation

Move toward:

- `contextIsolation: true`
- `nodeIntegration: false`
- minimal preload API
- validated navigation policy
- no arbitrary Node.js access from renderer content

#### WP7.3 — external endpoint review

For each external request, document:

- endpoint owner
- data sent
- timeout
- retry/failure behaviour
- privacy impact
- disable path

Remove the external server checker if it is not required for core operation or cannot meet the policy.

#### WP7.4 — webapp build contract

- immutable dependency installation
- lint/typecheck/test/build
- Electron launch smoke
- production asset verification

### Audit coverage

- `ALAS-AUDIT-002`
- `ALAS-AUDIT-005`
- `ALAS-AUDIT-010`
- `ALAS-AUDIT-013`

### Exit criteria

- Renderer isolation enabled.
- Loopback-first behaviour verified.
- External endpoints reviewed and controlled.
- Reproducible webapp/Electron build passes.

## 14. Milestone M8 — updater, installer, and reproducible packaging

### Objective

Reconstruct the distributable product around Python 3.14.6.

### Work packages

#### WP8.1 — fork-safe updater redesign

Required behaviour:

- fork-owned repository default
- automatic updates opt-in until proven safe
- no silent destructive reset
- local modification detection
- explicit update plan
- rollback or recovery guidance
- disposable-repository test suite

#### WP8.2 — artifact inventory

Identify and version:

- CPython runtime
- pip/bootstrap components
- Git
- ADB
- FFmpeg/native libraries
- OCR models
- webapp/Electron executable
- launcher scripts
- configuration templates

#### WP8.3 — reproducible build pipeline

Produce artifacts from documented inputs with:

- pinned versions
- checksums
- build scripts
- license notices
- SBOM where practical
- clean output directory
- deterministic naming/version metadata

#### WP8.4 — clean-machine validation

Validate in a clean Windows VM:

- installation/extraction
- launcher
- bundled Python
- dependency imports
- GUI startup
- webapp/Electron startup
- ADB discovery without hidden mutation
- update disabled/safe by default
- log and diagnostic collection

#### WP8.5 — fork-owned installation guide

Replace reliance on upstream installation instructions with documentation matching the actual fork package and updater behaviour.

### Audit coverage

- `ALAS-AUDIT-001`
- `ALAS-AUDIT-006`
- `ALAS-AUDIT-011`
- `ALAS-AUDIT-012`
- `ALAS-AUDIT-015`

### Exit criteria

- Complete package is reproducible from documented inputs.
- Clean VM installation and launch pass.
- Updater cannot silently change repository ownership or destroy local state.
- Fork-owned installation guide is validated.

## 15. Milestone M9 — full validation matrix

### Objective

Prove the product, not only individual libraries.

### Automated matrix

- Python 3.14.6 clean install
- compile/import
- unit tests
- configuration migration
- generated drift
- EN-only/no-AzurStats scans
- OCR corpus
- numerical/image fixtures
- device mocks
- updater disposable-repository tests
- webapp/Electron checks
- packaging verification

### Authorized EN-client matrix

At minimum:

- login/start screen detection
- package start/stop/restart
- screenshot and hierarchy
- one scheduler cycle
- representative reward/daily task
- representative campaign/combat path
- OCR counters/timers
- reconnect/error capture
- local DropRecorder save mode
- proof that no upload occurs

### Result reporting

Every check records:

- environment
- commit
- command/procedure
- result state
- output/log path
- known limitation

### Exit criteria

- No P0/P1 finding remains open unless explicitly accepted by the owner.
- Authorized EN-client smoke passes.
- Blocked checks are resolved or explicitly accepted.
- Release evidence is reviewable and reproducible.

## 16. Milestone M10 — Python 3.14.6 release candidate

### Objective

Produce the first release candidate that meets the target state.

### Release-candidate gate

- CPython 3.14.6 Windows x86-64 standard build
- no MXNet
- reproducible dependency and toolkit build
- fork-safe updater
- safe GUI/network defaults
- hardened Electron boundary
- modernized device stack
- complete audit register
- clean CI
- authorized EN-client evidence
- fork-owned installation documentation
- rollback and known-issues documentation

### Post-RC work

Only after M10:

- evaluate free-threaded CPython experimentally
- evaluate JIT experimentally
- broaden emulator matrix
- improve performance and startup time
- reduce package size
- remove remaining temporary compatibility shims

## 17. Work-package sizing rules

A pull request should normally address one of:

- one containment issue
- one dependency group
- one architectural seam
- one validation surface
- one documentation reorganization

Avoid a single pull request that simultaneously:

- changes Python version
- replaces OCR
- updates ADB
- rewrites packaging
- regenerates all assets/configuration
- reformats unrelated code

Large generated diffs must be isolated and explained.

## 18. Definition of programme completion

The Python 3.14 programme is complete when:

1. The application ships with CPython 3.14.6 on Windows x86-64.
2. A clean machine can reproduce and launch the packaged application.
3. All required runtime dependencies support the target interpreter.
4. MXNet is removed from the supported runtime.
5. OCR accuracy is validated against an EN corpus and authorized device smoke.
6. ADB/device operations use maintained dependencies and safe defaults.
7. Updater and installer cannot silently redirect or destroy user state.
8. GUI and Electron security defaults are hardened.
9. CI and release validation are truthful and repeatable.
10. Every audit finding is closed, mitigated, blocked with owner approval, or explicitly accepted as risk.
11. EN-only and no-AzurStats invariants remain verified.

## 19. Primary technical references

The roadmap is informed by current official project documentation and package metadata:

- Python 3.14 documentation and porting notes: <https://docs.python.org/3.14/whatsnew/3.14.html>
- Removed standard-library modules in Python 3.14: <https://docs.python.org/3.14/library/removed.html>
- Free-threaded Python considerations: <https://docs.python.org/3.14/howto/free-threading-python.html>
- Python Packaging User Guide — `pyproject.toml`: <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>
- Dependency Groups specification: <https://packaging.python.org/en/latest/specifications/dependency-groups/>
- ONNX Runtime package metadata: <https://pypi.org/project/onnxruntime/>
- PyTorch package metadata for optional OCR evaluation: <https://pypi.org/project/torch/>

Package versions must be reverified when each dependency work package begins. This roadmap records the architecture and sequence, not permanent version pins.

# EN-only validation report

> Historical record: these results describe the migration environment recorded at the time. They are not current branch validation. Skipped or unavailable checks are not considered successful by the active roadmap.

Overall result recorded by the migration: **PASS**

| Check | Command | Exit | Recorded result |
|---|---|---:|---|
| Compile/import check | `python -m compileall -q alas.py gui.py module deploy dev_tools campaign submodule tests` | 0 | PASS |
| EN-only unit tests | `python -m unittest discover -s tests -v` | 0 | PASS |
| Config regeneration drift check | `python -m module.config.config_updater` | 0 | PASS |
| Generated asset imports | import all generated `module/**/assets.py` modules | 0 | PASS |
| Webapp checks | `npm scripts` | 125 | SKIPPED |
| Residual removed-support scan | internal scanner | 0 | PASS |

## Generated asset imports

The historical import check covered:

```text
module.ui.assets
module.handler.assets
module.meowfficer.assets
module.combat_ui.assets
module.gacha.assets
module.raid.assets
module.reward.assets
module.campaign.assets
module.exercise.assets
module.os.assets
module.equipment.assets
module.hard.assets
module.statistics.assets
module.guild.assets
module.sos.assets
module.shipyard.assets
module.os_shop.assets
module.event_hospital.assets
module.minigame.assets
module.storage.assets
module.combat.assets
module.daily.assets
module.research.assets
module.war_archives.assets
module.event.assets
module.os_combat.assets
module.shop.assets
module.ui_white.assets
module.tactical.assets
module.coalition.assets
module.meta_reward.assets
module.os_ash.assets
module.retire.assets
module.commission.assets
module.template.assets
module.os_handler.assets
module.dorm.assets
module.awaken.assets
module.eventstory.assets
module.freebies.assets
module.map.assets
module.private_quarters.assets
```

## Scope limitations

- No real emulator/device was attached, so visual login, package start/stop/restart, OCR screenshots, and end-to-end task smoke tests require manual EN-client validation.
- The GitHub Wiki and already published Releases are separate/historical surfaces and were not rewritten.
- Webapp checks were skipped because dependency installation was unavailable in the audit snapshot.
- AzurStats network upload is intentionally unsupported; local drop-image saving was validated separately.

## Captured output for skipped checks

### Webapp checks

```text
Skipped: node_modules is not present in the repository snapshot.
```

## Reproducible runner baseline

- Fork baseline: `5e0453a6349c273efb558fc583da55e11f938248`
- Upstream baseline: `5e0453a6349c273efb558fc583da55e11f938248`
- Python: `3.10.20`
- Node: `v16.20.2`
- npm: `8.19.4`

## Webapp baseline comparison

| Check | Baseline exit | Post-migration exit | Historical classification |
|---|---:|---:|---|
| lint | 1 | 1 | BASELINE FAILURE (not introduced by migration) |
| typecheck | 0 | 0 | PASS |
| test | 1 | 1 | BASELINE FAILURE (not introduced by migration) |
| build | 0 | 0 | PASS |

## Active interpretation

Under the current repository policy:

- the webapp check is `SKIPPED`, not `PASS`;
- real-device validation is `BLOCKED` until an authorized EN test target is available;
- historical baseline failures remain failures requiring ownership and remediation;
- current validation must be rerun on the branch being released.
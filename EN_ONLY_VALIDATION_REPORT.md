# EN-only validation report

Overall result: **PASS**

| Check | Command | Exit | Result |
|---|---|---:|---|
| Compile/import check | `python -m compileall -q alas.py gui.py module deploy dev_tools campaign submodule tests` | 0 | PASS |
| EN-only unit tests | `python -m unittest discover -s tests -v` | 0 | PASS |
| Config regeneration drift check | `python -m module.config.config_updater` | 0 | PASS |
| Generated asset imports | `python -c import module.ui.assets
import module.handler.assets
import module.meowfficer.assets
import module.combat_ui.assets
import module.gacha.assets
import module.raid.assets
import module.reward.assets
import module.campaign.assets
import module.exercise.assets
import module.os.assets
import module.equipment.assets
import module.hard.assets
import module.statistics.assets
import module.guild.assets
import module.sos.assets
import module.shipyard.assets
import module.os_shop.assets
import module.event_hospital.assets
import module.minigame.assets
import module.storage.assets
import module.combat.assets
import module.daily.assets
import module.research.assets
import module.war_archives.assets
import module.event.assets
import module.os_combat.assets
import module.shop.assets
import module.ui_white.assets
import module.tactical.assets
import module.coalition.assets
import module.meta_reward.assets
import module.os_ash.assets
import module.retire.assets
import module.commission.assets
import module.template.assets
import module.os_handler.assets
import module.dorm.assets
import module.awaken.assets
import module.eventstory.assets
import module.freebies.assets
import module.map.assets
import module.private_quarters.assets` | 0 | PASS |
| Webapp checks | `npm scripts` | 125 | SKIPPED |
| Residual removed-support scan | internal scanner | 0 | PASS |

## Scope limitations

- No real emulator/device was attached, so visual login, package start/stop/restart, OCR screenshots, and end-to-end task smoke tests require manual EN-client validation.
- The GitHub Wiki and already published Releases are separate/historical surfaces and were not rewritten.
- Webapp checks are marked skipped when dependency installation is unavailable in the audit snapshot.
- AzurStats network upload is intentionally unsupported; local drop-image saving is validated separately.

## Captured output for failed or skipped checks

### Webapp checks

```text

Skipped: node_modules is not present in the repository snapshot.
```


## Reproducible runner baseline

- Fork baseline: 5e0453a6349c273efb558fc583da55e11f938248
- Upstream baseline: 5e0453a6349c273efb558fc583da55e11f938248
- Python: Python 3.10.20
- Node: v16.20.2
- npm: 8.19.4

## Webapp baseline comparison

| Check | Baseline exit | Post-migration exit | Classification |
|---|---:|---:|---|
| lint | 1 | 1 | BASELINE FAILURE (not introduced by migration) |
| typecheck | 0 | 0 | PASS |
| test | 1 | 1 | BASELINE FAILURE (not introduced by migration) |
| build | 0 | 0 | PASS |

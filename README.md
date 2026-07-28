# AzurLaneAutoScript — EN-only fork

This fork of **AzurLaneAutoScript (Alas)** supports only the **Azur Lane Global / EN client**.

- Server: **EN / Global**
- Android package: `com.YoStarEN.AzurLane`
- Documentation language: **English**
- GUI language: **English**

CN mainland/channel clients, JP, and TW clients are intentionally unsupported. Existing configurations that select a removed client are migrated to `auto`; startup then accepts only the EN package and fails with a clear EN-only error when only an unsupported client is installed.

Alas is free and open-source software. This fork is based on the upstream project by LmeSzinc and contributors. Upstream project: `LmeSzinc/AzurLaneAutoScript`.

![GUI](doc/README.assets/gui_en.png)

## Features

- **Farm:** main chapters, events, raids, affinity/gem farming, and leveling stages.
- **Rewards:** commissions, Tactical Class, Research, Dorm, Meowfficers, Guild, missions, shops, Shipyard, and daily build.
- **Daily:** Daily Raid, Hard Mode, Exercises, event daily stages, raids, and War Archives.
- **Operation Siren:** daily missions, monthly exploration, port shops, hidden zones, Abyssal zones, and Strongholds.
- **Scheduler:** independent tasks are coordinated automatically around their next completion or reset time.
- **Morale control:** delays sorties when needed to protect morale and preserve the experience bonus.

## Installation

1. Install the **Azur Lane Global** Android client with package `com.YoStarEN.AzurLane`.
2. Follow the upstream English installation guide: `https://github.com/LmeSzinc/AzurLaneAutoScript/wiki/Installation_en`.
3. In Alas, leave `Emulator.PackageName` on `auto` or explicitly select `com.YoStarEN.AzurLane`.
4. Configure an emulator/device resolution and controls supported by Alas.

This fork does not provide CN mirrors, CN installers, JP/TW APK helpers, or localized update channels.

## Correctly using the scheduler

Each task runs independently and is coordinated by a central scheduler. When a task finishes, Alas calculates its next run time. For example, a four-hour Research project postpones the Research task until the project can be collected.

Enable the tasks that are useful to you and let the scheduler coordinate them. Repeatedly starting and stopping only one or two tasks defeats the scheduler's purpose.

Morale control is preventive: it can wait before a warning appears so ships remain above the desired morale threshold while other tasks continue.

## Required in-game settings

| Setting | Value |
|---|---|
| Frame Rate | 60 FPS |
| Operation Siren: Reduce TB Guidance | On |
| Operation Siren: Auto-use items in Auto Mode | On |
| Operation Siren: Default Auto Mode in Threat Safe | Off |
| Story Autoplay | Enabled |
| Text Auto-scroll Speed | Very Fast |
| Sleep/Standby Mode on Main Menu | Off |
| Duplicate Ship Display | Off |
| Quick-switch confirmation | Off |
| Battle Result Cutscene | Off |

Operation Siren → Navigation Orders → Submarine Support:

| Setting | Value |
|---|---|
| Automatically call submarines | Off |

Remove equipment skins from ships used by automation because they can interfere with image recognition.

## Reporting bugs

Before opening an issue:

1. Update this fork and confirm the problem still occurs on the latest branch revision.
2. Confirm that the installed client is `com.YoStarEN.AzurLane`.
3. Attach the relevant `log/error/<timestamp>/log.txt` and recent screenshots. For unexpected behavior without a captured exception, attach the current day's log and at least one screenshot.
4. Describe the exact task, screen, expected behavior, and observed behavior.

## Known issues

- Network instability and some reconnect popups may still require manual recovery.
- Very slow systems can cause timing and recognition failures; screenshot capture over roughly one second is especially problematic.
- Exercise retreat detection can be late when character art obscures HP bars.
- ADB and `uiautomator2` can occasionally fail because of emulator state; restarting the emulator usually resolves it.
- A swipe can be interpreted as a click when the emulator stalls.

## Development

The map-detection implementation is in `module.map_detection`. Configuration outputs such as `module/config/argument/args.json`, `module/config/config_generated.py`, locale bundles, and `module/**/assets.py` are generated files; edit their source definitions and regenerate them.

Do not submit EN-only cleanup directly to upstream unless upstream explicitly accepts that scope. This fork retains upstream licensing, copyright, contributor history, and attribution.

## Project documentation

- [Repository rules for agents and contributors](AGENTS.md)
- [Documentation index](doc/README.md)
- [Python 3.14.6 modernization roadmap](doc/roadmap/python-3.14-modernization.md)
- [Audit remediation register](doc/roadmap/audit-remediation-register.md)
- [EN-only migration archive](doc/migrations/en-only/README.md)

Active development plans and audit remediation status belong under `doc/roadmap/`. Completed migration records belong under `doc/migrations/` rather than in the repository root.

## Acknowledgements

- EN support: [whoamikyo](https://github.com/whoamikyo) and [nEEtdo0d](https://github.com/nEEtdo0d)
- Historical JP support: [ferina8-14](https://github.com/ferina8-14), [noname94](https://github.com/noname94), and [railzy](https://github.com/railzy)
- Historical TW support: [Zorachristine](https://github.com/Zorachristine)
- GUI development: [18870](https://github.com/18870)
- Upstream maintainers and all contributors preserved in Git history and project licensing

## Contact

- Fork issues: `https://github.com/AliceLiddell01/AzurLaneAutoScript/issues`
- Upstream Discord: `https://discord.gg/AQN6GeJ`

## License

See [`LICENSE`](LICENSE). Historical releases and their descriptions remain part of project history and are not rewritten by this branch.
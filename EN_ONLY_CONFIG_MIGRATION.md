# EN-only configuration migration

## Accepted values

- `Alas.Emulator.PackageName`: `auto` or `com.YoStarEN.AzurLane`
- `Alas.Emulator.ServerName`: `disabled` or one of the generated `en-*` shard entries
- Web UI language: `en-US`
- Drop records: local `do_not` / `save` modes only

## Existing configurations

The normal `ConfigUpdater` option validation migrates removed package, shard, locale, and proxy values to their EN-only defaults. A removed package therefore becomes `auto`; auto-detection then accepts only `com.YoStarEN.AzurLane`.

Known CN/JP/TW package IDs remain only in `UNSUPPORTED_PACKAGE` so startup can emit `Unsupported client: EN-only fork` instead of silently launching another installed client.

## Removed configuration surface

- CN/JP/TW package options and shard lists
- CN reverse proxy selection
- AzurStats upload endpoint, client ID, and upload-capable record modes
- `AzurLaneUncensored` task and repository setting
- CN deploy templates and mirrors
- CN/JP/TW GUI locale selection

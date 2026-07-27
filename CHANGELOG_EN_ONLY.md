# EN-only migration changelog

## Documentation

- Made `README.md` the canonical English README.
- Removed the localized README duplicates and language switcher.
- Preserved upstream and historical localization contributor attribution.
- Added inventory, unique-content, wiki, configuration, asset, validation, and residual-match reports.

## Runtime and configuration

- Restricted server/package conversion to EN Global and `com.YoStarEN.AzurLane`.
- Added explicit rejection diagnostics for known CN/JP/TW packages.
- Removed CN/JP/TW package options, shards, server dispatch overloads, and localized branches.
- Removed the CN-only uncensor task, reverse proxy, mirror/update aliases, and deploy variants.
- Reduced GUI generation and runtime language selection to `en-US`.
- Removed AzurStats upload code, endpoint, client ID, API selector, upload modes, branding, and documentation links.
- Preserved local-only drop screenshots through the neutral `DropRecorder` implementation.

## OCR and assets

- Removed JP/TW-specific OCR model properties and model files.
- Retained the generic `cnocr` model only where EN runtime code still uses it for digits/Latin text; its legacy identifier does not represent a supported CN client.
- Migrated EN-selected fallback templates to `assets/en`, regenerated scalar EN asset definitions, and removed CN/JP/TW asset trees.

## Historical material

Published releases, release descriptions, Git history, contributor names, and the separate GitHub Wiki were not rewritten automatically.

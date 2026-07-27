# AzurStats removal

The fork contains no AzurStats network integration.

## Removed

- upload endpoint and HTTP client
- per-installation AzurStats identifier
- API selector and upload-capable record modes
- AzurStats module/class names and README links
- stale help text pointing users to the service

## Retained

Local screenshot recording remains available through `DropRecorder` with only `do_not` and `save` modes. Existing `save_and_upload` values migrate to `save`; upload-only values migrate to `do_not`.

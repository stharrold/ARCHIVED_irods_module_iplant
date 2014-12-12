# irods_module_iplant

IRODS module for iPlant collaboration. IRODS rules compress data when ingested and decompress data when fetched.

## Description

IRODS icommands call rules from `$IRODS/server/config/reConfigs/core.re` (e.g. `acPreprocForDataObjOpen`), which then call rules from `$IRODS/server/config/reConfigs/iplant.re` (e.g. `iplantPreprocForDataObjOpen`). Rules in `$IRODS/server/config/reConfigs/iplant.re` call `$IRODS/server/bin/cmd/iplant.py` with options specifying the action to be taken on a file. List available options with `$IRODS/server/bin/cmd/iplant.py --help`.

## Installation

See [INSTALL.md](INSTALL.md).

## Testing

See [TESTING.md](TESTING.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

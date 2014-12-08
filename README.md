# irods_module_iplant

IRODS module for iPlant collaboration. IRODS rules compress data when ingested and decompress data when fetched.

## Installation

See [INSTALL.md](INSTALL.md).

## Testing

See [TESTING.md](TESTING.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Example

```
$ ~/irods_module_iplant/iplant/rules/iplant.py --help
usage: iplant.py [-h] --ipath IPATH --iplant IPLANT --action
                 {compress,decompress} --itmp_iplant ITMP_IPLANT --tmp_iplant
                 TMP_IPLANT [--delete_itmp_files] [--delete_tmp_files]
                 [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 [--log_file LOG_FILE] [-t]

Compress or decompress .fastq file in iPlant collection.

optional arguments:
  -h, --help            show this help message and exit
  --ipath IPATH         iRODS path to .fastq file for (de)compression.
  --iplant IPLANT       iRODS path to iplant root directory. Only files within
                        this directory will be (de)compressed.
  --action {compress,decompress}
                        Action to take on the file from `ipath`.
  --itmp_iplant ITMP_IPLANT
                        iRODS path to temporary directory for moving files
                        during (de)compression.
  --tmp_iplant TMP_IPLANT
                        Local path to temporary directory for moving files
                        during (de)compression.
  --delete_itmp_files   Delete iRODS temporary files made during
                        (de)compression.
  --delete_tmp_files    Delete local temporary files made during
                        (de)compression.
  --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Verbosity of logging level. 'DEBUG' is the most
                        verbose; 'CRITICAL' is the least. Default: INFO
  --log_file LOG_FILE   Local path for writing log in addition to stdout. Use
                        to debug while executing module with iRODS icommands.
  -t, --test            Test that module is being called correctly. Checks
                        input then prints message to stdout. No actions are
                        taken.
  ```

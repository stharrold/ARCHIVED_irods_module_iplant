# TESTING

Example tests to complete and check installation.

## Define paths

Define local paths and paths within iRODS.

```bash
REPO=~/irods_module_iplant # Example local directory for cloned git repository.
IRODS=~/iRODS # Example local root directory for iRODS installation.
ITMP_IPLANT=/tempZone/tmp/iplant # Example iRODS directory to save temporary files.
imkdir -p $ITMP_IPLANT # Create iRODS temporary directory.
TMP_IPLANT=/tmp/iplant # Example local directory to save tempoary files.
mkdir -p $TMP_IPLANT # Create local temporary directory.
IPLANT_LOG=/tmp/iplant/iplant.log # Example local path to save iPlant log file.
IPLANT=/tempZone/home/rods/iplant # Example iRODS directory to save iplant data.
```

## Test iRODS temporary directory

Test that iRODS icommands execute in the user-defined iRODS temporary directory. For this test, avoid invoking rules from `$IRODS/server/config/reConfigs/core.re`.

```bash
date
iput $REPO/iplant/test/test1.fastq $ITMP_IPLANT/.
imv $ITMP_IPLANT/test1.fastq $ITMP_IPLANT/test1_moved.fastq
iget $ITMP_IPLANT/test1_moved.fastq /tmp/.
irm -f $ITMP_IPLANT/test1_moved.fastq
rm -f /tmp/test1_moved.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
```

## Test `iplant.py` with command line arguments

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly. For this test, avoid invoking rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. Also see `iplant.py --help` to test additional `iplant.py` options.

```bash
date
iput $REPO/iplant/test/test1.fastq $ITMP_IPLANT/.
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP_IPLANT/test1.fastq --action compress --itmp_iplant $ITMP_IPLANT --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP_IPLANT/test1.fastq --action decompress --itmp_iplant $ITMP_IPLANT --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
irm -f $ITMP_IPLANT/test1.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
# Read `$IPLANT_LOG` between the timestamps from `date` to check execution.
```

## Test `iplant.py` with iRODS icommands

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly when invoked by rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. Also see `iplant.py --help` to test additional `iplant.py` options.

```bash
date
iput $REPO/iplant/test/test1.fastq $IPLANT/.
iget $IPLANT/test1.fastq /tmp/test1_processed.fastq
diff $REPO/iplant/test/test1.fastq /tmp/test1_fromirods.fastq
irm -f $IPLANT/test1.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
# Read `$IPLANT_LOG` between the timestamps from `date` to check execution.
```

## Notes

- `iplant.py` creates parent directories as needed for `--log_file $IPLANT_LOG`. See `iplant.py --help`
- `iplant.py` uses the standard Python library `tempfile.tempdir` to defien the temporary directory from the environment [1]_.

## References

.. [1] https://docs.python.org/2/library/tempfile.html

# TESTING

Example tests to complete and check installation.

## Define paths

Define local paths and paths within iRODS.

```bash
REPO=~/irods_module_iplant # Example local directory for cloned git repository.
IRODS=~/iRODS # Example local root directory for iRODS installation.
IPLANT=/tempZone/home/rods/iplant # Example iRODS directory to save iplant data.
ITMP_IPLANT=/tempZone/tmp/iplant # Example iRODS directory to save temporary files.
imkdir -p $ITMP_IPLANT # Create iRODS temporary directory.
TMP_IPLANT=/tmp/iplant # Example local directory to save tempoary files.
mkdir -p $TMP_IPLANT # Create local temporary directory.
IPLANT_LOG=/tmp/iplant/iplant.log # Example local path to save iPlant log file.
```

## Test iRODS temporary directory

Test that iRODS icommands execute in the user-defined iRODS temporary directory without calling rules from `$IRODS/server/config/reConfigs/iplant.re`. These icommands are used by `iplant.py`.

```bash
date
iput -T $REPO/iplant/test/test1.fastq $ITMP_IPLANT/.
icp $ITMP_IPLANT/test1.fastq $ITMP_IPLANT/test1_copied.fastq
imv $ITMP_IPLANT/test1_copied.fastq $ITMP_IPLANT/test1_moved.fastq
iget -T $ITMP_IPLANT/test1_moved.fastq $TMP_IPLANT/.
diff $REPO/iplant/test/test1.fastq $TMP_IPLANT/test1_moved.fastq
irm -f $ITMP_IPLANT/test1.fastq $ITMP_IPLANT/test1_moved.fastq
rm -f $TMP_IPLANT/test1_moved.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
```

## Test `iplant.py` without automatic calls from iRODS

Test that the `$IRODS/server/bin/cmd/iplant.py` module is executes correctly when called from the command line for multiple files. Use the original version of `$IRODS/server/config/reConfigs/core.re` from before following [INSTALL.md](INSTALL.md) to avoid automatic calls from iRODS. See `iplant.py --help` to test additional `iplant.py` options.

```bash
# Use the original version of `core.re` from before following `INSTALL.md`: $IRODS/server/config/reConfigs/core.re_BACKUP_YYYYMMDDTHHMMSS
date
iput -T $REPO/iplant/test/test1.fastq $IPLANT/.
$IRODS/server/bin/cmd/iplant.py --ipath $IPLANT/test1.fastq --iplant $IPLANT --action compress --itmp_iplant $ITMP_IPLANT --tmp_iplant $TMP_IPLANT --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
$IRODS/server/bin/cmd/iplant.py --ipath $IPLANT/test1.fastq --iplant $IPLANT --action decompress --itmp_iplant $ITMP_IPLANT --tmp_iplant $TMP_IPLANT --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
iget -T $IPLANT/test1.fastq $TMP_IPLANT/.
diff $REPO/iplant/test/test1.fastq $TMP_IPLANT/test1.fastq
irm -f $IPLANT/test1.fastq
rm -f $TMP_IPLANT/test1.fastq
date
# Read `$IPLANT_LOG` between the timestamps from `date` to check execution.
# Replace `core.re` with the iPlant version from after following `INSTALL.md`.
```

## Test `iplant.py` with automatic calls from iRODS

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly when called by rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. See `iplant.py --help` to test additional `iplant.py` options.

**Note:** As of 2014-12-11, this test fails because the last file fetched is truncated. See issue https://github.com/stharrold/irods_module_iplant/issues/16

```bash
# Use the iPlant version of `core.re` from following `INSTALL.md`.
date
iput -T $REPO/iplant/test/test1.fastq $IPLANT/.
iget -T $IPLANT/test1.fastq $TMP_IPLANT/.
diff $REPO/iplant/test/test1.fastq $TMP_IPLANT/test1.fastq
irm -f $IPLANT/test1.fastq
rm -f $TMP_IPLANT/test1.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
# Read `$IPLANT_LOG` between the timestamps from `date` to check execution.
```

## Notes

- `iplant.py` creates parent directories as needed for `--itmp_iplant`, `--tmp_iplant`, `--log_file`.

## References

.. [1] https://docs.python.org/2/library/tempfile.html

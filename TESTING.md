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

Test that iRODS icommands execute in the user-defined iRODS temporary directory. For this test, avoid invoking rules from `$IRODS/server/config/reConfigs/core.re`.

```bash
date
iput $REPO/iplant/test/test1.fastq $ITMP_IPLANT/.
icp $ITMP_IPLANT/test1.fastq $ITMP_IPLANT/test1_copied.fastq
imv $ITMP_IPLANT/test1_copied.fastq $ITMP_IPLANT/test1_moved.fastq
iget $ITMP_IPLANT/test1_moved.fastq $TMP_IPLANT/.
irm -f $ITMP_IPLANT/test1.fastq $ITMP_IPLANT/test1_moved.fastq
rm -f $TMP_IPLANT/test1_moved.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
```

## Test `iplant.py` with iRODS icommands

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly when invoked by rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. See `iplant.py --help` to test additional `iplant.py` options.

```bash
date
iput $REPO/iplant/test/test1.fastq $IPLANT/.
iget $IPLANT/test1.fastq $TMP_IPLANT/test1_processed.fastq
diff $REPO/iplant/test/test1.fastq $TMP_IPLANT/test1_processed.fastq
irm -f $IPLANT/test1.fastq
rm -f $TMP_IPLANT/test1_processed.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check execution.
# Read `$IPLANT_LOG` between the timestamps from `date` to check execution.
```

## Notes

- `iplant.py` creates parent directories as needed `--itmp_iplant`, `--tmp_iplant`, `--log_file`.

## References

.. [1] https://docs.python.org/2/library/tempfile.html

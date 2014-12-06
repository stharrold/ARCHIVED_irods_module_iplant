# TESTING

Example tests.

## Define paths

Define local paths and paths within iRODS.

```bash
IRODS=~/iRODS # example local root directory for iRODS installation
ITMP=/tempZone/tmp # example iRODS directory to save temporary files
IPLANT_LOG=/tmp/iplant.log # example local path to save iplant log file
IPLANT=/tempZone/home/rods/iplant # example iRODS directory to save iplant data
```

## Test iRODS itmp directory

Test that iRODS icommands execute in the user-defined iRODS temporary directory. For this test, avoid invoking rules from `$IRODS/server/config/reConfigs/core.re`.

```bash
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $ITMP/.
imv $ITMP/test1.fastq $ITMP/test1_moved.fastq # $ITMP must permit move operations
iget $ITMP/test1_moved.fastq /tmp/.
irm -f $ITMP/test1_moved.fastq
rm /tmp/test1_moved.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check that execution was successful.
```

## Test `iplant.py` with command line arguments

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly. For this test, avoid invoking rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. Also see `iplant.py --help` to test additional `iplant.py` options.

```bash
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $ITMP/.
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP/test1.fastq --action compress --itmp $ITMP --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP/test1.fastq --action decompress --itmp $ITMP --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
irm -f $ITMP/test1.fastq
date
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check that execution was successful.
# Read `$IPLANT_LOG` between the timestamps from `date` to check that execution was successful.
```

## Test `iplant.py` with iRODS icommands

Test that the `$IRODS/server/bin/cmd/iplant.py` module executes correctly when invoked by rules from `$IRODS/server/config/reConfigs/core.re` and `$IRODS/server/config/reConfigs/iplant.re`. Also see `iplant.py --help` to test additional `iplant.py` options.

```bash
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $IPLANT/.
iget $IPLANT/test1.fastq /tmp/test1_processed.fastq
diff ~/irods_module_iplant/iplant/test/test1.fastq /tmp/test1_fromirods.fastq
irm -f $IPLANT/test1.fastq
date
# Read $IRODS/server/log/rodsLog.YYYY.MM.DD after timestamp from `date`.
# Read `$IRODS/server/log/rodsLog.YYYY.MM.DD` between the timestamps from `date` to check that execution was successful.
# Read `$IPLANT_LOG` between the timestamps from `date` to check that execution was successful.
```

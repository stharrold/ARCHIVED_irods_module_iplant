# TESTING

Example tests

## Define paths

```bash
IRODS=~/iRODS # example local root directory for iRODS installation
ITMP=/tempZone/tmp # example iRODS directory to save temporary files
IPLANT_LOG=/tmp/iplant.log # example local path to save iplant log file
IPLANT=/tempZone/home/rods/iplant # example iRODS directory to save iplant data
```

## Test iRODS itmp directory

Purpose: Test that iRODS icommands execute in the user-defined iRODS temporary directory without invoking rules from `$IRODS/server/config/reConfigs/core.re`.

```bash
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $ITMP/.
imv $ITMP/test1.fastq $ITMP/test1_moved.fastq
iget $ITMP/test1_moved.fastq /tmp/.
irm -f $ITMP/test1_moved.fastq
rm /tmp/test1_moved.fastq
# Read $IRODS/server/log/rodsLog.YYYY.MM.DD after timestamp from `date`
```

```bash
# BEGIN TEST_IPLANT_MODULE
# Purpose: Test that the iplant.py module works without invoking rules from core.re. Also see `iplant.py --help`.
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $ITMP/.
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP/test1.fastq --action compress --itmp $ITMP --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
$IRODS/server/bin/cmd/iplant.py --ipath $ITMP/test1.fastq --action decompress --itmp $ITMP --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file $IPLANT_LOG
irm -f $ITMP/test1.fastq
# Read $IRODS/server/log/rodsLog.YYYY.MM.DD after timestamp from `date`.
# Read $IPLANT_LOG after timestamp from `date`.
# END TEST_IPLANT_MODULE

# BEGIN TEST_IPLANT_IRODS
# TODO: REDO from above
# Purpose: Test that the iplant.py module works when invoked by rules from core.re.
date
iput ~/irods_module_iplant/iplant/test/test1.fastq $IPLANT/.
iget $IPLANT/test1.fastq /tmp/test1_processed.fastq
diff ~/irods_module_iplant/iplant/test/test1.fastq /tmp/test1_fromirods.fastq
irm -f $IPLANT/test1.fastq
# Read $IRODS/server/log/rodsLog.YYYY.MM.DD after timestamp from `date`.
# Read $IPLANT_LOG after timestamp from `date`.
# END TEST_IPLANT_IRODS
```

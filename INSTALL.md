# Setup

## Example installation

Download this repository and copy files into your iRODS v3.3.1 installation:
```bash
cd ~
git clone https://github.com/stharrold/irods_module_iplant.git
IRODS=~/iRODS # example root iRODS directory
chmod +x ~/irods_module_iplant/iplant/rules/*
cp -r ~/irods_module_iplant/iplant $IRODS/modules/.
cp $IRODS/modules/iplant/rules/*.re $IRODS/server/config/reConfigs/.
cp $IRODS/modules/iplant/rules/*.py $IRODS/server/bin/cmd/.
```

Backup and edit `$IRODS/server/config/server.config` to include rules from `iplant.re`:
```bash
cp $IRODS/server/config/server.config $IRODS/server/config/server.config_BACKUP_YYYYMMDDTHHMMSS
```
```bash
# ORIGINAL:
# reRuleSet   core
# IPLANT:
reRuleSet   core,iplant
```

Backup and edit `$IRODS/server/config/reConfigs/core.re` to call rules from `iplant.re`. Change the `$objPath` comparison to match your colletion:
```bash
cp $IRODS/server/config/reConfigs/core.re $IRODS/server/config/reConfigs/core.re_BACKUP_YYYYMMDDTHHMMSS
```
```bash
# ORIGINAL:
# acPreprocForDataObjOpen { }
# IPLANT:
acPreprocForDataObjOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPreprocForDataObjOpen;
    }
}
# ORIGINAL:
# acPostProcForPut { }
# IPLANT:
acPostProcForPut {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPostProcForPut;
    }
}
# ORIGINAL:
# acPostProcForOpen { }
# IPLANT:
acPostProcForOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPostProcForOpen;
    }
}
# ORIGINAL:
# acBulkPutPostProcPolicy { msiSetBulkPutPostProcPolicy("off"); }
# IPLANT:
acBulkPutPostProcPolicy { msiSetBulkPutPostProcPolicy("on"); }
```

### Note
  - As of 2014-10-11, for iRODS v3.3.1, rules files must be copied by hand (see [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)). Future iRODS releases may automatically link rules files in modules.
  - As of 2014-10-11, [iplant](iplant) does not contain microservices and does not need to be compiled as per [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module).

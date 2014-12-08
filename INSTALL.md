# INSTALL

Example installation. See [TESTING.md](TESTING.md) to complete installation and check.

## Download and copy

- Download this repository and edit `irods_module_iplant/iplant/rules/rules.re` so that the `--iplant` option matches your colletion:  
Replace all instances of: `msiExecCmd("iplant.py", "--ipath $objPath --iplant /tempZone/home/rods/iplant`  
with: `msiExecCmd("iplant.py", "--ipath $objPath --iplant /tempZone/home/rods/iplant`  
- Copy files into your iRODS v3.3.1 installation:
```bash
cd ~
git clone https://github.com/stharrold/irods_module_iplant.git
IRODS=~/iRODS # example root iRODS directory
chmod +x ~/irods_module_iplant/iplant/rules/*
cp -r ~/irods_module_iplant/iplant $IRODS/modules/.
cp $IRODS/modules/iplant/rules/*.re $IRODS/server/config/reConfigs/.
cp $IRODS/modules/iplant/rules/*.py $IRODS/server/bin/cmd/.
```

## Backup and edit `server.config`

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

## Backup and edit `core.re`

Backup and edit `$IRODS/server/config/reConfigs/core.re` to call rules from `iplant.re`:

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

## Notes

  - As of 2014-10-11, for iRODS v3.3.1, rules files must be copied by hand (see [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)). Future iRODS releases may automatically link rules files in modules.
  - As of 2014-10-11, [iplant](iplant) does not contain microservices and does not need to be compiled as per [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module).

## References
- [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module)
- [iRODS v3.3.1 docs: Rules](https://wiki.irods.org/index.php/Rules)
- [iRODS v3.3.1 docs: msiExecCmd](https://wiki.irods.org/doxygen/re_data_obj_opr_8c_a5e67b5b442a039b4ce7a81cfc708b1e3.html)
- [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)
- [iRODS presentation, 2014: Hao Xu, "The iRODS Rule Language"](http://irods.org/wp-content/uploads/2014/06/presentation_rule_engine_irods_user_meeting_2014.pdf)

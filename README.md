# irods_module_iplant

IRODS module for iPlant collaboration.

## Installation

To install:
- ```$IRODS``` is the root directory of your iRODS installation.
- ```git clone https://github.com/stharrold/irods_module_iplant.git```
- ```cp -r irods_module_iplant/iplant $IRODS/modules/.```
- ```cp $IRODS/modules/iplant/rules/*.re $IRODS/server/config/reConfigs/.```
- ```cp $IRODS/modules/iplant/rules/*.py $IRODS/server/bin/cmd/.```
- Call functions in iplant.re from core.re:
  - ```cp $IRODS/server/config/reConfigs/core.re $IRODS/server/config/reConfigs/core.re_BACKUP_YYYYMMDDTHHMMSS```
  - Edit `$IRODS/server/config/reConfigs/core.re`. Change objPath comparison to match collection:
```bash
# ORIGINAL:
# acPreprocForDataObjOpen { }
# iPlant:
acPreprocForDataObjOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPreprocForDataObjOpen;
    }
}
```
```bash
# ORIGINAL:
# acPostProcForPut { }
# iPlant:
acPostProcForPut {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPostProcForPut;
    }
}
```
```bash
# ORIGINAL:
# acPostProcForOpen { }
# iPlant:
acPostProcForOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*.fastq") {
        iplantPostProcForOpen;
    }
}
```
```bash
# ORIGINAL:
# acBulkPutPostProcPolicy { msiSetBulkPutPostProcPolicy("off"); }
# iPlant:
acBulkPutPostProcPolicy { msiSetBulkPutPostProcPolicy("on"); }
```
- Add iplant to server.config:
  - ```cp $IRODS/server/config/server.config $IRODS/server/config/server.config_BACKUP_YYYYMMDDTHHMMSS```
  - Edit `$IRODS/server/config/server.config`:
```bash
# ORIGINAL:
# reRuleSet   core
# iPlant:
reRuleSet   core,iplant
```
- **Note:**
  - As of 2014-10-11, for iRODS v3.3.1, rules files must be copied by hand (see [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)). Future iRODS releases may automatically link rules files in modules.
  - As of 2014-10-11, [iplant](iplant) does not contain microservices and does not need to be compiled as per [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module).

## References
- [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module)
- [iRODS v3.3.1 docs: Rules](https://wiki.irods.org/index.php/Rules)
- [iRODS v3.3.1 docs: msiExecCmd](https://wiki.irods.org/doxygen/re_data_obj_opr_8c_a5e67b5b442a039b4ce7a81cfc708b1e3.html)
- [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)
- [iRODS presentation, 2014: Hao Xu, "The iRODS Rule Language"](http://irods.org/wp-content/uploads/2014/06/presentation_rule_engine_irods_user_meeting_2014.pdf)

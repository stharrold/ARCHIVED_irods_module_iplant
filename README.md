# irods_module_iplant

IRODS module for iPlant collaboration.

To install:
- ```cp -r irods_module_iplant/iplant $IRODS/modules/iplant```
- ```cp $IRODS/modules/iplant/rules/iplant.re $IRODS/server/reConfig/.```
- ```cp $IRODS/modules/iplant/rules/iplant.py $IRODS/server/bin/cmd/.```
- Edit $IRODS/server/config/server.config: ```reRuleSet core,iplant```
- Note:
  - As of 2014-10-11, for iRODS v3.3.1, rules files must be copied by hand (see [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)). Future iRODS releases may automatically link rules files in modules.
  - As of 2014-10-11, [iplant](iplant) does not contain microserices and does not need to be compiled as per [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module).

References:
- [iRODS v3.3.1 docs: How to create a new module](https://wiki.irods.org/index.php/How_to_create_a_new_module)
- [iRODS V3.3.1 docs: Rules](https://wiki.irods.org/index.php/Rules)
- [iRODS v3.3.1 docs: msiExecCmd](https://wiki.irods.org/doxygen/re_data_obj_opr_8c_a5e67b5b442a039b4ce7a81cfc708b1e3.html)
- [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)

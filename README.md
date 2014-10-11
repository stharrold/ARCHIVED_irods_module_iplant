# irods_module_iplant

IRODS module for iPlant collaboration.

To install:
- ```cp -r irods_module_iplant/iplant $IRODS/modules/iplant```
- ```cp $IRODS/modules/iplant/rules/iplant.re $IRODS/server/reConfig/.```
- Edit $IRODS/server/config/server.config: ```reRuleSet core,iplant```
- Note: As of iRODS v3.3.1, rules files must be copied by hand. From [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ).

References:
- https://wiki.irods.org/index.php/How_to_create_a_new_module
- https://wiki.irods.org/index.php/Rules
- [iRODS forum post: "module rules target", 2010](https://groups.google.com/forum/#!searchin/irod-chat/module$20rules/irod-chat/gaBSUd0QyiQ/ECKUNLPF5ooJ)


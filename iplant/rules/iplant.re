# Rules for managing iPlant iRODS collection.
# Order of functions follows order called within $IRODS/server/config/reConfig/core.re
# Function names follow those of $IRODS/server/config/reConfig/core.re
# Functions call $IRODS/server/bin/cmd/iplant.py
# Functions adapted from $IRODS/clients/icommands/test/rules3.0/rulemsiExecCmd.r
# NOTE : As of 2014-12-08, ON($objPath like ...) does not work for acPostProcForOpen.
# REFERENCES:
# [1] https://wiki.irods.org/index.php/Tutorial
# [2] https://wiki.irods.org/index.php/Rules
# [3] https://wiki.irods.org/doxygen/


# PURPOSE : Decompresses files when users do iget, isync, icp.
# CALLED_BY : {core.re:acPreprocForDataObjOpen}
# CALLS : {iplant.py}
# RELATED : {iplantPostProcForPut, iplantPostProcForOpen}
# TODO: 2014-12-08, IRODS bug for ON($objPath like ...) with iplantPreprocForDataObjOpen
# https://github.com/stharrold/irods_module_iplant/issues/13
iplantPreprocForDataObjOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*") {
	writeLine("serverLog", "iplant.re:iplantPreprocForDataObjOpen: Calling iplant.py to decompress $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --iplant /tempZone/home/rods/iplant --action decompress --itmp_iplant /tempZone/tmp/iplant --tmp_iplant /tmp/iplant --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file /tmp/iplant/iplant.log", "", "", "", *Result);
	msiGetStdoutInExecCmdOut(*Result, *Out);
	writeLine("serverLog", "iplant.py:stdout:*Out");
	msiGetStderrInExecCmdOut(*Result, *Err);
	writeLine("serverLog", "iplant.py:stderr:*Err");
    }
}


# PURPOSE : Compress files when users do iput.
# CALLED_BY: {core.re:acPostProcForPut}
# CALLS : {iplant.py}
# RELATED : {iplantPreprocForDataObjOpen, iplantPostProcForOpen}
iplantPostProcForPut {
    ON($objPath like "/tempZone/home/rods/iplant/*") {
	writeLine("serverLog", "iplant.re:iplantPostProcForPut: Calling iplant.py to compress $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --iplant /tempZone/home/rods/iplant --action compress --itmp_iplant /tempZone/tmp/iplant --tmp_iplant /tmp/iplant --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file /tmp/iplant/iplant.log", "", "", "", *Result);
	msiGetStdoutInExecCmdOut(*Result, *Out);
	writeLine("serverLog", "iplant.py:stdout:*Out");
	msiGetStderrInExecCmdOut(*Result, *Err);
	writeLine("serverLog", "iplant.py:stderr:*Err");
    }
}


# PURPOSE : Recompress files after users did iget, isync.
# CALLED_BY: {core.re:acPostProcForOpen}
# CALLS : {iplant.py}
# RELATED : {iplantPreprocForDataObjOpen, iplantPostProcForPut}
iplantPostProcForOpen {
    ON($objPath like "/tempZone/home/rods/iplant/*") {
	writeLine("serverLog", "iplant.re:iplantPostProcForOpen: Calling iplant.py to compress $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --iplant /tempZone/home/rods/iplant --action compress --itmp_iplant /tempZone/tmp/iplant --tmp_iplant /tmp/iplant --delete_itmp_files --delete_tmp_files --logging_level DEBUG --log_file /tmp/iplant/iplant.log", "", "", "", *Result);
	msiGetStdoutInExecCmdOut(*Result, *Out);
	writeLine("serverLog", "iplant.py:stdout:*Out");
	msiGetStderrInExecCmdOut(*Result, *Err);
	writeLine("serverLog", "iplant.py:stderr:*Err");
    }
}

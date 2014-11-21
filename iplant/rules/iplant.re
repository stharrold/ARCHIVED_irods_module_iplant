# Rules for managing iPlant iRODS collection.
# Order of functions follows order called within $IRODS/server/config/reConfig/core.re
# Function names follow those of $IRODS/server/config/reConfig/core.re
# Functions call $IRODS/server/bin/cmd/iplant.py
# Functions adapted from $IRODS/clients/icommands/test/rules3.0/rulemsiExecCmd.r
# REFERENCES:
# [1] https://wiki.irods.org/index.php/Tutorial
# [2] https://wiki.irods.org/index.php/Rules
# [3] https://wiki.irods.org/doxygen/


# PURPOSE : Decompresses files when users do iget, isync.
# CALLED_BY : {core.re:acPreprocForDataObjOpen}
# CALLS : {iplant.py}
# RELATED : {iplantPostProcForPut, iplantPreprocForDataObjOpen}
iplantPreprocForDataObjOpen {
    ON($objPath like "*.fastq") {
	writeLine("serverLog", "iplant.re:iplantPreprocForDataObjOpen: Decompressing $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --action decompress", "", "", "", *Result);
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
    ON($objPath like "*.fastq") {
	writeLine("serverLog", "iplant.re:iplantPostProcForPut: Compressing $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --action compress", "", "", "", *Result);
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
    ON($objPath like "*.fastq") {
	writeLine("serverLog", "iplant.re:iplantPostProcForOpen: Compressing $objPath");
	msiExecCmd("iplant.py", "--ipath $objPath --action compress", "", "", "", *Result);
	msiGetStdoutInExecCmdOut(*Result, *Out);
    	writeLine("serverLog", "iplant.py:stdout:*Out");
	msiGetStderrInExecCmdOut(*Result, *Err);
    	writeLine("serverLog", "iplant.py:stderr:*Err");
    }
}

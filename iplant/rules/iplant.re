iplant {
    postProcForPut;
    myTestRule;
}

postProcForPut {
    ON($objPath like "\*fastq") {
	writeLine("serverLog", "File $objPath");
    }
}

myTestRule {
#Input parameters are:
#  Command to be executed located in directory irods/server/bin/cmd
#  Optional command argument
#  Optional host address for command execution
#  Optional hint for remote data object path, command is executed on host where the file is stored
#  Optional flag.  If > 0, use the resolved physical data object path as first argument
#Output parameter is:
#  Structure holding status, stdout, and stderr from command execution
#Output from running the example is:
#  Command result is
#  Hello world written from irods
    msiExecCmd("hello","written","null","null","null",*Result);
    msiGetStdoutInExecCmdOut(*Result,*Out);
    writeLine("stdout","Command result is");
    writeLine("stdout","*Out");
}

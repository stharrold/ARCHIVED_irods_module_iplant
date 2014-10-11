acPostProcForPut {
  fastqPostProcForPut;
}

fastqPostProcForPut {
  ON($objPath like "\*.fastq") {
    writeLine("serverLog", "File $objPath");
  }
}

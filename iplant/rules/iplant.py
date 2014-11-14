#!/usr/bin/env python
"""Top-level module for iPlant iRODS operations.

See Also
--------
CALLED_BY : {iplant.re}

Notes
-----
Docstring format is adapted from [1]_.
`See Also` references file and objects by category: `CALLS`, `CALLED_BY`, `RELATED`.

References
----------
.. [1] https://github.com/numpy/numpy/blob/master/doc/example.py

"""


import os
import argparse


def compress(ipath):
    """Replace file in iRODS with compressed version.
    
    Parameters
    ----------
    ipath : string
        Path to .fastq file in iRODS database.

    Returns
    -------
    None

    See Also
    --------
    CALLS : {}
    CALLED_BY : {main}
    RELATED : {decompress}
    
    """
    print("TEST: Processing file. Time estimate (min): {min}".format(min=10))
    print("TEST: test imeta for IS_COMPRESSED==False, else raise IOError")
    print("TEST: icp to itmp prefixed with iso timestamp0 to avoid invoking iplant.re")
    print("TEST: check space to move to tmp local, delete oldest files that sum to size")
    print("TEST: iget to tmp local")
    print("TEST: get size, checksum")
    print("TEST: gzip --fast")
    print("TEST: iput to itmp with iso timestamp1 to avoid invoking iplant.re")
    print("TEST: icp to ipath")
    info_msg = ("This file is registered under the extension .fastq but is stored internally to iRODS with compression as .fastq.gz.\n" +
                "File will be decompressed upon retrieval (e.g. with iget, isync).")
    print("TEST: add info {msg}".format(msg=info_msg))
    print("TEST: imeta ['IS_COMPRESSED', True, bool]")
    print("TEST: imeta ['COMPRESSION_METHOD', gzip, ]")
    print("TEST: imeta ['UNCOMPRESSED_SIZE', 100, bytes]")
    print("TEST: imeta ['UNCOMPRESSED_CHECKSUM', 12345, ]")
    print("TEST: imeta ['ORIGINAL_FILE', itmp_timestamp0_iso.fastq, ]")
    return None


def decompress(ipath):
    """Replace file in iRODS with decompressed version.
    
    Parameters
    ----------
    ipath : string
        Path to .fastq file in iRODS database.

    Returns
    -------
    None

    See Also
    --------
    CALLS : {}
    CALLED_BY : {main}
    RELATED : {compress}
    
    """
    print("TEST: Processing file. Time estimate (min): {min}".format(min=10))
    print("TEST: test imeta for is_compressed, method, size, checksum")
    print("TEST: icp to itmp with iso timestamp to avoid invoking iplant.re")
    print("TEST: check space to move to tmp, delete oldest files that sum to size")
    print("TEST: iget to tmp local")
    print("TEST: if method == gzip, gunzip; else warn")
    print("TEST: iput to ipath -f")
    info_msg = ("This file is registered under the extension .fastq and is stored internally to iRODS without compression as .fastq")
    print("TEST: add info {msg}".format(msg=info_msg))
    print("TEST: imeta ['IS_COMPRESSED', False, bool]")
    print("TEST: imeta ['COMPRESSION_METHOD', null, ]")
    print("TEST: imeta ['UNCOMPRESSED_SIZE', 100, bytes]")
    print("TEST: imeta ['UNCOMPRESSED_CHECKSUM', 12345, ]")
    print("TEST: imeta ['ORIGINAL_FILE', itmp_timestamp0_iso.fastq, ]")
    return None


def main(ipath, action):
    """Top-level function for iPlant iRODS operations.

    Parameters
    ----------
    ipath : string
        Path to .fastq file in iRODS database.
    action : string
        Action to take on file from `ipath`
        Examples: action='compress'; action='decompress'
    
    Returns
    -------
    None
    
    See Also
    --------
    CALLS : {compress, decompress}
    CALLED_BY : {__main__}
    RELATED : {}
    
    """
    if action == 'compress':
        compress(ipath=ipath)
    elif action == 'decompress':
        decompress(ipath=ipath)
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compress or decompress .fastq file in iPlant collection.")
    parser.add_argument('--ipath',
                        required=True,
                        help=("iRODS path to .fastq file for (de)compression."))
    parser.add_argument('--action',
                        choices=['compress', 'decompress'],
                        required=True,
                        help=("Action to take on the file."))
    args = parser.parse_args()
    # Check input.
    # TODO: create logger and allow command to set logger verbosity
    print("INFO: Arguments:\n{args}".format(args=args))
    # TODO: check that ipath exists
    (, ext) = os.path.splitext(args.ipath)
    if ext != '.fastq':
        raise IOError("`ipath` file extension is not '.fastq':\n" +
                      "--ipath {ipath}".format(ipath=args.ipath))
    main(ipath=args.ipath, action=args.action)

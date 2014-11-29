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


# Import only standard libraries.
from __future__ import absolute_import, division, print_function
import os
import sys
import pdb
import logging
import argparse
import datetime
import tempfile
import subprocess


# Define logger to work for imports and as __main__.
logger = logging.getLogger(__name__)


def _value_as_units_type(value, units):
    """Semi-private method to convert string values from 'imeta ls' command
    into Python typed values using the labeled unit.

    Parameters
    ----------
    value : string
        Value parsed from 'imeta ls' stdout.
    units : string
        Units parsed from 'imeta ls' stdout.

    Returns
    -------
    typed_value : value as Python type
        Value as a Python type. Examples of accepted units and values:
        INPUT_UNITS               : INPUT_VALUE               : RETURNED_TYPED_VALUE
        ''                        : ''                        : ``None``
        'BOOL', 'Bool', 'bool'    : 'TRUE', 'True', 'true'    : ``True``
        'BOOL', 'Bool', 'bool'    : 'FALSE', 'False', 'false' : ``False``
        'BYTES', 'Bytes', 'bytes' : '12345'                   : 12345
        'INT', 'Int', 'int'       : '12345'                   : 12345

    """
    value = value.lower()
    units = units.lower()
    units_to_typed_value = {'': (lambda x: None if x == '' else x),
                            'bool': (lambda x: True if x == 'true' else False),
                            'bytes': (lambda x: int(float(x))),
                            'int': (lambda x: int(float(x)))}
    if units in units_to_typed_value.keys():
        typed_value = units_to_typed_value[units](value)
    else:
        typed_value = value
    return typed_value
                   

def _imeta_to_dict(imeta_stdout):
    """Semi-private method to parse stdout from 'imeta ls' command into a dict of attributes.
    
    Parameters
    ----------
    imeta_stdout : string
        stdout from 'imeta ls' command, [1]_.
    
    Returns
    -------
    imeta_dict : dict
        ``dict`` of metadata with attribute names as keys.
        Values and units are in a nested ``dict`` under the attribute name.
        Placeholder for null values is ''.
    
    References
    ----------
    .. [1] https://wiki.irods.org/index.php/imeta
    
    """
    # Parse the string stdout by lines.
    # Initialize dict and flags to catch ordered metadata fields.
    lines = imeta_stdout.split('\n')
    imeta_dict = {}
    catch_attribute = True
    catch_value = False
    catch_units = False
    # Catch metadata fields in order. All metadata have name-value-units triplet.
    # Once a metadata field is found, skip remaining if-elif-else statements.
    for line in lines:
        if catch_attribute and line.startswith('attribute'):
            (field, attr_name) = [elt.strip() for elt in line.split(':')]
            if field != 'attribute':
                raise AssertionError(("Program error. Parsed metadata field should be 'attribute'. Actual metadata:\n" +
                                      "line = {line}\n" +
                                      "field = {field}").format(line=line, field=field))
            imeta_dict[attr_name] = {}
            catch_attribute = False
            catch_value = True
            continue
        elif catch_value and line.startswith('value'):
            (field, attr_value) = [elt.strip() for elt in line.split(':')]
            if field != 'value':
                raise AssertionError(("Program error. Parsed metadata field should be 'value'. Actual metadata:\n" +
                                      "line = {line}\n" +
                                      "field = {field}").format(line=line, field=field))
            imeta_dict[attr_name][field] = attr_value
            catch_value = False
            catch_units = True
            continue
        elif catch_units and line.startswith('units'):
            (field, attr_units) = [elt.strip() for elt in line.split(':')]
            if field != 'units':
                raise AssertionError(("Program error. Parsed metadata field should be 'units'. Actual metadata:\n" +
                                      "line = {line}\n" +
                                      "field = {field}").format(line=line, field=field))
            imeta_dict[attr_name][field] = attr_units
            imeta_dict[attr_name]['value'] = _value_as_units_type(value=imeta_dict[attr_name]['value'],
                                                                 units=imeta_dict[attr_name]['units'])
            catch_units = False
            catch_attribute = True
            if not (catch_attribute and not catch_value and not catch_units):
                raise AssertionError(("Program error. Flags to catch metadata should be\n" +
                                      "(catch_attribute, catch_value, catch_units) == (True, False, False).\n" +
                                      "Actual flag values:\n" +
                                      "catch_attribute = {ca}\n" +
                                      "catch_value = {cv}\n" +
                                      "catch_units = {cu}").format(ca=catch_attribute, cv=catch_value, cu=catch_unit))
            continue
        else:
            # Otherwise line has nothing to parse.
            continue
    return imeta_dict


def compress(ipath, itmp_iplant, tmp_iplant, delete_tmp=False):
    """Replace file in iRODS with compressed version.
    
    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for (de)compression.
    itmp_iplant : string
        iRODS path to temporary 'iplant' directory for moving files during compression.
    tmp_iplant : string
        Local path to temporary 'iplant' directory for moving files during compression.
    delete_tmp : {False, True}, bool, optional
        Delete temporary files made during (de)compression. Compressing a file creates a compressed copy
        and an uncompressed copy of the file in both `itmp`/iplant/ and local 'tmp'/iplant/ directories.

    Returns
    -------
    None

    See Also
    --------
    CALLS : {}
    CALLED_BY : {main}
    RELATED : {decompress}

    Notes
    -----
    Compressing a file creates a compressed copy and an uncompressed copy of the file in both `itmp`/iplant/
    and local 'tmp'/iplant/ directories.
    
    """
    # NOTE: Input checking is handled by "if __name__ == '__main__'" section and main() function.
    print("compress: TODO: Processing file. Time estimate (min): {min}".format(min=10))
    # Determine if data is compressed from imeta.
    logger.debug("compress: imeta ls -d {ipath}".format(ipath=ipath))
    imeta_stdout = subprocess.check_output(["imeta", "ls", "-d", ipath])
    logger.debug(("compress: imeta_stdout =\n" +
                  "{imeta_stdout}").format(imeta_stdout=imeta_stdout))
    imeta_dict = _imeta_to_dict(imeta_stdout=imeta_stdout)
    logger.debug(("compress: _imeta_to_dict(imeta_stdout) =\n" +
                  "{imeta_dict}").format(imeta_dict=imeta_dict))
    do_compress = None
    if 'IS_COMPRESSED' in imeta_dict.keys():
        if imeta_dict['IS_COMPRESSED']['value']:
            do_compress = False
        else:
            do_compress = True
    else:
        do_compress = True
    if do_compress is None:
        raise AssertionError(("Program error. 'do_compress' flag not set:\n" +
                              "do_compress = {dc}").format(dc=do_compress))
    # Compress data...
    if do_compress:
        logger.debug("compress: Compressing {ipath}".format(ipath=ipath))
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        fname = timestamp+'_'+os.path.basename(ipath)
        itmp_path = os.path.join(itmp_iplant, fname)
        logger.debug("compress: imv {ipath} {itmp_path}".format(ipath=ipath, itmp_path=itmp_path))
        subprocess.check_output(["imv", ipath, itmp_path])
        # TODO: check space to move to tmp local, delete oldest files that sum to size
        tmp_path = os.path.join(tmp_iplant, fname)
        logger.debug("compress: iget {itmp_path} {tmp_path}".format(itmp_path=itmp_path, tmp_path=tmp_path))
        #subprocess.check_output(["iget", itmp_path, tmp_path])
        print("TEST: iget to tmp local")
        print("TEST: get size, checksum")
        print("TEST: gzip --fast")
        print("TEST: iput to itmp with iso timestamp1 to avoid invoking iplant.re")
        print("TEST: imv to ipath")
        info_msg = ("This file is registered under the extension .fastq but is stored internally to iRODS with compression as .fastq.gz.\n" +
                    "File will be decompressed upon retrieval (e.g. with iget, isync).")
        print("TEST: add info {msg}".format(msg=info_msg))
        print("TEST: imeta set -d ['IS_COMPRESSED', True, bool]")
        print("TEST: imeta set -d ['COMPRESSION_METHOD', gzip, ]")
        print("TEST: imeta set -d ['UNCOMPRESSED_SIZE', 100, bytes]")
        print("TEST: imeta set -d ['UNCOMPRESSED_CHECKSUM', 12345, ]")
        print("TEST: imeta set -d ['ORIGINAL_FILE', itmp_timestamp0_iso.fastq, ]")
    # ...otherwise do nothing.
    else:
        logger.debug("compress: Skipping compress for {ipath}".format(ipath=ipath))
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
    print("TEST: imv to itmp with iso timestamp to avoid invoking iplant.re")
    print("TEST: check space to move to tmp, delete oldest files that sum to size")
    print("TEST: iget to tmp local")
    print("TEST: if method == gzip, gunzip; else warn")
    print("TEST: iput to itmp then  -f")
    info_msg = ("This file is registered under the extension .fastq and is stored internally to iRODS without compression as .fastq")
    print("TEST: add info {msg}".format(msg=info_msg))
    print("TEST: imeta set -d ['IS_COMPRESSED', False, bool]")
    print("TEST: imeta set -d ['COMPRESSION_METHOD', null, ]")
    print("TEST: imeta set -d ['UNCOMPRESSED_SIZE', 100, bytes]")
    print("TEST: imeta set -d ['UNCOMPRESSED_CHECKSUM', 12345, ]")
    print("TEST: imeta set -d ['ORIGINAL_FILE', itmp_timestamp0_iso.fastq, ]")
    return None


def main(ipath, action, itmp, delete_tmp=False, logginglevel='INFO'):
    """Top-level function for iPlant iRODS operations.

    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for (de)compression.
    action : {'compress', 'decompress'}, string
        Action to take on file from `ipath`.
    itmp : string
        iRODS path to temporary directory for moving files during (de)compression.
        Files will be created in `itmp`/iplant/ and local 'tmp'/iplant/ directories.
    delete_tmp : {False, True}, bool, optional
        Delete temporary files made during (de)compression. Compressing a file creates a compressed copy
        and an uncompressed copy of the file in both `itmp`/iplant/ and local 'tmp'/iplant/ directories.
    logginglevel : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, string, optional
        Verbosity of logging level. 'DEBUG' is most verbose; 'CRITICAL' is least.
        Default: 'INFO'
    
    Returns
    -------
    None
    
    See Also
    --------
    CALLS : {compress, decompress}
    CALLED_BY : {__main__}
    RELATED : {}
    
    """
    # NOTE: Input checking is handled by "if __name__ == '__main__'" section.
    # Set logging level and add handler.
    logger.setLevel(level=logginglevel)
    shandler = logging.StreamHandler(sys.stdout)
    logger.addHandler(shandler)
    logger.debug("main: Added stdout stream handler to logger.")
    # Check that temporary directories exist.
    itmp_iplant = os.path.join(itmp, 'iplant')
    try:
        subprocess.check_output(["ils", itmp_iplant])
    except subprocess.CalledProcessError:
        logger.debug("main: imkdir -p {itmp_iplant}".format(itmp_iplant=itmp_iplant))
        subprocess.check_output(["imkdir", "-p", itmp_iplant])
    tmp_iplant = os.path.join(tempfile.gettempdir(), 'iplant')
    if not os.path.exists(tmp_iplant):
        logger.debug("main: os.makedirs({tmp_iplant})".format(tmp_iplant=tmp_iplant))
        os.makedirs(tmp_iplant)
    # Perform action on file.
    if action == 'compress':
        logger.debug("main: Compressing {ipath}".format(ipath=ipath))
        compress(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant, delete_tmp=delete_tmp)
    elif action == 'decompress':
        logger.debug("main: Decompressing {ipath}".format(ipath=ipath))
        decompress(ipath=ipath)
    # Remove logging handler.
    logger.debug("main: Removing stdout stream handler from logger.")
    logger.removeHandler(shandler)
    return None


if __name__ == '__main__':
    # Define defaults.
    defaults = {}
    defaults['logginglevel'] = 'INFO'
    # Parse input arguments and check choices.
    parser = argparse.ArgumentParser(description="Compress or decompress .fastq file in iPlant collection.")
    parser.add_argument('--ipath',
                        required=True,
                        help=("iRODS path to .fastq file for (de)compression."))
    parser.add_argument('--action',
                        choices=['compress', 'decompress'],
                        required=True,
                        help=("Action to take on the file from `ipath`."))
    parser.add_argument('--itmp',
                        required=True,
                        help=("iRODS path to temporary directory for moving files during (de)compression.\n" +
                              "Files will be created in `itmp`/iplant/ and local 'tmp'/iplant/ directories."))
    parser.add_argument('--delete_tmp',
                        action='store_true',
                        help=("Delete temporary files made during (de)compression. (De)compressing a file creates a compressed copy\n" +
                              "and an uncompressed copy of the file in both `itmp`/iplant/ and local 'tmp'/iplant/ directories."))
    parser.add_argument('--logginglevel',
                        default=defaults['logginglevel'],
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help=(("Verbosity of logging level. 'DEBUG' is most verbose; 'CRITICAL' is least." +
                               "Default: {dflt}").format(dflt=defaults['logginglevel'])))
    args = parser.parse_args()
    # Check input then call main function.
    print("INFO: Arguments:\n{args}".format(args=args))
    try:
        subprocess.check_output(["ils", args.ipath])
    except subprocess.CalledProcessError:
        raise IOError(("`ipath` does not exist or user lacks access permission:\n" +
                       "--ipath {ipath}").format(ipath=args.ipath))
    (base, ext) = os.path.splitext(args.ipath)
    if ext != '.fastq':
        raise IOError(("`ipath` file extension is not '.fastq':\n" +
                       "--ipath {ipath}").format(ipath=args.ipath))
    try:
        subprocess.check_output(["ils", args.itmp])
    except subprocess.CalledProcessError:
        raise IOError(("`itmp` does not exist or user lacks access permission:\n" +
                       "--itmp {itmp}").format(itmp=args.itmp))
    main(ipath=args.ipath, action=args.action, itmp=args.itmp, delete_tmp=args.delete_tmp, logginglevel=args.logginglevel)

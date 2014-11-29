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
                   

def _imeta_to_dict(stdout):
    """Semi-private method to parse stdout from 'imeta ls' command into a dict of attributes.
    
    Parameters
    ----------
    stdout : string
        stdout from 'imeta ls' command, [1]_.
    
    Returns
    -------
    attr_dict : dict
        ``dict`` of metadata with attribute names as keys.
        Values and units are in a nested ``dict`` under the attribute name.
        Placeholder for null values is ''.
    
    References
    ----------
    .. [1] https://wiki.irods.org/index.php/imeta
    
    """
    # Parse the string stdout by lines.
    # Initialize dict and flags to catch ordered metadata fields.
    lines = stdout.split('\n')
    attr_dict = {}
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
            attr_dict[attr_name] = {}
            catch_attribute = False
            catch_value = True
            continue
        elif catch_value and line.startswith('value'):
            (field, attr_value) = [elt.strip() for elt in line.split(':')]
            if field != 'value':
                raise AssertionError(("Program error. Parsed metadata field should be 'value'. Actual metadata:\n" +
                                      "line = {line}\n" +
                                      "field = {field}").format(line=line, field=field))
            attr_dict[attr_name][field] = attr_value
            catch_value = False
            catch_units = True
            continue
        elif catch_units and line.startswith('units'):
            (field, attr_units) = [elt.strip() for elt in line.split(':')]
            if field != 'units':
                raise AssertionError(("Program error. Parsed metadata field should be 'units'. Actual metadata:\n" +
                                      "line = {line}\n" +
                                      "field = {field}").format(line=line, field=field))
            attr_dict[attr_name][field] = attr_units
            attr_dict[attr_name]['value'] = _value_as_units_type(value=attr_dict[attr_name]['value'],
                                                                 units=attr_dict[attr_name]['units'])
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
    return attr_dict


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
    print("compress: TODO: Processing file. Time estimate (min): {min}".format(min=10))
    # Determine if data is compressed from imeta.
    imeta_stdout = subprocess.check_output(["imeta", "ls", "-d", ipath])
    attr_dict = _imeta_to_dict(stdout=imeta_stdout)
    do_compress = None
    if 'IS_COMPRESSED' in attr_dict.keys():
        if attr_dict['IS_COMPRESSED']['value']:
            do_compress = False
        else:
            do_compress = True
    else:
        do_compress = True
    if do_compress is None:
        raise AssertionError(("Program error. 'do_compress' flag not set:\n" +
                              "do_compress = {dc}").format(dc=do_compress))
    if do_compress:
        logger.debug("compress: compressing {ipath}".format(ipath=ipath))
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        #itmp_path = os.path.
        subprocess.check_output(["imv", ipath, itmp])
        print("TEST: imv to itmp prefixed with iso timestamp0 to avoid invoking iplant.re")
        print("TEST: check space to move to tmp local, delete oldest files that sum to size")
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
    else:
        logger.debug("compress: skipping compress for {ipath}".format(ipath=ipath))
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
    delete_tmp : {False, True}, bool, optional
        Delete temporary files made during (de)compression. Compressing a file creates
        a compressed and a uncompressed copy of the file in both `itmp` and the local 'tmp' directory.
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
    # Check input.
    valid_actions = ['compress', 'decompress']
    if action in valid_actions:
        raise IOError(("Not a valid action: {act}\n" +
                       "Valid actions: {vact}").format(act=action, vact=valid_actions))
    valid_logginglevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if logginglevel not in valid_logginglevels:
        raise IOError(("Not a valid logging level: {ll}\n" +
                       "Valid logging levels: {vll}").format(ll=logginglevel, vll=valid_logginglevels))
    # Set logging level and add handler.
    logger.setLevel(level=logginglevel)
    shandler = logging.StreamHandler(sys.stdout)
    logger.addHandler(shandler)
    logger.debug("main: Added stream handler to logger.")
    # Perform action on file.
    if action == 'compress':
        logger.debug("main: compressing {ipath}".format(ipath=ipath))
        compress(ipath=ipath)
    elif action == 'decompress':
        logger.debug("main: decompressing {ipath}".format(ipath=ipath))
        decompress(ipath=ipath)
    else:
        raise 
    # Remove logging handler.
    logger.debug("main: Removing stream handler from logger.")
    logger.removeHandler(shandler)
    return None


if __name__ == '__main__':
    # Define defaults.
    # TODO: make unit test flag
    defaults = {}
    defaults['logginglevel'] = 'INFO'
    # Parse input arguments.
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
                        help=("iRODS path to temporary directory for moving files during (de)compression."))
    parser.add_argument('--delete_tmp',
                        action='store_true',
                        help=("Delete temporary files made during (de)compression. Compressing a file creates\n" +
                              "a compressed and a uncompressed copy of the file in both `itmp` and the local 'tmp' directory."))
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
    main(ipath=args.ipath, action=args.action, itmp=arg.itmp, delete_tmp=args.delete_tmp, logginglevel=args.logginglevel)

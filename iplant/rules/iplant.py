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
import time
import hashlib
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
        Value as a Python type. Examples of accepted units and values (inputs are not case-sensitive):
        INPUT_UNITS               : INPUT_VALUE               : RETURNED_TYPED_VALUE
        'NONE', 'None', 'none'    : 'NONE', 'None, 'none'     : ``None``
        'BOOL', 'Bool', 'bool'    : 'TRUE', 'True', 'true'    : ``True``
        'BOOL', 'Bool', 'bool'    : 'FALSE', 'False', 'false' : ``False``
        'BYTES', 'Bytes', 'bytes' : '12345'                   : 12345

    See Also
    --------
    CALLS : {}
    CALLED_BY : {_imeta_to_dict}
    RELATED : {}

    """
    units_lower = units.lower()
    units_to_typed_value = {'none': (lambda x: None if x == 'none' else x),
                            'bool': (lambda x: True if x.lower() == 'true' else False),
                            'bytes': (lambda x: int(float(x)))}
    if units_lower in units_to_typed_value.keys():
        typed_value = units_to_typed_value[units_lower](value)
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
        Placeholder for null values is 'NONE'.

    See Also
    --------
    CALLS : {_value_as_units_type}
    CALLED_BY : {compress, decompress}
    RELATED : {}
    
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


def _compute_hash(fpath, algorithm='sha1', blocksize=2**16):
    """Semi-private method to compute hash of file.

    Use to check that file was not corrupted during compression. Incrementally reads files to accommodate
    large file sizes.

    Parameters
    ----------
    fpath : string
        Path to local file.
    algorithm : {'sha1'}, hashlib.algorithm, optional
        Hashing function. Must be a `hashlib.algorithm`. Not case-sensitive.
    blocksize : {2**16}, int, optional
        Number of bytes to read incrementally.

    Returns
    -------
    hexdigest : string
        Secure hash as non-binary string.

    See Also
    --------
    CALLS : {}
    CALLED_BY : {compress, decompress}
    RELATED : {}
    
    Notes
    -----
    Adapted from [1]_.
    Typical processing speed is ~4.4 GB/min.
    
    References
    ----------
    .. [1] http://www.pythoncentral.io/hashing-files-with-python/

    """
    # Check input.
    algorithm = algorithm.lower()
    if algorithm not in hashlib.algorithms:
        raise IOError(("Algorithm not valid.\n" + 
                       "algorithm = {alg}\n" +
                       "valid_algorithms = {valgs}").format(alg=algorithm, valgs=hashlib.algorithms))
    hasher = getattr(hashlib, algorithm)()
    # Read big file incrementally to compute hash.
    with open(fpath, 'rb') as fobj:
        buf = fobj.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fobj.read(blocksize)
    hexdigest = hasher.hexdigest()
    return hexdigest


def compress(ipath, itmp_iplant, tmp_iplant, delete_itmp_files=False, delete_tmp_files=False):
    """Replace file in iRODS with compressed version.
    
    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for compression.
    itmp_iplant : string
        iRODS path to temporary 'iplant' directory for moving files during compression.
    tmp_iplant : string
        Local path to temporary 'iplant' directory for moving files during compression.
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during compression. Compressing a file creates
        a compressed copy and an uncompressed copy of the file in the iRODS `itmp_iplant`/ directory.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during compression. Compressing a file creates
        a compressed copy and an uncompressed copy of the file in the local `tmp_iplant`/ directory.

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
    Compressing a file creates a compressed copy and an uncompressed copy of the file in both `itmp_iplant`/
    and local 'tmp'/iplant/ directories.
    
    """
    # NOTE: Input checking is handled by "if __name__ == '__main__'" section and main() function.
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
                              "do_compress = {do_compress}").format(do_compress=do_compress))
    # Compress data...
    if do_compress:
        logger.debug("compress: do_compress = {do_compress}".format(do_compress=do_compress))
        # Define temporary file paths.
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        fname = timestamp+'_'+os.path.basename(ipath)
        itmp_path = os.path.join(itmp_iplant, fname)
        tmp_path = os.path.join(tmp_iplant, fname)
        fname_gz = fname+'.gz'
        tmp_path_gz = tmp_path+'.gz'
        itmp_path_gz = itmp_path+'.gz'
        # Move data to temporary files, record metadata on uncompressed version, then compress.
        # NOTE: Use imv instead of icp since icp will invoke acPreprocForDataObjOpen
        logger.debug("compress: imv {ipath} {itmp_path}".format(ipath=ipath, itmp_path=itmp_path))
        subprocess.check_output(["imv", ipath, itmp_path])
        # TODO: check space to move to tmp local, delete oldest files that sum to size
        logger.debug("compress: iget {itmp_path} {tmp_path}".format(itmp_path=itmp_path, tmp_path=tmp_path))
        subprocess.check_output(["iget", itmp_path, tmp_path])
        logger.debug("compress: uncompressed_size = os.path.getsize({tmp_path})".format(tmp_path=tmp_path))
        uncompressed_size = os.path.getsize(tmp_path)
        logger.debug("compress: uncompressed_size = {uncompressed_size}".format(uncompressed_size=uncompressed_size))
        logger.debug("compress: uncompressed_hash = _compute_hash({tmp_path})".format(tmp_path=tmp_path))
        uncompressed_hash = _compute_hash(fpath=tmp_path)
        logger.debug("compress: uncompressed_hash = {uncompressed_hash}".format(uncompressed_hash=uncompressed_hash))
        logger.debug("compress: gzip --fast --force --keep {tmp_path}".format(tmp_path=tmp_path))
        subprocess.check_output(["gzip", "--fast", "--force", "--keep", tmp_path])
        logger.debug("compress: iput {tmp_path_gz} {itmp_path_gz}".format(tmp_path_gz=tmp_path_gz, itmp_path_gz=itmp_path_gz))
        subprocess.check_output(["iput", tmp_path_gz, itmp_path_gz])
        logger.debug("compress: imv {itmp_path_gz} {ipath}".format(itmp_path_gz=itmp_path_gz, ipath=ipath))
        subprocess.check_output(["imv", itmp_path_gz, ipath])
        # Set metadata describing compression state. Metadata must be converted to strings.
        comments = "'This file is registered under the extension .fastq but is stored internally to iRODS with compression as .fastq.gz. This file will be decompressed upon retrieval (e.g. with iget, isync).'"
        imeta_triplets = [('IS_COMPRESSED', 'TRUE', 'BOOL'),
                          ('COMPRESSION_METHOD', 'GZIP', 'NONE'),
                          ('UNCOMPRESSED_SIZE', uncompressed_size, 'BYTES'),
                          ('UNCOMPRESSED_HASH', uncompressed_hash, 'NONE'),
                          ('HASH_METHOD', 'SHA1', 'NONE'),
                          ('PARENT_FILE', itmp_path, 'NONE'),
                          ('COMMENTS', comments, 'NONE')]
        imeta_triplets = [[str(elt) for elt in triplet] for triplet in imeta_triplets]
        for (attr, value, units) in imeta_triplets:
            logger.debug("compress: imeta set -d {ipath} {attr} {value} {units}".format(ipath=ipath, attr=attr, value=value, units=units))
            subprocess.check_output(["imeta", "set", "-d", ipath, attr, value, units])
        # Delete temporary files if requested.
        if delete_itmp_files:
            logger.debug("compress: delete_itmp_files = {delete_itmp_files}".format(delete_itmp_files=delete_itmp_files))
            # NOTE: itmp_path_gz does not exist since itmp_path_gz was moved to ipath.
            for itmp in [itmp_path]:
                logger.debug("compress: irm -f {itmp}".format(itmp=itmp))
                subprocess.check_output(["irm", "-f", itmp])
        if delete_tmp_files:
            logger.debug("compress: delete_tmp_files = {delete_tmp_files}".format(delete_tmp_files=delete_tmp_files))
            for tmp in [tmp_path, tmp_path_gz]:
                logger.debug("compress: os.remove({tmp})".format(tmp=tmp))
                os.remove(tmp)
    # ...otherwise do nothing.
    else:
        logger.debug("compress: do_compress = {do_compress}".format(do_compress=do_compress))
    return None


def decompress(ipath, itmp_iplant, tmp_iplant, delete_itmp_files=False, delete_tmp_files=False):
    """Replace file in iRODS with decompressed version.
    
    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for compression.
    itmp_iplant : string
        iRODS path to temporary 'iplant' directory for moving files during compression.
    tmp_iplant : string
        Local path to temporary 'iplant' directory for moving files during compression.
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during decompression. Decompressing a file creates
        a compressed copy and an uncompressed copy of the file in the iRODS `itmp_iplant`/ directory.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during decompression. Decompressing a file creates
        a compressed copy and an uncompressed copy of the file in the local `tmp_iplant`/ directory.

    Returns
    -------
    None

    See Also
    --------
    CALLS : {}
    CALLED_BY : {main}
    RELATED : {compress}
    
    """
    # NOTE: Input checking is handled by "if __name__ == '__main__'" section and main() function.
    # Determine if data is decompressed from imeta.
    logger.debug("decompress: imeta ls -d {ipath}".format(ipath=ipath))
    imeta_stdout = subprocess.check_output(["imeta", "ls", "-d", ipath])
    logger.debug(("decompress: imeta_stdout =\n" +
                  "{imeta_stdout}").format(imeta_stdout=imeta_stdout))
    imeta_dict = _imeta_to_dict(imeta_stdout=imeta_stdout)
    logger.debug(("decompress: _imeta_to_dict(imeta_stdout) =\n" +
                  "{imeta_dict}").format(imeta_dict=imeta_dict))
    do_decompress = None
    if 'IS_COMPRESSED' in imeta_dict.keys():
        if imeta_dict['IS_COMPRESSED']['value']:
            do_decompress = True
        else:
            do_decompress = False
    else:
        do_decompress = False
    if do_decompress is None:
        raise AssertionError(("Program error. 'do_decompress' flag not set:\n" +
                              "do_decompress = {do_decompress}").format(do_decompress=do_decompress))
    # Decompress data...
    if do_decompress:
        logger.debug("decompress: do_decompress = {do_decompress}".format(do_decompress=do_decompress))
        # Define temporary file paths.
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        fname = timestamp+'_'+os.path.basename(ipath)
        itmp_path = os.path.join(itmp_iplant, fname)
        tmp_path = os.path.join(tmp_iplant, fname)
        compression_method_imeta = imeta_dict['COMPRESSION_METHOD']['value']
        valid_compression_methods = ['GZIP']
        # Move data to temporary files then decompress.
        # NOTE: Use imv instead of icp since icp will invoke acPreprocForDataObjOpen
        # NOTE: File is already compressed, so rename with compressed extension (e.g. '.gz') when moving to temporary location.
        if compression_method_imeta == 'GZIP':
            fname_gz = fname+'.gz'
            tmp_path_gz = tmp_path+'.gz'
            itmp_path_gz = itmp_path+'.gz'
            logger.debug("decompress: imv {ipath} {itmp_path_gz}".format(ipath=ipath, itmp_path_gz=itmp_path_gz))
            subprocess.check_output(["imv", ipath, itmp_path_gz])
            # TODO: check space to move to tmp local, delete oldest files that sum to size
            logger.debug("decompress: iget {itmp_path_gz} {tmp_path_gz}".format(itmp_path_gz=itmp_path_gz, tmp_path_gz=tmp_path_gz))
            subprocess.check_output(["iget", itmp_path_gz, tmp_path_gz])
            logger.debug("decompress: gunzip --force --keep {tmp_path_gz}".format(tmp_path_gz=tmp_path_gz))
            subprocess.check_output(["gunzip", "--force", "--keep", tmp_path_gz])
        elif compression_method_imeta not in valid_compression_methods:
            logger.error(("decompress: 'COMPRESSION_METHOD' not valid. Skipping decompression.\n" +
                          "COMPRESSION_METHOD = {cm}\n" +
                          "valid_compression_methods = {vcm}").format(cm=compression_method_imeta, vcm=valid_compression_methods))
        # If file was successfully decompressed, check metadata against uncompressed version then move to ipath..
        if os.path.isfile(tmp_path):
            logger.debug("decompress: uncompressed_size = os.path.getsize({tmp_path})".format(tmp_path=tmp_path))
            uncompressed_size = os.path.getsize(tmp_path)
            logger.debug("decompress: uncompressed_size = {uncompressed_size}".format(uncompressed_size=uncompressed_size))
            uncompressed_size_imeta = imeta_dict['UNCOMPRESSED_SIZE']['value']
            if uncompressed_size != uncompressed_size_imeta:
                logger.error(("decompress: Uncompressed file size does not match 'UNCOMPRESSED_SIZE' from imeta.\n" +
                              "uncompressed_size from file  = {us}\n" +
                              "UNCOMPRESSED_SIZE from imeta = {usi}").format(us=uncompressed_size, usi=uncompressed_size_imeta))
            hash_method_imeta = imeta_dict['HASH_METHOD']['value']
            logger.debug(("decompress: uncompressed_hash = _compute_hash(fpath={tmp_path}," +
                          "algorithm={hmi})").format(tmp_path=tmp_path, hmi=hash_method_imeta))
            uncompressed_hash = _compute_hash(fpath=tmp_path, algorithm=hash_method_imeta)
            logger.debug("decompress: uncompressed_hash = {uncompressed_hash}".format(uncompressed_hash=uncompressed_hash))
            uncompressed_hash_imeta = imeta_dict['UNCOMPRESSED_HASH']['value']
            if uncompressed_hash != uncompressed_hash_imeta:
                logger.error(("decompress: Uncompressed hash size does not match 'UNCOMPRESSED_HASH' from imeta.\n" +
                              "uncompressed_hash from file     = {uh}\n" +
                              "UNCOMPRESSED_HASH from imeta    = {uhi}\n" +
                              "HASH_METHOD from file and imeta = {hmi}").format(uh=uncompressed_hash,
                                                                                uhi=uncompressed_hash_imeta, hmi=hash_method_imeta))
            logger.debug("decompress: iput {tmp_path} {itmp_path}".format(tmp_path=tmp_path, itmp_path=itmp_path))
            subprocess.check_output(["iput", tmp_path, itmp_path])
            logger.debug("decompress: imv {itmp_path} {ipath}".format(itmp_path=itmp_path, ipath=ipath))
            subprocess.check_output(["imv", itmp_path, ipath])
            # Set metadata describing compression state. Metadata must be converted to strings.
            comments = "'This file is registered under the extension .fastq and is stored internally to iRODS without compression as .fastq.'"
            imeta_triplets = [('IS_COMPRESSED', 'FALSE', 'BOOL'),
                              ('COMPRESSION_METHOD', 'NONE', 'NONE'),
                              ('UNCOMPRESSED_SIZE', uncompressed_size, 'BYTES'),
                              ('UNCOMPRESSED_HASH', uncompressed_hash, 'NONE'),
                              ('HASH_METHOD', hash_method_imeta, 'NONE'),
                              ('PARENT_FILE', itmp_path_gz, 'NONE'),
                              ('COMMENTS', comments, 'NONE')]
            imeta_triplets = [[str(elt) for elt in triplet] for triplet in imeta_triplets]
            for (attr, value, units) in imeta_triplets:
                logger.debug("decompress: imeta set -d {ipath} {attr} {value} {units}".format(ipath=ipath, attr=attr, value=value, units=units))
                subprocess.check_output(["imeta", "set", "-d", ipath, attr, value, units])
            # Delete temporary files if requested.
            if delete_itmp_files:
                logger.debug("decompress: delete_itmp_files = {delete_itmp_files}".format(delete_itmp_files=delete_itmp_files))
                # NOTE: itmp_path does not exist since itmp_path was moved to ipath
                for itmp in [itmp_path_gz]:
                    logger.debug("decompress: irm -f {itmp}".format(itmp=itmp))
                    subprocess.check_output(["irm", "-f", itmp])
            if delete_tmp_files:
                logger.debug("decompress: delete_tmp_files = {delete_tmp_files}".format(delete_tmp_files=delete_tmp_files))
                for tmp in [tmp_path, tmp_path_gz]:
                    logger.debug("decompress: os.remove({tmp})".format(tmp=tmp))
                    os.remove(tmp)
        else:
            logger.error(("decompress: File was not decompressed.\n" +
                          "tmp_path = {tmp_path}\n").format(tmp_path=tmp_path))
    # ...otherwise do nothing.
    else:
        logger.debug("decompress: do_decompress = {do_decompress}")
    return None


def main(ipath, action, itmp, delete_itmp_files=False, delete_tmp_files=False, logging_level='INFO'):
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
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during (de)compression. (De)compressing a file creates
        a compressed copy and an uncompressed copy of the file in the iRODS `itmp`/iplant/ directory.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during (de)compression. (De)compressing a file creates
        a compressed copy and an uncompressed copy of the file in the local 'tmp'/iplant/ directory.
    logging_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, string, optional
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
    # Set logging level, format logging, and add handler.
    logger.setLevel(level=logging_level)
    fmt = '"%(asctime)s","%(name)s","%(levelname)s","%(message)s"'
    formatter = logging.Formatter(fmt=fmt)
    formatter.converter = time.gmtime
    shandler = logging.StreamHandler(sys.stdout)
    shandler.setFormatter(formatter)
    logger.addHandler(shandler)
    logger.info("main: BEGIN_LOG")
    logger.info("main: Log format: {fmt}".format(fmt=fmt.replace('\"', '\'')))
    logger.info("main: Log date format: default ISO 8601, UTC")
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
        logger.debug(("main: compress(ipath={ipath}, itmp_iplant={itmp_iplant}," +
                      "tmp_iplant={tmp_iplant}, delete_itmp_files={delete_itmp_files}," +
                      "delete_tmp_files={delete_tmp_files})").format(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant,
                                                                     delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files))
        compress(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant, delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files)
    elif action == 'decompress':
        logger.debug(("main: decompress(ipath={ipath}, itmp_iplant={itmp_iplant}," +
                      "tmp_iplant={tmp_iplant}, delete_itmp_files={delete_itmp_files}," +
                      "delete_tmp_files={delete_tmp_files})").format(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant,
                                                                     delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files))
        decompress(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant, delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files)
    # Remove logging handler.
    logger.debug("main: END_LOG")
    logger.removeHandler(shandler)
    return None


if __name__ == '__main__':
    # Define defaults.
    defaults = {}
    defaults['logging_level'] = 'INFO'
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
    parser.add_argument('--delete_itmp_files',
                        action='store_true',
                        help=("Delete iRODS temporary files made during (de)compression. (De)compressing a file creates\n" +
                              "a compressed copy and an uncompressed copy of the file in the iRODS `itmp`/iplant/ directory."))
    parser.add_argument('--delete_tmp_files',
                        action='store_true',
                        help=("Delete local temporary files made during (de)compression. (De)compressing a file creates\n" +
                              "a compressed copy and an uncompressed copy of the file in the local 'tmp'/iplant/ directory."))
    parser.add_argument('--logging_level',
                        default=defaults['logging_level'],
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help=(("Verbosity of logging level. 'DEBUG' is most verbose; 'CRITICAL' is least." +
                               "Default: {dflt}").format(dflt=defaults['logging_level'])))
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
    main(ipath=args.ipath, action=args.action, itmp=args.itmp,
         delete_itmp_files=args.delete_itmp_files,
         delete_tmp_files=args.delete_tmp_files,
         logging_level=args.logging_level)

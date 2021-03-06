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
import time
import hashlib
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
        iRODS path to temporary directory for moving files during compression.
    tmp_iplant : string
        Local path to temporary directory for moving files during compression.
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during compression.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during compression.

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
    - Compressing a file creates a compressed copy and an uncompressed copy in both
      the iRODS `itmp_iplant`/ directory and the local `tmp_iplant`/ directory.
    
    """
    # NOTE: Input checking is handled by "if __name__ == '__main__'" section.
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
                              "do_compress = {tf}").format(tf=do_compress))
    # Compress data...
    if do_compress:
        # TODO: get isysmeta
        logger.debug("compress: do_compress = {tf}".format(tf=do_compress))
        # Define temporary file paths.
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        basename = os.path.basename(ipath)
        tmpname = timestamp+'_'+basename
        itmp_path = os.path.join(itmp_iplant, tmpname)
        tmp_path = os.path.join(tmp_iplant, tmpname)
        tmpname_gz = tmpname+'.gz'
        itmp_path_gz = itmp_path+'.gz'
        tmp_path_gz = tmp_path+'.gz'
        # Move data to temporary files, record metadata on uncompressed version, then compress.
        # NOTE: Use imv instead of icp to move data from/to `ipath` since icp will invoke acPreprocForDataObjOpen/acPostProcForCopy.
        # NOTE: Copy compressed file within `itmp_path` to leave trace of files for debugging.
        # TODO: Accommodate other compression methods and add flag option to arguments.
        # TODO: Remove "copy compressed file" step for optimization when robustly tested.
        # TODO: Check space to move to tmp local, delete oldest files that sum to size.
        logger.debug("compress: imv {src} {dst}".format(src=ipath, dst=itmp_path))
        subprocess.check_output(["imv", ipath, itmp_path])
        logger.debug("compress: iget -f -T {src} {dst}".format(src=itmp_path, dst=tmp_path))
        subprocess.check_output(["iget", "-f", "-T", itmp_path, tmp_path])
        logger.debug("compress: uncompressed_size = os.path.getsize({tmp_path})".format(tmp_path=tmp_path))
        uncompressed_size = os.path.getsize(tmp_path)
        logger.debug("compress: uncompressed_size = {usize}".format(usize=uncompressed_size))
        hash_method = 'SHA1'
        logger.debug(("compress: uncompressed_hash = _compute_hash(fpath={tmp_path}, " +
                      "algorithm={hm})").format(tmp_path=tmp_path, hm=hash_method))
        uncompressed_hash = _compute_hash(fpath=tmp_path, algorithm=hash_method)
        logger.debug("compress: uncompressed_hash = {uhash}".format(uhash=uncompressed_hash))
        logger.debug("compress: gzip --fast --force --keep {tmp_path}".format(tmp_path=tmp_path))
        subprocess.check_output(["gzip", "--fast", "--force", "--keep", tmp_path])
        logger.debug("compress: iput -T {src} {dst}".format(src=tmp_path_gz, dst=itmp_path_gz))
        subprocess.check_output(["iput", "-T", tmp_path_gz, itmp_path_gz])
        itmp_path_gz_copy = itmp_path_gz+'_copy'
        logger.debug("compress: icp {src} {dst}".format(src=itmp_path_gz, dst=itmp_path_gz_copy))
        subprocess.check_output(["icp", itmp_path_gz, itmp_path_gz_copy])
        logger.debug("compress: imv {src} {dst}".format(src=itmp_path_gz_copy, dst=ipath))
        subprocess.check_output(["imv", itmp_path_gz_copy, ipath])
        # Set metadata describing compression state. Metadata must be converted to strings.
        comments = "'This file is registered under the extension .fastq but is stored internally to iRODS with compression as .fastq.gz. This file will be decompressed upon retrieval (e.g. with iget).'"
        imeta_triplets = [('IS_COMPRESSED', 'TRUE', 'BOOL'),
                          ('COMPRESSION_METHOD', 'GZIP', 'NONE'),
                          ('UNCOMPRESSED_SIZE', uncompressed_size, 'BYTES'),
                          ('UNCOMPRESSED_HASH', uncompressed_hash, 'NONE'),
                          ('HASH_METHOD', hash_method, 'NONE'),
                          ('PARENT_FILE', itmp_path, 'NONE'),
                          ('COMMENTS', comments, 'NONE')]
        imeta_triplets = [[str(elt) for elt in triplet] for triplet in imeta_triplets]
        for (attr_name, attr_value, attr_units) in imeta_triplets:
            logger.debug("compress: imeta set -d {ipath} {an} {av} {au}".format(ipath=ipath, an=attr_name, av=attr_value, au=attr_units))
            subprocess.check_output(["imeta", "set", "-d", ipath, attr_name, attr_value, attr_units])
        # Delete temporary files if requested.
        if delete_itmp_files:
            logger.debug("compress: delete_itmp_files = {tf}".format(tf=delete_itmp_files))
            for itmp in [itmp_path, itmp_path_gz]:
                logger.debug("compress: irm -f {itmp}".format(itmp=itmp))
                subprocess.check_output(["irm", "-f", itmp])
        if delete_tmp_files:
            logger.debug("compress: delete_tmp_files = {tf}".format(tf=delete_tmp_files))
            for tmp in [tmp_path, tmp_path_gz]:
                logger.debug("compress: os.remove({tmp})".format(tmp=tmp))
                os.remove(tmp)
    # ...otherwise do nothing.
    else:
        logger.debug("compress: do_compress = {tf}".format(tf=do_compress))
    return None


def decompress(ipath, itmp_iplant, tmp_iplant, delete_itmp_files=False, delete_tmp_files=False):
    """Replace file in iRODS with decompressed version.
    
    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for compression.
    itmp_iplant : string
        iRODS path to temporary directory for moving files during compression.
    tmp_iplant : string
        Local path to temporary directory for moving files during compression.
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during decompression.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during decompression.

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
                              "do_decompress = {tf}").format(tf=do_decompress))
    # Decompress data...
    if do_decompress:
        logger.debug("decompress: do_decompress = {tf}".format(tf=do_decompress))
        # Define temporary file paths.
        timestamp = datetime.datetime.now().isoformat().replace('-', '').replace(':', '')
        basename = os.path.basename(ipath)
        tmpname = timestamp+'_'+basename
        itmp_path = os.path.join(itmp_iplant, tmpname)
        tmp_path = os.path.join(tmp_iplant, tmpname)
        compression_method_imeta = imeta_dict['COMPRESSION_METHOD']['value']
        valid_compression_methods = ['GZIP']
        # Move data to temporary files then decompress.
        # NOTE: Use imv instead of icp to move data from/to `ipath` since icp will invoke acPreprocForDataObjOpen/acPostProcForCopy.
        # NOTE: Copy compressed file within `itmp_path` to leave trace of files for debugging.
        # NOTE: File is already compressed, so rename with compressed extension (e.g. '.gz') when moving to temporary location.
        # TODO: Remove "copy compressed file" step for optimization when robustly tested.
        # TODO: Check space to move to tmp local, delete oldest files that sum to size.
        if compression_method_imeta == 'GZIP':
            tmpname_gz = tmpname+'.gz'
            itmp_path_gz = itmp_path+'.gz'
            tmp_path_gz = tmp_path+'.gz'
            logger.debug("decompress: imv {src} {dst}".format(src=ipath, dst=itmp_path_gz))
            subprocess.check_output(["imv", ipath, itmp_path_gz])
            logger.debug("decompress: iget -f -T {src} {dst}".format(src=itmp_path_gz, dst=tmp_path_gz))
            subprocess.check_output(["iget", "-f", "-T", itmp_path_gz, tmp_path_gz])
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
            logger.debug("decompress: uncompressed_size = {usize}".format(usize=uncompressed_size))
            uncompressed_size_imeta = imeta_dict['UNCOMPRESSED_SIZE']['value']
            if uncompressed_size == uncompressed_size_imeta:
                logger.debug("decompress: Uncompressed file size matches 'UNCOMPRESSED_SIZE' from imeta.")
            else:
                logger.error(("decompress: Uncompressed file size does not match 'UNCOMPRESSED_SIZE' from imeta.\n" +
                              "uncompressed_size from file  (bytes) = {usize}\n" +
                              "UNCOMPRESSED_SIZE from imeta (bytes) = {usize_im}").format(usize=uncompressed_size,
                                                                                          usize_im=uncompressed_size_imeta))
            hash_method_imeta = imeta_dict['HASH_METHOD']['value']
            logger.debug(("decompress: uncompressed_hash = _compute_hash(fpath={tmp_path}, " +
                          "algorithm={hmi})").format(tmp_path=tmp_path, hmi=hash_method_imeta))
            uncompressed_hash = _compute_hash(fpath=tmp_path, algorithm=hash_method_imeta)
            logger.debug("decompress: uncompressed_hash = {uhash}".format(uhash=uncompressed_hash))
            uncompressed_hash_imeta = imeta_dict['UNCOMPRESSED_HASH']['value']
            if uncompressed_hash == uncompressed_hash_imeta:
                logger.debug("decompress: Uncompressed hash matches 'UNCOMPRESSED_HASH' from imeta.")
            else:
                logger.error(("decompress: Uncompressed hash does not match 'UNCOMPRESSED_HASH' from imeta.\n" +
                              "HASH_METHOD from file and imeta = {hmeth_im}\n" +
                              "uncompressed_hash from file     = {uhash}\n" +
                              "UNCOMPRESSED_HASH from imeta    = {uhash_im}").format(hmeth_im=hash_method_imeta,
                                                                                     uhash=uncompressed_hash,
                                                                                     uhash_im=uncompressed_hash_imeta))
            logger.debug("decompress: iput -T {src} {dst}".format(src=tmp_path, dst=itmp_path))
            subprocess.check_output(["iput", "-T", tmp_path, itmp_path])
            itmp_path_copy = itmp_path+'_copy'
            logger.debug("decompress: icp {src} {dst}".format(src=itmp_path, dst=itmp_path_copy))
            subprocess.check_output(["icp", itmp_path, itmp_path_copy])
            logger.debug("decompress: imv {src} {dst}".format(src=itmp_path_copy, dst=ipath))
            subprocess.check_output(["imv", itmp_path_copy, ipath])
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
            for (attr_name, attr_value, attr_units) in imeta_triplets:
                logger.debug("decompress: imeta set -d {ipath} {an} {av} {au}".format(ipath=ipath, an=attr_name, av=attr_value, au=attr_units))
                subprocess.check_output(["imeta", "set", "-d", ipath, attr_name, attr_value, attr_units])
            # Delete temporary files if requested.
            if delete_itmp_files:
                logger.debug("decompress: delete_itmp_files = {tf}".format(tf=delete_itmp_files))
                for itmp in [itmp_path, itmp_path_gz]:
                    logger.debug("decompress: irm -f {itmp}".format(itmp=itmp))
                    subprocess.check_output(["irm", "-f", itmp])
            if delete_tmp_files:
                logger.debug("decompress: delete_tmp_files = {tf}".format(tf=delete_tmp_files))
                for tmp in [tmp_path, tmp_path_gz]:
                    logger.debug("decompress: os.remove({tmp})".format(tmp=tmp))
                    os.remove(tmp)
        else:
            logger.error(("decompress: File was not decompressed.\n" +
                          "tmp_path = {tmp_path}\n").format(tmp_path=tmp_path))
    # ...otherwise do nothing.
    else:
        logger.debug("decompress: do_decompress = {tf}".format(tf=do_decompress))
    return None


def main(ipath, action, itmp_iplant, tmp_iplant,
         delete_itmp_files=False, delete_tmp_files=False,
         logging_level='INFO', log_file=None):
    """Top-level function for iPlant iRODS operations.

    Parameters
    ----------
    ipath : string
        iRODS path to .fastq file for (de)compression.
    action : {'compress', 'decompress'}, string
        Action to take on file from `ipath`.
    itmp_iplant : string
        iRODS path to temporary directory for moving files during (de)compression.
    tmp_iplant : string
        Local path to temporary directory for moving files during (de)compression.
    delete_itmp_files : {False, True}, bool, optional
        Delete iRODS temporary files made during (de)compression.
    delete_tmp_files : {False, True}, bool, optional
        Delete local temporary files made during (de)compression.
    logging_level : {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}, string, optional
        Verbosity of logging level. 'DEBUG' is the most verbose; 'CRITICAL' is the least.
        Default: 'INFO'
    log_file : {None}, string, optional
        Local path for writing log in addition to stdout.
        Use to debug while executing module with iRODS icommands.
    
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
    # Set logging level, format logging, and add handlers.
    logger.setLevel(level=logging_level)
    fmt = '"%(asctime)s","%(name)s","%(levelname)s","%(message)s"'
    formatter = logging.Formatter(fmt=fmt)
    formatter.converter = time.gmtime
    shandler = logging.StreamHandler(sys.stdout)
    shandler.setFormatter(formatter)
    logger.addHandler(shandler)
    if log_file is not None:
        fhandler = logging.FileHandler(filename=log_file, mode='ab')
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)
    logger.info("main: BEGIN_LOGGING")
    logger.info("main: Log format: {fmt}".format(fmt=fmt.replace('\"', '\'')))
    logger.info("main: Log date format: default ISO 8601, UTC")
    # Perform action on file.
    if action == 'compress':
        logger.info("main: Compressing file.")
        logger.debug(("main: compress(ipath={ip}, itmp_iplant={itip}, tmp_iplant={tip}, " +
                      "delete_itmp_files={ditf}, delete_tmp_files={dtf})").format(ip=ipath, itip=itmp_iplant, tip=tmp_iplant,
                                                                                  ditf=delete_itmp_files, dtf=delete_tmp_files))
        compress(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant, delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files)
    elif action == 'decompress':
        logger.info("main: Decompressing file.")
        logger.debug(("main: decompress(ipath={ip}, itmp_iplant={itip}, tmp_iplant={tip}, " +
                      "delete_itmp_files={ditf}, delete_tmp_files={dtf})").format(ip=ipath, itip=itmp_iplant, tip=tmp_iplant,
                                                                                  ditf=delete_itmp_files, dtf=delete_tmp_files))
        decompress(ipath=ipath, itmp_iplant=itmp_iplant, tmp_iplant=tmp_iplant, delete_itmp_files=delete_itmp_files, delete_tmp_files=delete_tmp_files)
    # Remove logging handlers.
    logger.info("main: END_LOGGING")
    logger.removeHandler(shandler)
    if log_file is not None:
        logger.removeHandler(fhandler)
    return None


if __name__ == '__main__':
    # Define defaults.
    defaults = {}
    defaults['logging_level'] = 'INFO'
    defaults['log_file'] = None
    # Parse input arguments and check choices.
    parser = argparse.ArgumentParser(description="Compress or decompress .fastq file in iPlant collection.")
    parser.add_argument('--ipath',
                        required=True, type=os.path.abspath,
                        help=("iRODS path to .fastq file for (de)compression."))
    parser.add_argument('--iplant',
                        required=True, type=os.path.abspath,
                        help=("iRODS path to iplant root directory. Only files within this directory will be (de)compressed."))
    parser.add_argument('--action',
                        choices=['compress', 'decompress'],
                        required=True,
                        help=("Action to take on the file from `ipath`."))
    parser.add_argument('--itmp_iplant',
                        required=True, type=os.path.abspath,
                        help=("iRODS path to temporary directory for moving files during (de)compression."))
    parser.add_argument('--tmp_iplant',
                        required=True, type=os.path.abspath,
                        help=("Local path to temporary directory for moving files during (de)compression."))
    parser.add_argument('--delete_itmp_files',
                        action='store_true',
                        help=("Delete iRODS temporary files made during (de)compression."))
    parser.add_argument('--delete_tmp_files',
                        action='store_true',
                        help=("Delete local temporary files made during (de)compression."))
    parser.add_argument('--logging_level',
                        default=defaults['logging_level'],
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help=(("Verbosity of logging level. 'DEBUG' is the most verbose; 'CRITICAL' is the least. " +
                               "Default: {dflt}").format(dflt=defaults['logging_level'])))
    parser.add_argument('--log_file',
                        default=defaults['log_file'], type=os.path.abspath,
                        help=("Local path for writing log in addition to stdout. " +
                              "Use to debug while executing module with iRODS icommands."))
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help=("Test that module is being called correctly. Checks input then prints message to stdout. " +
                              "No actions are taken."))
    args = parser.parse_args()
    # Check input then call main function.
    print("INFO: Arguments:\n{args}".format(args=args))
    if os.path.commonprefix([args.ipath, args.iplant]) == args.iplant:
        print(("INFO: --ipath is contained within --iplant.\n" +
               "--ipath {ipath}\n" +
               "--iplant {iplant}").format(ipath=args.ipath, iplant=args.iplant))
        try:
            subprocess.check_output(["ils", args.ipath])
        except subprocess.CalledProcessError:
            raise IOError(("`ipath` does not exist or user lacks access permission:\n" +
                           "--ipath {ipath}").format(ipath=args.ipath))
        try:
            subprocess.check_output(["ils", args.itmp_iplant])
        except subprocess.CalledProcessError:
            print("INFO: Creating --itmp_iplant {itip}".format(itip=args.itmp_iplant))
            subprocess.check_output("imkdir -p {itip}".format(itip=args.itmp_iplant))
        if not os.path.exists(args.tmp_iplant):
            print("INFO: Creating --tmp_iplant {tip}".format(tip=args.tmp_iplant))
            os.makedirs(args.tmp_iplant)
        if (args.log_file is not None) and (not os.path.exists(args.log_file)):
            print("INFO: Creating --log_file {lf}".format(lf=args.log_file))
            log_file_dirname = os.path.dirname(args.log_file)
            if not os.path.exists(log_file_dirname):
                os.makedirs(log_file_dirname)
            open(args.log_file, 'ab').close()
        if args.test:
            print("INFO: --test flag given. Skipping call to main function.")
        else:
            main(ipath=args.ipath, action=args.action,
                 itmp_iplant=args.itmp_iplant, tmp_iplant=args.tmp_iplant,
                 delete_itmp_files=args.delete_itmp_files, delete_tmp_files=args.delete_tmp_files,
                 logging_level=args.logging_level, log_file=args.log_file)
    else:
        print(("INFO: --ipath is not contained within --iplant. Skipping call to main function.\n" +
               "--ipath {ipath}\n" +
               "--iplant {iplant}").format(ipath=args.ipath, iplant=args.iplant))

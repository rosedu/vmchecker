"""Functions for properly handling zip files"""


import os



# HACK: XXX: TODO: determine when python2.5 is old enough to ignore

# python2.5 has a limited zipfile implementation (for example there's
# no extractall() method

# instead on changing & bloating this code I'll just copy and use the
# zipfile from upstream import zipfile

from . import zipfile


def unzip_safely(archive_filename, destination):
    """Sanity checks before unzipping a file.

    Paths stored in a zip file may be absolute or use '..'.

    In both cases, unzipping those files may create files outside the
    specified destination. This may lead to overwritting of other
    submissions or security problems leading to overwritting of system
    files or vmchecker configuration files.

    If any such file is found, the unzippig is aborted.
    """
    z = zipfile.ZipFile(archive_filename)
    try:
        for name in z.namelist():
            if os.path.isabs(name) or name.find('..') != -1:
                raise zipfile.BadZipfile
        z.extractall(destination)
    finally:
        z.close()


def create_zip(file_handler, file_list):
    """Create a zip into the opened file_handler. The zip is comprised
    of all files specified in file_list"""
    zip_ = zipfile.ZipFile(file_handler, 'w')
    try:
        for (dest, src) in file_list:
            assert os.path.isfile(src), 'File %s is missing' % src
            zip_.write(src, dest)
    finally:
        zip_.close()


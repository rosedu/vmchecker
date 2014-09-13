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

def check_archive_for_file_override(archive_filename, \
        should_not_contain=['tests.zip', 'archive.zip', 'run.sh', 'build.sh', 'course-config', 'submission-config']):
    """Sanyity check for archive contents file names.
    We do not want to override certain file names.
    """
    z = zipfile.ZipFile(archive_filename)
    try:
        for raw_name in z.namelist():
            name = os.path.normpath(raw_name)
            # UTF8 safe?
            if name in should_not_contain:
                raise zipfile.BadZipfile
    finally:
        z.close()

def check_archive_size(archive_filename, max_file_size=10*1024*1024):
    """Sanity check for the unpacked archive file.

    We are checking without unpacking the archive.
    """
    z = zipfile.ZipFile(archive_filename)
    size = 0
    try:
        for zinfo in z.filelist:
            size += zinfo.file_size
        if size > max_file_size:
            raise zipfile.LargeZipFile
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


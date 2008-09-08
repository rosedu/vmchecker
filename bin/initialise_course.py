#! /usr/bin/python
# Initialises the directory path for one course 

__author__ = 'Ana Savu, ana.savu86@gmail.com'


import os
import misc


def main():
    
    base_path = misc.vmchecker_root()

    # if the directories exist the script fails
    assert not(os.path.isdir(os.path.join(base_path, 'unchecked'))), (
        'Directorul %s exista' % (
            os.path.join(base_path, 'unchecked')))
    os.mkdir(os.path.join(base_path, 'unchecked'))

    assert not(os.path.isdir(os.path.join(base_path, 'back'))), (
        'Directorul %s exista' % (
            os.path.join(base_path, 'back')))
    os.mkdir(os.path.join(base_path, 'back'))

    assert not(os.path.isdir(os.path.join(base_path, 'checked'))), (
        'Directorul %s exista' % (
            os.path.join(base_path, 'checked')))
    os.mkdir(os.path.join(base_path, 'checked'))

    assert not(os.path.isdir(os.path.join(base_path, 'tests'))), (
        'Directorul %s exista' % (
            os.path.join(base_path, 'tests')))
    os.mkdir(os.path.join(base_path, 'tests'))

if __name__ == '__main__':
    main()

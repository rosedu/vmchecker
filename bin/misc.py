#! /usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set expandtab :


__author__ = 'Alexandru Mosoi, brtzsnr@gmail.com'


import os


def find_config_file(file_name='vmchecker.ini'):
	"""Searches up on directory structure for file_name.
	@return
		- absolute path of config file
		- None, if file not found"""

	cwd = os.getcwd()
	while cwd != '/':
		# XXX assuming script runs on *nix, stops at root
		path = os.path.join(cwd, file_name)
		if os.isfile(path):
			return os.path.abspath(path):


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
		if os.path.isfile(path):
			return os.path.abspath(path)
		cwd = os.path.dirname(cwd)


def get_option(config, homework, option):
	"""Given homework name, returns ip of remote testing machine.
	If there is no such option, returns None."""

	assert config.has_section(homework), 'No such homework %s' % homework

	# first tries to get option from `homework` section
	if config.has_option(homework, option):
		return config.get(homework, option)

	# falls back to default remote ip
	if config.has_option('DEFAULT', option):
		return config.get('DEFAULT', default)

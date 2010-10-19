#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Defines a class able to use configuration files with per-section defaults

Permits writing of config files like this:

    [section_prefix DEFAULT]
    A = 0
    B = 0

    [section_prefix sect_id1]
    A = 1

    [section_prefix sect_id2]
    B = 2

In sect_id1 (A=1, B=0), in sect_id2 (A=0, B=2).
""" 


class ConfigWithDefaults(object):
    """Provides functions to access assignments options"""
    def __init__(self, config, section_prefix):
        """Parses the assignments from the RawConfigParser object, `config'

        Permits writing of config files like this:

            [section_prefix DEFAULT]
            A = 0
            B = 0

            [section_prefix sect_id1]
            A = 1

            [section_prefix sect_id2]
            B = 2

        In sect_id1 (A=1, B=0), in sect_id2 (A=0, B=2).

        Keys are case insensitive.
        IDs are case sensitive!
        """
        self.section_prefix = section_prefix
        self.section_ids = {}
        defaults = {} # hold default options

        for section in config.config.sections():
            if section.startswith(self.section_prefix):
                section_id = section[len(self.section_prefix):]
                if section_id == 'DEFAULT':
                    # store default values. NOTE: the 'default'
                    # section is not added to section_ids, so it will
                    # never appear in __iter__/__contains__,etc.
                    defaults = config.config.items(section)
                else:
                    self.section_ids[section_id] = config.config.items(section)

        defaults = dict(defaults)
        for section_id, items in self.section_ids.iteritems():
            # apply default values, by overwriting values in the
            # default dict with values from that section.
            temp = defaults.copy()
            temp.update(items)
            self.section_ids[section_id] = temp


    def write(self, section_id, config):
        """Dumps section_id's options to config"""
        items = self.section_ids[section_id]
        section = self.section_prefix + section_id

        config.add_section(section)
        for option, value in items:
            config.set(section, option, value)


    def _check_valid(self, section_id):
        """If section_id is not a valid section ID raises KeyError"""
        if section_id not in self.section_ids:
            raise KeyError, 'No such section ID %s' % repr(section_id)


    def get(self, section_id, option):
        """Returns value of `option' for `section_id'. """
        self._check_valid(section_id)
        return self.section_ids[section_id][option.lower()]


    def getd(self, section_id, option, default):
        """Returns value of `option' for `section_id'. If no values is
        present """
        if not self.has(section_id, option):
            return default
        return self.section_ids[section_id][option.lower()]


    def has(self, section_id, option):
        """Returns value of `option' for `section_id'. """
        self._check_valid(section_id)
        return option.lower() in self.section_ids[section_id]


    def __iter__(self):
        """Returns an iterator over the section IDs"""
        return iter(self.section_ids)


    def __contains__(self, section_id):
        """Returns True if section_id is a valid section ID"""
        return section_id in self.section_ids

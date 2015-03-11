#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import os

LIST_SEPARATOR = ' '

class Config:
    """An object that encapsulates parsing of the config file of a course"""
    def __init__(self, config_file_ = None, config = None):
        if config != None:
            # Copy the underlying ConfigParser from the given instance
            self.config = config.config
            self.config_file = config.config_file
        else:
            self.config = ConfigParser.RawConfigParser()
            if config_file_ != None:
                self.config_file = config_file_
                with open(os.path.expanduser(config_file_)) as handle:
                    self.config.readfp(handle)

    def get(self, section, option, default=None):
        """A convenient wrapper for config.get()"""
        if not self.config.has_option(section, option) and default != None:
            return default
        return self.config.get(section, option)

    def get_boolean(self, section, option, default=None):
        val = self.get(section, option, default).strip().lower()
        return (val == 'yes') or (val == 'y') or (val == 'true')

    def get_int(self, section, option, default=None):
        return int(self.get(section, option, default))

    def get_list(self, section, option, default=None):
        return self.get(section, option, default).split(LIST_SEPARATOR)

    def get_prefixed_list(self, section, option, default=None):
        result = []
        for opt in self.config.options(section):
            if opt.lower().startswith(option.lower()):
                result.append(self.get(section, opt, default))

        return result


class ConfigWithDefaults(Config):
    """Defines a class able to use configuration files with per-section defaults"""
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


    def get(self, section_id, option, default=None):
        """Returns value of `option' for `section_id'. """
        if default != None and not self.has(section_id, option):
            return default
        self._check_valid(section_id)
        return self.section_ids[section_id][option.lower()]


    def getd(self, section_id, option, default):
        """Returns value of `option' for `section_id'. If no values are
        present """
        if not self.has(section_id, option):
            return default
        return self.section_ids[section_id][option.lower()]


    def has(self, section_id, option):
        """Returns value of `option' for `section_id'. """
        self._check_valid(section_id)
        return option.lower() in self.section_ids[section_id]

    def items(self, section_id):
        """Return the items in this section."""
        if not self.section_ids.has_key(section_id):
            return default
        return self.section_ids[section_id].items()

    def __iter__(self):
        """Returns an iterator over the section IDs"""
        return iter(self.section_ids)


    def __contains__(self, section_id):
        """Returns True if section_id is a valid section ID"""
        return section_id in self.section_ids

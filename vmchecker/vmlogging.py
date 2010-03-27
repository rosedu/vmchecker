"""Routines for common vmchecker logging tasks"""

import sys
import logging


class _NullHandler(logging.Handler):
    """A class to use in the vmchecker library when application writter
    using the library does not provide a handler"""

    def emit(self, record):
        """Don't do noting with the data, you're a null logger"""
        pass


def create_module_logger(name):
    """Create a logger valid for vmchecker modules:

    It must have a default handler, because, it the application does
    not provide any, logging will throw exceptions.
    """
    logger = logging.getLogger('vmchecker.' + name)
    logger.addHandler(_NullHandler())
    return logger


def create_script_sdtout_logger():
    """Create a logger for scripts that use vmchecker modules. The
    logger spits all to stdout.
    """
    logger = logging.getLogger('vmchecker')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    return logger


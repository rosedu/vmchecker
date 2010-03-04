import logging

"""A class to use in the vmchecker library when application writter
using the library does not provide a handler"""

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

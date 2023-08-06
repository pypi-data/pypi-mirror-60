# -*- coding: utf-8 -*-

"""
Static functions for using the logger. The logger is supposed to be set up
with lazy loading, and to be configured via the generated .env file.
"""

from .logger import Logger


def debug(message, data=None):
    __log_with_level(message, data, Logger.LEVEL_DEBUG)


def info(message, data=None):
    __log_with_level(message, data, Logger.LEVEL_INFO)


def warning(message, data=None):
    __log_with_level(message, data, Logger.LEVEL_WARNING)


def error(message, data=None):
    __log_with_level(message, data, Logger.LEVEL_ERROR)


def critical(message, data=None):
    __log_with_level(message, data, Logger.LEVEL_CRITICAL)


def get_instance():
    return Logger.get_instance()


def __log_with_level(message, data, level):
    logger = Logger.get_instance()
    logger.write(message, data, level)

# -*- coding: utf-8 -*-

"""
An instance of the logger. Wraps the Python logger and some other 3rd-P integrations.
"""

import color
import sys
import dict_expander


class Logger:

    COLUMN_PADDING = 2  # Minimum width of column when writing to console.

    # Drawing the dictionaries.
    BOX_STEM = "├"
    BOX_STEM_END = "└"
    BOX_BRANCH = "─"
    BOX_BRANCH_DOWN = "┬"
    LOG_BULLET = "⚫"  # "┃"

    # Log level constants.
    LEVEL_DEBUG: int = 10
    LEVEL_INFO: int = 20
    LEVEL_WARNING: int = 30
    LEVEL_ERROR: int = 40
    LEVEL_CRITICAL: int = 50

    LEVEL_NAME = {
        LEVEL_INFO: "INFO",
        LEVEL_WARNING: "WARNING",
        LEVEL_ERROR: "ERROR",
        LEVEL_CRITICAL: "CRITICAL",
        LEVEL_DEBUG: "DEBUG"
    }

    LEVEL_COLOR = {
        LEVEL_INFO: color.Color.BLUE,
        LEVEL_WARNING: color.Color.YELLOW,
        LEVEL_ERROR: color.Color.RED,
        LEVEL_CRITICAL: color.Color.RED,
        LEVEL_DEBUG: color.Color.GREEN,
    }

    # ======================================================================================================================
    # Singleton Access
    # ======================================================================================================================

    _instance = None

    @staticmethod
    def get_instance() -> "Logger":
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance

    @staticmethod
    def format_log_name(x: str) -> str:
        return f"[{x}]"

    def __init__(self):
        # Native Python logging module.
        self.file_logger = None
        self.file_logging_map = None

        self.with_color = True
        self.with_level_prefix = True

        self.index: int = 1

    # ======================================================================================================================
    # Loading and Initialization
    # ======================================================================================================================

    def write(self, message, data, level: int):
        # Parse the data first.
        if data is not None:
            if type(data) is not dict:
                message = f"{message}: {data}"
                data = None

        self.console_write(message, data, level, with_color=self.with_color)

    def console_write(self, message, data: dict, level: int, with_color: bool = False):
        """ Custom function to write message to console. """

        # Write the Header.
        self.console_write_line(message, level, with_color)

        # Write the Items.
        if data is not None:
            stem_color = None if not with_color else self.LEVEL_COLOR[level]
            expanded_lines = dict_expander.expand(key=None, data=data, stem_color=stem_color)
            for x in expanded_lines:
                print(x)
            sys.stdout.flush()

    def console_write_line(self, content, level, with_color: bool = False):

        prefix = self.format_log_name(self.LEVEL_NAME[level])
        pad_length = max(0, self.COLUMN_PADDING - len(prefix))
        prefix += " " * pad_length
        self.index += 1

        if with_color:
            if level > self.LEVEL_INFO:
                content = "{} {}".format(prefix, content)
                content = self.set_level_color(content, level)
            else:
                prefix = self.set_level_color(prefix, level)
                content = "{} {}".format(prefix, content)
        else:
            content = "{} {}".format(prefix, content)

        print(content)
        sys.stdout.flush()

    def set_level_color(self, content, level):

        content = str(content)

        if level == self.LEVEL_INFO:
            return color.blue(content)

        if level == self.LEVEL_DEBUG:
            return color.green(content)

        if level == self.LEVEL_WARNING:
            return color.yellow(content)

        if level == self.LEVEL_ERROR:
            return color.red(content)

        if level == self.LEVEL_CRITICAL:
            return color.red(content)

        return content

"""
Definition of custom logger of :mod:`shapepy` module.
"""

from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from functools import wraps
from typing import Dict, Optional


# pylint: disable=too-few-public-methods
class LogConfiguration:
    """Contains the configuration values for the loggers"""

    indent_str = "|   "
    log_enabled = False


class IndentingLoggerAdapter(logging.LoggerAdapter):
    """
    An indenting logger that insert spaces depending on the
    value of `indent_level`.
    It is used to keep track of the stack of function calls
    """

    instances: Dict[str, IndentingLoggerAdapter] = {}
    indent_level = 0

    def __init__(self, logger, extra=None):
        super().__init__(logger, extra)
        self.instances[logger.name] = self

    def process(self, msg, kwargs):
        """
        Inserts spaces proportional to `indent_level` before the message
        """
        indent_str = LogConfiguration.indent_str * self.indent_level
        return f"{indent_str}{msg}", kwargs


def set_level(base: str, /, *, level: logging._Level):
    """
    Sets the level of all the shapepy loggers into given level

    Parameters
    ----------
    base: str
        The base name to filter the
    level: logging._Level
        One from 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'

    Example
    -------
    >>> set_level("INFO")
    >>> set_level("ERROR")
    """
    for name, logger in IndentingLoggerAdapter.instances.items():
        if base in name:
            logger.setLevel(level)


def get_logger(
    name: Optional[str] = None, /, *, level: Optional[logging._Level] = None
) -> IndentingLoggerAdapter:
    """
    Equivalent to `logging.getLogger`, but gives the standard
    `shapepy` logger if no name is given
    """
    if name is None:
        name = "shapepy"
    if name not in IndentingLoggerAdapter.instances:
        setup_logger(name)
    logger = IndentingLoggerAdapter.instances[name]
    if level is not None:
        logger.setLevel(level)
    return logger


def setup_logger(name, level=logging.INFO):
    """
    Setups the indenting logger with given level
    and adds the file handler 'shapepy.log' to store
    """
    logger = logging.getLogger(name)
    adapter = IndentingLoggerAdapter(logger)
    adapter.logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
    )
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
    # formatter = logging.Formatter("%(asctime)s - %(message)s")
    formatter = logging.Formatter("%(name)s:%(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)
    adapter.logger.addHandler(stdout_handler)

    file_handler = logging.FileHandler(
        "shapepy.log", "w" if (name == "shapepy") else "a"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    adapter.logger.addHandler(file_handler)


@contextmanager
def indent():
    """
    An indent context manager, that increases the indentation level when
    entering the block with `with" command and decreases when leaving it
    """
    IndentingLoggerAdapter.indent_level += 1
    try:
        yield
    finally:
        IndentingLoggerAdapter.indent_level -= 1


@contextmanager
def enable_logger(base: str, /, *, level: logging._Level = "DEBUG"):
    """Enables temporarily the given logger"""
    current_enable = LogConfiguration.log_enabled
    current_levels = {}
    for name, logger in IndentingLoggerAdapter.instances.items():
        if base in name:
            current_levels[name] = logger.getEffectiveLevel()
    try:
        LogConfiguration.log_enabled = True
        for name, logger in IndentingLoggerAdapter.instances.items():
            if name in current_levels:
                logger.setLevel(level)
        yield
    finally:
        LogConfiguration.log_enabled = current_enable
        for name, logger in IndentingLoggerAdapter.instances.items():
            if name in current_levels:
                logger.setLevel(current_levels[name])


# Create decorator to use in functions
def debug(name: Optional[str] = None, /, *, maxdepth: Optional[int] = None):
    """
    Decorator to automatically log in debug mode the input and outputs
    of the given function in a indentation mode.

    Parameters
    ----------
    name : str
        The name of the logger, something like "shapepy.module.submodule"
    maxdepth : Optional[int], default = None
        The maximal depth to log the function. It's used as a method to
        clean the logger when the functions stack of calls becomes too big
    """
    logger = get_logger(name)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not LogConfiguration.log_enabled or (
                maxdepth is not None and logger.indent_level > maxdepth
            ):
                return func(*args, **kwargs)
            tipos = [repr(arg) for arg in args]
            tipos += [
                str(key) + "=" + repr(val) for key, val in kwargs.items()
            ]
            if maxdepth is None or logger.indent_level < maxdepth:
                logger.debug(
                    f"Compute {func.__qualname__}({', '.join(tipos)})"
                )
            try:
                with indent():
                    result = func(*args, **kwargs)
                if maxdepth is None or logger.indent_level < maxdepth:
                    logger.debug("Return = " + repr(result))
                return result
            except Exception as e:
                logger.debug("Error = " + repr(e))
                raise e

        return wrapper

    return decorator

"""
Definition of custom logger of :mod:`shapepy` module.
"""

from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from functools import wraps
from typing import Dict, Optional


class IndentingLoggerAdapter(logging.LoggerAdapter):
    """
    An indenting logger that insert spaces depending on the
    value of `indent_level`.
    It is used to keep track of the stack of function calls
    """

    instances: Dict[[str], IndentingLoggerAdapter] = {}
    indent_level = 0

    def __init__(self, logger, extra=None):
        super().__init__(logger, extra)
        self.instances[logger.name] = self

    def process(self, msg, kwargs):
        """
        Inserts spaces proportional to `indent_level` before the message
        """
        indent_str = "    " * self.indent_level
        return f"{indent_str}{msg}", kwargs


def get_logger(name: Optional[str] = None) -> IndentingLoggerAdapter:
    """
    Equivalent to `logging.getLogger`, but gives the standard
    `shapepy` logger if no name is given
    """
    if name is None:
        name = "shapepy"
    if name not in IndentingLoggerAdapter.instances:
        setup_logger(name)
    return IndentingLoggerAdapter.instances[name]


def setup_logger(name, level=logging.INFO):
    """
    Setups the indenting logger with given level
    and adds the file handler 'shapepy.log' to store
    """
    logger = logging.getLogger(name)
    adapter = IndentingLoggerAdapter(logger)
    adapter.logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    formatter = logging.Formatter("%(message)s")

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


# Create decorator to use in functions
def debug(name: Optional[str] = None, maxdepth: Optional[int] = None):
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
        If
    """
    logger = get_logger(name)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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

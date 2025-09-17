"""Configuration file for the bool2d package"""

from contextlib import contextmanager


# pylint: disable=too-few-public-methods
class Config:
    """Static class that contains flags"""

    clean = {
        "add": True,
        "or": False,
        "xor": True,
        "and": False,
        "sub": True,
        "mul": True,
        "neg": True,
        "inv": False,
    }

    auto_clean = True


@contextmanager
def set_auto_clean(value: bool):
    """Function that enables/disables temporarily the auto clean"""
    value = bool(value)
    old = Config.clean.copy()
    for key in Config.clean:
        Config.clean[key] = value
    try:
        yield
    finally:
        for key in Config.clean:
            Config.clean[key] = old[key]

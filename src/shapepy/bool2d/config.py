"""Configuration file for the bool2d package"""

from contextlib import contextmanager


# pylint: disable=too-few-public-methods
class Config:
    """Static class that contains flags"""

    clean = {
        "add": True,
        "or": True,
        "xor": True,
        "and": True,
        "sub": True,
        "mul": True,
        "neg": True,
        "inv": True,
    }

    auto_clean = True


@contextmanager
def disable_auto_clean():
    """Function that disables temporarily the auto clean"""
    old = Config.clean.copy()
    for key in Config.clean:
        Config.clean[key] = False
    try:
        yield
    finally:
        for key in Config.clean:
            Config.clean[key] = old[key]

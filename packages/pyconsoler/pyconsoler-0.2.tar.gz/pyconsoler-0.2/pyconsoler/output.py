"""Output helper functions."""

import asyncio
import logging
import time

from colorama import Style

from pyconsoler.const import RIGHT_PAD

_LOGGER = logging.getLogger(__name__)



def _out(text, color=None, end="\n"):
    if color:
        print(color + text, end=end)
    else:
        print(Style.RESET_ALL + text, end=end)


async def print_waiting_countdown(delay: int):
    """Print a waiting message including a countdown timer

    Args:
        delay The amount of seconds to countdown.

    Returns:

    """
    for i in range(delay, 0, -1):
        print(f"waiting for {i} seconds\r", end="", flush=True)
        await asyncio.sleep(1)
    print("\n", end="")


def print_key_value(key, value, spacing=RIGHT_PAD, color=None):
    """Print a key-value with the value indented from the left border with a certain
        spacing

    Args:
        key: The key to print out
        value: The value to print out
        spacing: Print the value with an indentation relative to the left border
        color: A colorama color

    """
    _str = str(key).ljust(spacing) + str(value)
    _out(_str, color=color)


def get_time_stamp(
    time_sec=None,
    add_date=True,
    add_time=True,
    date_sep="-",
    time_sep=":",
    date_time_sep=" ",
) -> str:
    if time_sec is None:
        _date = time.strftime(f"%Y{date_sep}%m{date_sep}%d")
        _time = time.strftime(f"%H{time_sep}%M{time_sep}%S")
    else:
        _date = time.strftime(f"%Y{date_sep}%m{date_sep}%d", time.localtime(time_sec))
        _time = time.strftime(f"%H{time_sep}%M{time_sep}%S", time.localtime(time_sec))

    if add_date and add_time:
        return f"{_date}{date_time_sep}{_time}"
    elif add_date:
        return _date
    else:
        return _time

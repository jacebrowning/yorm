"""Integration tests for the `yorm` package."""

import time
import logging


def strip(text, tabs=None, end='\n'):
    """Strip leading whitespace indentation on multiline string literals."""
    lines = text.strip().splitlines()
    for index in range(len(lines)):
        if not tabs:
            tabs = lines[index].count(' ' * 4)
        lines[index] = lines[index].replace(' ' * tabs * 4, '')
    return '\n'.join(lines) + end


def refresh_file_modification_times(seconds=1.1):
    """Sleep to allow file modification times to refresh."""
    logging.info("delaying for %s second%s...", seconds,
                 "" if seconds == 1 else "s")
    time.sleep(seconds)

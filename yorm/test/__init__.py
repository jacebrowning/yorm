"""Unit tests for the `yorm` package."""

import time
import logging


def strip(text, tabs=None, end='\n'):
    """Strip leading whitespace indentation on multiline string literals."""
    lines = []

    for line in text.strip().splitlines():
        if not tabs:
            tabs = line.count(' ' * 4)
        lines.append(line.replace(' ' * tabs * 4, ''))

    return '\n'.join(lines) + end


def refresh_file_modification_times(seconds=1.1):
    """Sleep to allow file modification times to refresh."""
    logging.info("delaying for %s second%s...", seconds,
                 "" if seconds == 1 else "s")
    time.sleep(seconds)

"""Unit tests for the `yorm` package."""

import os
import time
import logging

import expecter


def is_none(x):
    return x is None


def is_true(x):
    return x is True


def is_false(x):
    return x is False


def exists(x):
    return os.path.exists(x)


def missing(x):
    return not os.path.exists(x)


expecter.add_expectation(is_none)
expecter.add_expectation(is_true)
expecter.add_expectation(is_false)
expecter.add_expectation(exists)
expecter.add_expectation(missing)


def strip(text, tabs=None, end='\n'):
    """Strip leading whitespace indentation on multiline string literals."""
    lines = []

    for line in text.strip().splitlines():
        if not tabs:
            tabs = line.count(' ' * 4)
        lines.append(line.replace(' ' * tabs * 4, '', 1))

    return '\n'.join(lines) + end


def refresh_file_modification_times(seconds=1.1):
    """Sleep to allow file modification times to refresh."""
    logging.info("Delaying for %s second%s...", seconds,
                 "" if seconds == 1 else "s")
    time.sleep(seconds)

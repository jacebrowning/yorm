#!/usr/bin/env python

"""Tests for the `yorm` package."""


def strip(text, tabs=None, end='\n'):
    """Strip leading whitespace indentation on multiline string literals."""
    lines = text.strip().splitlines()
    for index in range(len(lines)):
        if not tabs:
            tabs = lines[index].count(' ' * 4)
        lines[index] = lines[index].replace(' ' * tabs * 4, '')
    return '\n'.join(lines) + end

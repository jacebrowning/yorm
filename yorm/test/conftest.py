from copy import deepcopy

import pytest

import yorm


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


# @pytest.yield_fixture(autouse=True)
# def backup_restore_attrs():
#     attrs = deepcopy(yorm.common.ATTRS)
#     yield
#     yorm.common.ATTRS = attrs

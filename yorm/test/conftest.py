"""Unit tests configuration file."""

import logging


def pytest_configure(config):
    """Conigure logging and silence verbose test runner output."""
    logging.basicConfig(
        level=logging.DEBUG - 1,
        format="[%(levelname)-8s] (%(name)s @%(lineno)4d) %(message)s",
    )

    terminal = config.pluginmanager.getplugin('terminal')
    base = terminal.TerminalReporter

    class QuietReporter(base):
        """A py.test reporting that only shows dots when running tests."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter

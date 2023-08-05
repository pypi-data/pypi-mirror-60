#!/usr/bin/env python

"""Tests for `test_python_200123` package."""


import unittest
from click.testing import CliRunner

from test_python_200123 import test_python_200123
from test_python_200123 import cli


class TestTest_python_200123(unittest.TestCase):
    """Tests for `test_python_200123` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'test_python_200123.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from click.testing import CliRunner

from malabar.malabar import cli
from malabar.config import CONFIGURATION_FILE_NAME


def test_main():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert 'Usage:' in result.output
    assert result.exit_code == 0


def test_init():
    runner = CliRunner()
    result = runner.invoke(cli, ['init'])

    assert 'Init' in result.output
    assert CONFIGURATION_FILE_NAME in result.output
    assert result.exit_code == 0

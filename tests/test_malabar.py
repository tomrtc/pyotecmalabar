#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from click.testing import CliRunner

from malabar.malabar import cli


def test_main():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert 'Usage:' in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli, ['init'])

    assert 'init' in result.output
    assert result.exit_code == 0

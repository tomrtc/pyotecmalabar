#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from click.testing import CliRunner

from malabar.__main__ import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.output == ''
    assert result.exit_code == -1

    result = runner.invoke(main, ['init'])

    assert result.output == ''
    assert result.exit_code == 0

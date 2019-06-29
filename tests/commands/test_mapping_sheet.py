import sys
from io import StringIO
from unittest.mock import patch

import pytest

from ocdskit.cli.__main__ import main
from tests import path, read


def test_command(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', '--infer-required', path('release-schema.json')])
        main()

    assert actual.getvalue() == read('mapping-sheet.csv', newline='')


def test_command_order_by(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', '--order-by', 'path',
                                          '--infer-required', path('release-schema.json')])
        main()

    assert actual.getvalue() == read('mapping-sheet_order-by.csv', newline='')


def test_command_oc4ids(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', path('project-schema.json')])
        main()

    assert actual.getvalue() == read('mapping-sheet_oc4ids.csv', newline='')


def test_command_bods(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', '--order-by', 'path',
                                          path('bods/person-statement.json')])
        main()

    assert actual.getvalue() == read('mapping-sheet_bods.csv', newline='')


def test_command_sedl(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', path('sedl-schema.json')])
        main()

    assert actual.getvalue() == read('mapping-sheet_sedl.csv', newline='')


def test_command_order_by_nonexistent(monkeypatch, caplog):
    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', 'mapping-sheet', '--order-by', 'nonexistent',
                                              path('release-schema.json')])
            main()

    assert actual.getvalue() == ''
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "the column 'nonexistent' doesn't exist – did you make a typo?"
    assert excinfo.value.code == 1

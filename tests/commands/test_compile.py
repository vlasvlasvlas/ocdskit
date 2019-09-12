import json
import re
import sys
from io import BytesIO, StringIO, TextIOWrapper
from unittest.mock import patch

import pytest

from ocdskit.cli.__main__ import main
from tests import read


@pytest.mark.vcr()
def test_command(monkeypatch):
    stdin = read('realdata/release-package-1.json', 'rb') + read('realdata/release-package-2.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', '--ascii', 'compile'])
        main()

    assert actual.getvalue() == read('realdata/compiled-release-1.json') + read('realdata/compiled-release-2.json')


@pytest.mark.vcr()
def test_command_versioned(monkeypatch):
    stdin = read('realdata/release-package-1.json', 'rb') + read('realdata/release-package-2.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', '--ascii', 'compile', '--versioned'])
        main()

    assert actual.getvalue() == read('realdata/versioned-release-1.json') + read('realdata/versioned-release-2.json')


@pytest.mark.vcr()
def test_command_package(monkeypatch):
    stdin = read('realdata/release-package-1.json', 'rb') + read('realdata/release-package-2.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package'])
        main()

    assert actual.getvalue() == read('realdata/record-package_package.json')


@pytest.mark.vcr()
def test_command_package_uri_published_date(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package', '--uri', 'http://example.com/x.json',
                                          '--published-date', '2010-01-01T00:00:00Z'])
        main()

    package = json.loads(actual.getvalue())
    assert package['uri'] == 'http://example.com/x.json'
    assert package['publishedDate'] == '2010-01-01T00:00:00Z'


@pytest.mark.vcr()
def test_command_package_publisher(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package', '--publisher-name', 'Acme Inc.'])
        main()

    package = json.loads(actual.getvalue())
    assert package['publisher']['name'] == 'Acme Inc.'


@pytest.mark.vcr()
def test_command_package_linked_releases(monkeypatch):
    stdin = read('realdata/release-package-1.json', 'rb') + read('realdata/release-package-2.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package', '--linked-releases'])
        main()

    assert actual.getvalue() == read('realdata/record-package_linked-releases.json')


@pytest.mark.vcr()
def test_command_package_versioned(monkeypatch):
    stdin = read('realdata/release-package-1.json', 'rb') + read('realdata/release-package-2.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package', '--versioned'])
        main()

    assert actual.getvalue() == read('realdata/record-package_versioned.json')


@pytest.mark.vcr()
def test_command_version_mismatch(monkeypatch, caplog):
    stdin = read('realdata/release-package_1.1-1.json', 'rb') + read('realdata/release-package_1.0-1.json', 'rb')

    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile', '--package', '--versioned'])
            main()

    assert actual.getvalue() == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "item 1: version error: this package uses version 1.0, but earlier packages " \
                                        "used version 1.1\nTry first upgrading packages to the same version:\n  cat " \
                                        "file [file ...] | ocdskit upgrade 1.0:1.1 | ocdskit compile --package " \
                                        "--versioned"
    assert excinfo.value.code == 1


def test_command_help(monkeypatch, caplog):
    stdin = read('release-package_minimal.json', 'rb')

    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', '--help'])
            main()

    assert actual.getvalue().startswith('usage: ocdskit [-h] ')

    assert len(caplog.records) == 0
    assert excinfo.value.code == 0


@pytest.mark.vcr()
def test_command_pretty(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', '--pretty', 'compile'])
        main()

    assert actual.getvalue() == read('compile_pretty_minimal.json')


def test_command_bad_encoding_iso_8859_1(monkeypatch, caplog):
    stdin = read('realdata/release-package_encoding-iso-8859-1.json', 'rb')

    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile'])
            main()

    assert actual.getvalue() == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "encoding error: 'utf-8' codec can't decode byte 0xd3 in position 83: " \
                                        "invalid continuation byte\nTry saving the inputs as UTF-8?"
    assert excinfo.value.code == 1


def test_command_multiline_input(monkeypatch, caplog):
    stdin = b'{\n  "releases": [\n    {\n      "ocid": "x",\n      "date": "2001-02-03T00:00:00Z"\n    }\n  ]\n}'

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile'])
        main()

    assert actual.getvalue() == '{"tag":["compiled"],"id":"x-2001-02-03T00:00:00Z","date":"2001-02-03T00:00:00Z","ocid":"x"}\n'  # noqa


def test_command_invalid_json(monkeypatch, caplog):
    with caplog.at_level('INFO'):
        stdin = read('release-package_minimal.json', 'rb') + b'\n{\n'

        with pytest.raises(SystemExit) as excinfo:
            with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:  # noqa
                monkeypatch.setattr(sys, 'argv', ['ocdskit', 'compile'])
                main()

        assert actual.getvalue() == ''

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'CRITICAL'
        assert re.search(r'^JSON error: parse error: premature EOF[ \n]+\(right here\) ------\^\n$',
                         caplog.records[0].message)
        assert excinfo.value.code == 1

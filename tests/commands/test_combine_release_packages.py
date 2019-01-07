import json
import sys
from io import BytesIO, StringIO, TextIOWrapper
from unittest.mock import patch

from ocdskit.cli.__main__ import main
from tests import read


def test_command(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb') + \
            read('release-package_maximal.json', 'rb') + \
            read('release-package_extensions.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'combine-release-packages'])
        main()

    assert actual.getvalue() == read('combine-release-packages_minimal-maximal-extensions.json')


def test_command_no_extensions(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'combine-release-packages'])
        main()

    assert actual.getvalue() == read('combine-release-packages_minimal.json')


def test_command_uri_published_date(monkeypatch):
    stdin = read('release-package_minimal.json', 'rb')

    with patch('sys.stdin', TextIOWrapper(BytesIO(stdin))), patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', ['ocdskit', 'combine-release-packages', '--uri', 'http://example.com/x.json',
                                          '--published-date', '2010-01-01T00:00:00Z'])
        main()

    package = json.loads(actual.getvalue())
    assert package['uri'] == 'http://example.com/x.json'
    assert package['publishedDate'] == '2010-01-01T00:00:00Z'

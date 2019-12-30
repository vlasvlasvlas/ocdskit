import logging
import os.path

import pytest

import ocdskit.combine

logger = logging.getLogger('vcr')
logger.setLevel(logging.WARNING)


@pytest.fixture()
def vcr_cassette_name(request):
    return '{}-{}'.format(os.path.splitext(os.path.basename(request.node.fspath))[0], request.node.name)


@pytest.fixture(params=[True, False])
def sqlite(request, monkeypatch):
    ocdskit.combine.using_sqlite = request.param

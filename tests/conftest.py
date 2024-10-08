import os
import pathlib

import pytest

TESTS_DIR = pathlib.Path(__file__).parent.resolve()


@pytest.fixture
def site_config_dir():
    return os.path.join(TESTS_DIR, "fixtures_site_config")


@pytest.fixture
def test_site_config_path():
    return os.path.join(TESTS_DIR, "fixtures_site_config", ".test.com.txt")

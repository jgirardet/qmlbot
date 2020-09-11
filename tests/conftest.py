from pathlib import Path
import pytest


@pytest.fixture
def dir_test():
    return Path(__file__).parent / "dir_test"
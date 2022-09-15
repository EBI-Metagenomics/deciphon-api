import importlib.metadata

from deciphon_api import __name__, __version__


def test_version():
    assert __version__ == importlib.metadata.version(__name__)

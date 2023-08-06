import pkg_resources

from .main import main

try:
    __version__ = pkg_resources.get_distribution("pytest-chdir").version
except pkg_resources.DistributionNotFound:
    __version__ = "develop"

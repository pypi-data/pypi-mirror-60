import pkg_resources

from .plugin import define_chdir_fixture

try:
    __version__ = pkg_resources.get_distribution("pytest-chdir").version
except pkg_resources.DistributionNotFound:
    __version__ = "develop"

from .read_only_decorator import read_only
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['read_only', ]

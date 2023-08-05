# -*- coding: utf-8 -*-
'''
PyTest Salt Plugin
'''

# Import Python libs
import re

# Import pytest salt libs
from pytestsalt._version import get_versions

# Store the version attribute
__version__ = get_versions()['version']
del get_versions

# Define __version_info__ attribute
VERSION_INFO_REGEX = re.compile(
    r'(?P<year>[\d]{4})\.(?P<month>[\d]{1,2})\.(?P<day>[\d]{1,2})'
    r'(?:\.dev0\+(?P<commits>[\d]+)\.(?:.*))?'
)
try:
    __version_info__ = tuple([int(p) for p in VERSION_INFO_REGEX.match(__version__).groups() if p])
except AttributeError:
    __version_info__ = (-1, -1, -1)
finally:
    del VERSION_INFO_REGEX

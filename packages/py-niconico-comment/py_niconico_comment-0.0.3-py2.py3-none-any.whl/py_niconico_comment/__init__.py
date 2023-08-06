# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'py-niconico-comment'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:   # pragma: no cover
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

from py_niconico_comment.niconico import NiconicoComments
from py_niconico_comment.utils import write_file

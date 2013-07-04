# -*- coding: utf-8 -*-

"""
.. module:: facio
   :synopsis: Provides version number and exposes base facio class.
"""

from facio.facio import Facio  # noqa


__VERSION__ = (1, 2, 0, 'dev', 0)


def get_version(*args, **kwagrs):
    from facio import __VERSION__ as version
    return '.'.join(str(part) for part in version)

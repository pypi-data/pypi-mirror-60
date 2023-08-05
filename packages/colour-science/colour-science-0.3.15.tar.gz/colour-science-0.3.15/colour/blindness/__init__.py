#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .datasets import *  # noqa
from . import datasets
from .machado2009 import (anomalous_trichromacy_cmfs_Machado2009,
                          anomalous_trichromacy_matrix_Machado2009,
                          cvd_matrix_Machado2009)

__all__ = []
__all__ += datasets.__all__
__all__ += [
    'anomalous_trichromacy_cmfs_Machado2009',
    'anomalous_trichromacy_matrix_Machado2009', 'cvd_matrix_Machado2009'
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from cryptography.fernet import Fernet

cdef str key = 'wFkN0Y2K1gQPzCRhwWfvwoXtKzYqS3oKWA672UYX-Iw='
cdef f = Fernet(key)


def encode(data):
    return f.encrypt(data)


def decode(data):
    return f.decrypt(data)

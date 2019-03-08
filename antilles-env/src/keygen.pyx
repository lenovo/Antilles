#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import pwd

from distutils.dir_util import mkpath
from os import path, environ, chmod, chown
from paramiko.ecdsakey import ECDSAKey

key = ECDSAKey.generate(bits=256)

pam_user = environ.get('PAM_USER')
user_pwd = pwd.getpwnam(pam_user) if pam_user is not None else None

if user_pwd is not None:
    if not path.exists(user_pwd.pw_dir):
        # workspace does not exists
        exit(-1)
    key_folder = path.join(user_pwd.pw_dir, '.ssh')
else:
    key_folder = path.expanduser('~/.ssh')

mkpath(key_folder, mode=0700)
if user_pwd is not None:
    chown(key_folder, user_pwd.pw_uid, user_pwd.pw_gid)

private_key_file = path.join(key_folder, 'id_ecdsa')
public_key_file = path.join(key_folder, 'id_ecdsa.pub')

if not path.exists(private_key_file) and not path.exists(public_key_file):
    key.write_private_key_file(private_key_file)

    with open(public_key_file, 'w') as f:
        f.write(
            "{keyname} {keybaese64}".format(
                keyname=key.get_name(),
                keybaese64=key.get_base64()
            )
        )

    if user_pwd is not None:
        chown(private_key_file, user_pwd.pw_uid, user_pwd.pw_gid)
        chown(public_key_file, user_pwd.pw_uid, user_pwd.pw_gid)

    chmod(private_key_file, 0600)
    chmod(public_key_file, 0644)

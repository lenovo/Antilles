# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

from abc import ABCMeta
from contextlib import contextmanager
from distutils.dir_util import mkpath
from getpass import getpass
from os import chown, path

import psycopg2
from six import add_metaclass, print_

from antilles.tools import obfuscator

__all__ = ['save_pass', 'fetch_pass', 'start_guide']


def _try_module_path(name):
    from importlib import import_module
    try:
        module = import_module(name)
        return module.__path__[0]
    except ImportError:
        return None


def _get_db_path():
    for name in [
        'libs.util',
        'antilles.mond.confluent',
        'antilles.mond.ganglia',
        'antilles.mond.icinga',
    ]:
        p = _try_module_path(name)
        if p is not None:
            return p
    return '/var/lib/antilles/tools'


dbpath = _get_db_path()

userfile = path.join(dbpath, 'ldatetime', 'node.pyc')
passfile = path.join(dbpath, 'lmonitor', 'node.pyc')


@add_metaclass(ABCMeta)
class BaseAccount(object):
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd


class Account(BaseAccount):
    def save(self):
        from pwd import getpwnam
        user = getpwnam('antilles')

        mkpath(path.dirname(userfile))
        mkpath(path.dirname(passfile))

        chown(path.dirname(userfile), user.pw_uid, user.pw_gid)
        chown(path.dirname(passfile), user.pw_uid, user.pw_gid)

        with open(userfile, 'w') as f1, open(passfile, 'w') as f2:
            f1.write(obfuscator.encode(self.user))
            f2.write(obfuscator.encode(self.passwd))

        chown(userfile, user.pw_uid, user.pw_gid)
        chown(passfile, user.pw_uid, user.pw_gid)

    def form_dsn(self, db, host=None, port=None):
        if host is None:
            dsn = 'dbname={0} user={1} password={2}'.format(
                db, self.user, self.passwd
            )
        else:
            dsn = 'dbname={0} host={1} port={2}' \
                  ' user={3} password={4}'.format(
                        db, host, port, self.user, self.passwd
                    )

        return dsn

    @contextmanager
    def connect(self, db, host=None, port=None):
        with psycopg2.connect(self.form_dsn(db, host, port)) as conn:
            yield conn

    @classmethod
    def fetch(cls):
        with open(userfile) as f1, open(passfile) as f2:
            return cls(
                user=obfuscator.decode(f1.read().rstrip()),
                passwd=obfuscator.decode(f2.read().rstrip())
            )


class PostgreAccount(BaseAccount):
    @classmethod
    def _try_create_table(cls, conn):
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ACCOUNT (
                    key TEXT not NULL,
                    username TEXT not NULL,
                    pass TEXT not NULL,
                    PRIMARY KEY (key)
                )
            """)

    def save(self, key, conn):
        self._try_create_table(conn)
        try:
            self._fetch(key, conn)
        except KeyError:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO ACCOUNT (key, username, pass)'
                    ' VALUES (%s, %s, %s)',
                    [key, self.user, obfuscator.encode(self.passwd)]
                )
        else:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE ACCOUNT SET username=%s, pass=%s WHERE key=%s',
                    [self.user, obfuscator.encode(self.passwd), key]
                )

    @classmethod
    def _fetch(cls, key, conn):
        cls._try_create_table(conn)

        with conn.cursor() as cur:
            cur.execute(
                'SELECT username,pass from ACCOUNT where key=%s',
                [key]
            )
            data = cur.fetchall()
            if len(data) == 0:
                raise KeyError(key)
            else:
                return data[0]

    @classmethod
    def fetch(cls, key, conn):
        data = cls._fetch(key, conn)
        return cls(user=data[0], passwd=obfuscator.decode(data[1]))


def save_pass(keyword, user, passwd, host, port, db):
    if keyword == 'postgres':
        Account(user, passwd).save(keyword)
    else:
        with Account.fetch().connect(db, host, port) as conn:
            PostgreAccount(user=user, passwd=passwd).save(
                keyword, conn
            )


def fetch_pass(keyword, host, port, db):
    pg_account = Account.fetch()
    if keyword == 'postgres':
        return pg_account
    else:
        with pg_account.connect(db, host, port) as conn:
            return PostgreAccount.fetch(keyword, conn)


def _enter_account(keyword, db, host, port):
    from six.moves import input
    user = input('Please enter the {0} username: '.format(keyword))

    passwd = getpass('Please enter the {0} password: '.format(keyword))
    confirm = getpass('Please confirm the {0} password: '.format(keyword))

    if passwd != confirm:
        print_('The {0} passwords entered did not match.'.format(keyword))
        exit(1)
    else:
        if keyword == 'postgres':
            pg_account = Account(user=user, passwd=passwd)
            try:
                with pg_account.connect(db, host, port):
                    pg_account.save()
            except psycopg2.OperationalError:
                print_()
                print_('Could not connect to psycopg2.')
                exit(1)
        else:
            with Account.fetch().connect(db, host, port) as conn:
                PostgreAccount(user=user, passwd=passwd).save(keyword, conn)
        print_()


def start_guide(db, host, port, config_icinga=False):
    try:
        _enter_account('postgres', db, host, port)
        _enter_account('influxdb', db, host, port)
        _enter_account('confluent', db, host, port)
        if config_icinga:
            _enter_account('icinga2 api', db, host, port)
    except KeyboardInterrupt:
        exit(1)
    except EOFError:
        exit(1)

# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import re
from abc import ABCMeta
from collections import OrderedDict

from six import add_metaclass, raise_from

from ..exceptions import UserModuleException

# from `man adduser`
USERNAME_REGEX = r'^[a-z_][a-z0-9_-]*[$]?$'


PASSWORD_RULRE = OrderedDict([
    # 'key': ('message_password_should_be', 'message_why_password_invalid')

    # legal characters
    ('has_non_ascii',
        ('should not contains non-ascii character',
         'password has non-ascii character')),
    ('has_illegal_characters',
        ('should not contains illegal characters',
         'password contains illegal characters')),
    # length
    ('too_short',
        ('at least 10 characters',
         'password only {} characters')),
    ('too_long',
        ('at most 128 characters',
         'password has {} characters')),
    # complexity
    ('not_conform_complexity_rules',
        ('should conform at least 3 complexity rules :',
         'password not conform {} complexity rules :')),
    ('no_digit',
        ('    should have at least 1 digit (0-9)',
         '    not contain digit')),
    ('no_special_character',
        ('    should have at least 1 special character',
         '    not contain special character')),
    ('no_uppercase_character',
        ('    should have at least 1 uppercase character (A-Z)',
         '    not contain uppercase character')),
    ('no_lowercase_character',
        ('    should have at least 1 lowercase character (a-z)',
         '    not contain lowercase character')),
    # identical
    ('identical',
        ('not more than 2 identical characters in password\
         (e.g., 111 not allowed)',
         'more than 2 identical characters in password'))
])


class VerifyException(UserModuleException):
    def __nozero__(self):
        return False


class PasswordException(VerifyException):
    errid = 2002

    def __init__(self, type, param=None):
        self.type = type
        self.should, exception = PASSWORD_RULRE[type]
        if param is not None:
            except_param = param if isinstance(param, list) else [param, ]
            exception = exception.format(*except_param)
        self.exception = exception
        super(VerifyException, self).__init__(exception)

    def __repr__(self):
        return self.exception


@add_metaclass(ABCMeta)
class PasswordSubException(VerifyException):
    errid = 2002

    def __init__(self, errs):
        self.errs = {e.type: e for e in errs}
        self.exception = '\n'.join(str(e) for e in errs)
        super(VerifyException, self).__init__(self.exception)

    def __iter__(self):
        return iter(self.errs.values())

    def __getitem__(self, key):
        return self.errs[key]

    def __contains__(self, type):
        assert isinstance(type, str)
        return any(sub.type == type for sub in self)


class PasswordComplexityException(PasswordSubException):
    def __init__(self, errs):
        self.type = 'not_conform_complexity_rules'
        super(PasswordComplexityException, self).__init__(errs)
        self.should, exception = PASSWORD_RULRE['not_conform_complexity_rules']
        self.exception = '\n'.join(
            [exception.format(len(errs)),
             '\n'.join(e.exception for e in self.errs.values())]
        )


class PasswordVerifyException(PasswordSubException):
    message = 'password verify failed.'

    def __init__(self, errs):
        super(PasswordVerifyException, self).__init__(errs)

    def __repr__(self):
        return '{}\n{}'.format(
            'password verify has {} exception:'.format(len(self.errs)),
            self.exception
        )

    def desc(self):
        return [
            {
                'should': e.should,
                'exception': e.exception
            }
            for e in self.errs.values()
        ]


class UserNameVerifyException(VerifyException):
    should = ('Usernames must start with a lower case letter or an underscore,'
              'followed by lower case letters, digits, underscores, or dashes.'
              '\nUsernames may only be up to 32 characters long')
    exception = 'username invalid'
    message = 'username invalid'
    errid = 2001


class PasswordVerify(object):
    def __init__(self, password, do_raise):
        self.password = password
        self.do_raise = do_raise

    def check(self):
        '''password verify'''
        # if characters legal check
        checkers = [
            self.check_encode,
            self.check_illegal_char,
            self.check_length_short,
            self.check_length_long,
            self.check_complexity,
            self.check_identical
        ]
        errors = list()

        for checker in checkers:
            err = checker()
            if err:
                errors.append(err)

        if len(errors) > 0:
            err = PasswordVerifyException(errors)
            if self.do_raise:
                raise err
            else:
                return err
        else:
            return True

    def check_encode(self):
        try:
            self.password.decode('ascii')
        except Exception as e:
            raise_from(
                PasswordException('has_non_ascii'),
                e
            )

    def check_illegal_char(self):
        if not all(32 <= ord(c) <= 126 for c in self.password):
            return PasswordException('has_illegal_characters')

    def check_length_short(self):
        # length check
        if len(self.password) < 10:
            return PasswordException('too_short', len(self.password))

    def check_length_long(self):
        if len(self.password) > 128:
            return PasswordException('too_long', len(self.password))

    def check_complexity(self):
        # complexity check
        complexity_exceptions = list()
        password = self.password

        if not any(c.isdigit() for c in password):
            complexity_exceptions.append(PasswordException('no_digit'))

        if not re.search(r'[a-z]', password):
            complexity_exceptions.append(
                PasswordException('no_lowercase_character'))

        if not re.search(r'[A-Z]', password):
            complexity_exceptions.append(
                PasswordException('no_uppercase_character'))

        if not re.search(r"[ \"'[\]!#$%&()*+,-./:;<=>?@^_`{|}~]", password):
            complexity_exceptions.append(
                PasswordException('no_special_character'))

        if len(complexity_exceptions) >= 2:
            return PasswordComplexityException(complexity_exceptions)

    def check_identical(self):
        # identical check
        last_char, identical_times = None, 1
        for c in self.password:
            if last_char != c:
                last_char, identical_times = c, 1
            else:
                identical_times += 1
            if identical_times >= 3:
                return PasswordException('identical')


class verify(object):
    @staticmethod
    def get_password_ruler():
        return '\n'.join(e[0] for e in PASSWORD_RULRE.values())

    @staticmethod
    def username(name):
        '''username verify'''
        if (not re.match(USERNAME_REGEX, name)) or (len(name) > 32):
            raise UserNameVerifyException

    @staticmethod
    def password(password, do_raise=True):
        '''password verify'''
        return PasswordVerify(password, do_raise).check()

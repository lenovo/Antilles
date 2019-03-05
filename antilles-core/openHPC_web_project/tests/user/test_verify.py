# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""
from pytest import raises

from antilles.user.managers.verify import VerifyException, verify


# test password verify
def test_too_long():
    with raises(VerifyException) as e:
        verify.password('Aa!_567890' * 12 + '123456789')
    assert 'too_long' in e.value


def test_too_short():
    with raises(VerifyException) as e:
        verify.password('Aa!_56789')
    assert 'too_short' in e.value


def test_complexity_rules():
    with raises(VerifyException) as e:
        verify.password('abc')

    assert 'no_digit' in e.value['not_conform_complexity_rules']

    with raises(VerifyException) as e:
        verify.password('abc4567890')

    assert 'not_conform_complexity_rules' in e.value
    assert 'no_uppercase_character' in e.value['not_conform_complexity_rules']
    assert 'no_special_character' in e.value['not_conform_complexity_rules']

    with raises(VerifyException) as e:
        verify.password('ABC4567890')

    assert 'not_conform_complexity_rules' in e.value
    assert 'no_lowercase_character' in e.value['not_conform_complexity_rules']
    assert 'no_special_character' in e.value['not_conform_complexity_rules']


def test_identical():
    with raises(VerifyException) as e:
        verify.password('Ab!XXXX890')
    assert 'identical' in e.value.exception


# test username verify

def test_username():
    # exception
    with raises(VerifyException) as e:
        verify.username('123_user')
    assert e.value.errid == 2001
    # ok
    verify.username('valid_user_name')

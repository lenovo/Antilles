# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import logging

from django.conf import settings
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from six import raise_from

from .managers.pam import auth
from .models import User

logger = logging.getLogger(__name__)


class AuthBackend(object):
    def authenticate(
            self, user=None,
            password=None,
            **kwargs
    ):
        username = user.username
        from pamela import PAMError
        try:
            auth(username, password)
        except PAMError:
            logger.warn(
                'Invalid user[ %s ]', username,
                exc_info=True
            )
            return None
        else:
            return user


class JWTAuthentication(BaseAuthentication):
    keyword = 'Jwt'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise AuthenticationFailed(
                detail='Invalid token header. No credentials provided.'
            )
        elif len(auth) > 2:
            raise AuthenticationFailed(
                detail='Invalid token header.'
                'Token string should not contain spaces.'
            )

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(
                detail='Invalid token header.'
                'Token string should not contain invalid characters.'
            )
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        import jwt
        from jwt import InvalidTokenError
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                    'require_exp': True,
                    'require_nbf': True,
                    'require_iat': True,
                    'require_iss': True,
                    'require_jti': True,
                    'require_role': True,
                    'require_sub': True,
                    'require_mgt': True
                }
            )

            user = User.objects.get(username=payload['sub'])

            payload_role = User.get_role_value(payload['role'])
            if payload_role > user.role:
                raise PermissionDenied(
                    'Insufficient permission.'
                )

            return user, payload
        except InvalidTokenError as e:
            raise_from(
                AuthenticationFailed, e
            )
        except User.DoesNotExist as e:
            raise_from(
                AuthenticationFailed, e
            )

    def authenticate_header(self, request):
        return self.keyword


class CookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('token')
        if token is None:
            return None
        token = token.decode()

        return self.authenticate_credentials(token)

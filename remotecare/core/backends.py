# -*- coding: utf-8 -*-
"""
The standard email backend is replaced by a custom
ModelBackend that supports getting the user based
on the stored hmac email value.

:subtitle:`Class definitions:`
"""
from django.contrib.auth.backends import ModelBackend
from apps.account.models import User
from django.contrib.auth.hashers import check_password


class EmailBackend(ModelBackend):
    '''
    Custom authentication backend which uses the hmac
    email address rather than the username to authenticate.
    '''
    def authenticate(self, email=None, password=None, username=None, **kwargs):
        """
        Processes an authentication attempt

        args:
            - email: not used
            - password: the password to check
            - username: the plain-text email address to search for

        Returns:
            the user if found and password correct else None.
        """
        try:
            # match the user's HMAC email address to the
            # entered 'username'
            # The hmac_email field will automatically HMAC the username.lower()
            # value
            user = User.objects.get(hmac_email=username)
            if check_password(password, user.password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

# coding=utf-8
from rest_framework import authentication
from apps.api.models import Token


class TokenAuthentication(authentication.TokenAuthentication):
    """
    Simple token based authentication.
    ...
    """

    model = Token
    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """
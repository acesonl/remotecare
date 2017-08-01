# -*- coding: utf-8 -*-
"""
Provides a couple of usefull functions for
generating random strings by randomly chosing values
from a list of possible characters

:subtitle:`Function definitions:`
"""
# Requires Crypto
from Crypto.Random import random, atfork
import string

# defaults
default_length = 8
default_choices = string.letters + string.digits
default_symbols = '!@#$%^&*_-+.'  # Subsection of all symbols

# password settings
default_password_length = 12
default_password_choices = default_choices + default_symbols

# id settings
default_id_length = 64
default_id_choices = default_choices + default_symbols

# key settings
default_key_length = 8
default_key_choices = default_choices


def randomint(minimum, maximum):
    """
    Wrapper function for getting a random int

    Args:
        - minimum: the minimum value
        - maximum: the maximum value

    Returns:
        a random integer between (including) minumum, maximum
    """
    atfork()  # Needed for UWSGI
    return random.randint(minimum, maximum)


def randombase(length=None, choices=default_choices):
    """
    Wrapper function for getting a random choice from
    a list of choices

    Args:
        - length: the length of the random string to return
        - choices: a list of choices to choose from

    Returns:
        A string with the specified length of random choices
    """
    atfork()  # Needed for UWSGI
    return ''.join(random.choice(choices) for x in range(length))


def randomid(length=default_id_length, choices=default_id_choices):
    """
    Wrapper function for getting a random id

    Produces a 64 length random string with symbols by default.

    Args:
        - length: the length of the random string to return
        - choices: a list of choices to choose from

    Returns:
        A string with the specified length of random choices
    """
    return randombase(length, choices)


def randompassword(length=default_password_length,
                   choices=default_password_choices):
    """
    Wrapper function for getting a random password

    Produces a 12 length random string with symbols by default.

    Args:
        - length: the length of the random string to return
        - choices: a list of choices to choose from

    Returns:
        A string with the specified length of random choices
    """
    return randombase(length, choices)


def randomkey(length=default_key_length, choices=default_key_choices):
    """
    Wrapper function for getting a random key

    Produces a 8 length random string with no symbols by default.
    Can be used to store longer values in the session.

    Args:
        - length: the length of the random string to return
        - choices: a list of choices to choose from

    Returns:
        A string with the specified length of random choices
    """
    return randombase(length, choices)

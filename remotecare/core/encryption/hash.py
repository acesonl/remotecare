# -*- coding: utf-8 -*-
"""
Contains functions for hashing values with use of HMAC or without.

An hash is created as:
    hash_algorithm$salt$hashed_value

an HMAC is created as:
    hash_algorirthm$hashed_value

All values are default stored as base64

:subtitle:`Class and function definitions:`
"""

# Requires Crypto
from Crypto.Hash import SHA256
from Crypto.Hash import HMAC
import base64
from random import randomkey

# List of available hashers and used hashnames
available_hashers = {SHA256: 'SHA256'}

# Default cipher
default_hasher = SHA256

# Default iterations
default_iterations = 100


class HashException(Exception):
    """
    This exception is thrown when the hash algorithm is unknown.
    """
    pass


# checks a HMAC
def check_hmac(secret, password, hmac_base64):
    """
    Checks whether the hmac(password, secret) is
    the same as the hmac_base64.

    Args:
        - secret: the key to use
        - password: the value to hash.
        - hmac_base64: base64 representation in hash_algorirthm$hashed_value\
                       format

    Returns:
        True/False

    Raises:
        HashException: HMAC algorithm unknown
    """
    hash_name, hashed_string = hmac_base64.split('$')

    hasher = None

    for cls, hashername in list(available_hashers.items()):
        if hashername == hash_name:
            hasher = cls
            break

    if not hasher:  # pragma: no cover
        raise HashException('HMAC algorithm unknown!')

    return hmac_base64 == create_hmac(secret, password, hasher)


# checks a salted hash
def check_hash(password, hash_base64):
    """
    Checks whether the hash(password) is
    the same as the hmac_base64.

    Args:
        - password: the value to hash.
        - hmac_base64: base64 representation in\
                       hash_algorirthm$salt$hashed_value format

    Returns:
        True/False

    Raises:
        HashException: hash algorithm unknown
    """
    hash_name, salt, hashed_string = hash_base64.split('$')

    hasher = None

    for cls, hashername in list(available_hashers.items()):
        if hashername == hash_name:
            hasher = cls
            break

    if not hasher:  # pragma: no cover
        raise HashException('Hash algorithm unknown!')

    return hash_base64 == create_hash(password, salt, hasher)


# Generate a HMAC
def create_hmac(secret, password,
                hasher=default_hasher, iterations=default_iterations):
    """create_hmac(secret, password, hasher=default_hasher, iterations=\
    default_iterations)

    Create a hmac from secret and password with ability
    to set the hasher and number of iterations.

    Args:
        - secret: the key to use
        - password: the value to hash.
        - hasher: override default hasher
        - iterations: override default iterations.

    Returns:
        hash_algorirthm$hashed_value in base64 format

    Raises:
        HashException: HMAC algorithm unknown
    """
    if isinstance(password, unicode):
        password = password.encode("utf8")
    
    if hasher not in available_hashers:  # pragma: no cover
        raise HashException('HMAC algorithm unknown!')

    # hmac the password and secret a couple of times
    for i in range(1, iterations):
        password = do_hmac_hash(secret, password, hasher)

    # base 64 encode
    password = base64.urlsafe_b64encode(password)

    return available_hashers[hasher] + '$' + password


# Generate salted hash
# Intended usage: possible password storage
def create_hash(password, salt=None,
                hasher=default_hasher, iterations=default_iterations):
    """create_hash(password, salt, hasher=default_hasher, iterations=\
    default_iterations)

    Create a hash of password using salt, hasher and iterations

    Args:
        - password: the value to hash.
        - salt: the salt value.
        - hasher: override default hasher
        - iterations: override default iterations.

    Returns:
        hash_algorirthm$salt$hashed_value in base64 format

    Raises:
        HashException: Hash algorithm unknown
    """

    if isinstance(password, unicode):
        password = password.encode("utf8")

    if salt is None:
        salt = randomkey()

    if hasher not in available_hashers:  # pragma: no cover
        raise HashException('Hash algorithm unknown!')

    # hash the password + salt a couple of times
    for i in range(1, iterations):
        password = do_hash(password + salt, hasher)

    # base 64 encode
    password = base64.urlsafe_b64encode(password)

    return available_hashers[hasher] + '$' + salt + '$' + password


# Hash worker
def do_hash(password, hasher):
    """
    Shortcut for crypto hashing function

    Args:
        - password: the value to hash.
        - hasher: override default hasher

    Returns:
        password hashed by hasher
    """
    hasher_instance = hasher.new()
    hasher_instance.update(password)
    return hasher_instance.hexdigest()


# HMAC worker
def do_hmac_hash(secret, password, hasher):
    """
    Shortcut for hmac function

    Args:
        - secret: the key to use
        - password: the value to hash.
        - hasher: the hasher to use

    Returns:
        password hashed by hasher with HMAC
    """
    hasher_instance = hasher.new()
    hmac_instance = HMAC.new(secret, digestmod=hasher_instance)
    hmac_instance.update(password)
    return hmac_instance.hexdigest()

# -*- coding: utf-8 -*-
"""
Contains functions for symmetric encryption/decryption,
by default with AES_256_CBC although this can be set to an other
encryption algorithm or key length in a later stage.

.. note::
    The encrypted values are returned with the cipher prepended, as following:
    AES256CBC$encrypted_value

:subtitle:`Class and function definitions:`
"""
import math

# Encrypt/decrypt wrappers to allow other ciphers in the future.
from core.encryption.AES import AES_256_CBC

# List of available ciphers and used ciphernames
available_ciphers = {AES_256_CBC: 'AES256CBC'}

cipher_list = [available_ciphers[x] for x in available_ciphers]

# Default cipher
default_cipher = AES_256_CBC


class EncryptionException(Exception):
    """
    This exception is thrown when the cipher is unknown.
    """
    pass


def get_max_length(max_length, cipher=default_cipher):
    """
    Get the max_length to set on a field based on
    the max_length you want to store on the field..

    Args:
        - max_length: the max_length of the text to store
        - cipher: override the default cipher

    Returns:
        The max length of the field to hold the AES encryption.
        based on the first: 2 ^ x which is high enough.

    Raises:
        EncryptionException: Cipher is unknown
    """
    if cipher not in available_ciphers:  # pragma: no cover
        raise EncryptionException('Cipher is unknown')

    # just encrypt some dummy value and get the length
    max_length = len(encrypt('1' * max_length, 'password'))

    # get 2 ^ x with can certainly hold the length to be stored
    # 172 = 2 ^ x
    # log(max_length) / log(2) = 7.42....
    # ceil(7.42) = 8
    # 2 ^ 8 = 256
    max_length = math.pow(
        2, math.ceil(
            math.log(max_length) / math.log(2)
        )
    )

    return int(max_length)


def is_encrypted(value):
    """
    Check if the value is encrypted by comparing the first characters
    of the value to the list of known ciphers.

    Args:
        - value: the value to check (AES256CBC$#encrypted_value#)

    Returns:
        True if the cipher name could be found in the value else False
    """
    for cipher in cipher_list:
        if value.startswith(cipher):
            return True
    return False


def encrypt(plain_text, key, cipher=default_cipher):
    """encrypt(plain_text, key, cipher=default_cipher)
    Encrypt wrapper function

    Args:
        - plain_text: the text to encrypt
        - key: the key to use
        - cipher: override the default cipher

    Returns:
        encrypted plain_text by key with use of cipher

    Raises:
        EncryptionException: Cipher is unknown
    """
    if cipher not in available_ciphers:  # pragma: no cover
        raise EncryptionException('Cipher is unknown')

    cipher_instance = cipher()

    # Add ciphername in front
    return available_ciphers[cipher] + '$' +\
        cipher_instance.encrypt(plain_text, key)


def decrypt(cipher_and_encrypted_text, key):
    """
    Decrypt wrapper function

    the cipher_and_encrypted_text in ciphername$encrypted_text format
    with use of the key

    Args:
        - cipher_and_encrypted_text: encrypted value in\
          ciphername$encrypted_text
        - key: the key to use

    Returns:
        plain text if key is correct else crap.

    Raises:
        EncryptionException: Cipher is unknown
    """

    cipher_and_encrypted_text = cipher_and_encrypted_text.split('$')
    encrypted_text = cipher_and_encrypted_text[1]

    cipher = None

    for cls, ciphername in list(available_ciphers.items()):
        if ciphername == cipher_and_encrypted_text[0]:
            cipher = cls
            break

    if not cipher:  # pragma: no cover
        raise EncryptionException('Cipher is unknown')

    cipher_instance = cipher()

    decrypted = cipher_instance.decrypt(encrypted_text, key)

    if decrypted == 'None':
        decrypted = None
    return decrypted

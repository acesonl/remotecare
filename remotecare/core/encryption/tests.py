# -*- coding: utf-8 -*-
"""
Test the encryption and hash functions

:subtitle:`Class definitions:`
"""
from django.test import TestCase
from core.encryption.symmetric import encrypt, decrypt
from core.encryption.hash import check_hmac, check_hash, create_hmac,\
    create_hash
from core.encryption.random import randomint, randomid, randombase,\
    randompassword, randomkey


class Encryption(TestCase):
    '''
    Test cases definitions for the encryption functions
    '''

    def check_encryption(self):
        """
        Check the AES256CBC encryption
        """
        key = 'Ohrohtei0aeshai8Jaigi7eech3CheXe'
        plain_text = 'Plain text test 1234567890 !@#$%*()~'

        encrypted_text = encrypt(plain_text, key)
        decrypted_text = decrypt(encrypted_text, key)

        self.assertEqual('AES256CBC', encrypted_text[0:9])
        self.assertNotEqual(encrypted_text[10:], plain_text)
        self.assertEqual(decrypted_text, plain_text)

    def check_hash(self):
        """
        Check the hash/hmac functions
        """
        password = 'Ohrohtei0aeshai8Jaigi7eech3CheXe'
        secret = 'aaBei6aeViek'
        salt = 'abe32ds'
        hmac = create_hmac(secret, password)
        hmac_test = 'SHA256$NWY0YmNkOWVlMjVjNDMyZWRlMTJmMGQzMDVlZW' +\
            'RhOTBiYjQzYmFmNDJkMTlkNjRiYThmYzAxNmEyMjExZGMyMw=='
        self.assertEquals(hmac, hmac_test)
        self.assertEquals(True, check_hmac(secret, password, hmac_test))

        hash_val = create_hash(secret, salt)
        hash_test = 'SHA256$abe32ds$NGMzZjIwZWVlNjIzMDNjODVjNjMyM2IyMjVm' +\
            'YjAwZDliMmExNzY1NmExMWJhNjNlOGRhMGI0Yjc4MTc0N2I0Zg=='

        self.assertEquals(hash_val, hash_test)
        self.assertEquals(True, check_hash(secret, hash_test))

    def check_random(self):
        """
        Check that the random functions can be called without
        exceptions
        """
        randomint(10, 100)
        randomid()
        randompassword()
        randomkey()
        randombase(length=50)

    def test_encryption_functions(self):
        """
        Runs the checks
        """
        self.check_encryption()
        self.check_hash()
        self.check_random()

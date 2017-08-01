# -*- coding:Utf-8 -*-
"""
Contains all tests for login and User model.

:subtitle:`Class definitions:`
"""
from core.unittest.baseunittest import BaseUnitTest
from apps.account.models import User
from apps.healthperson.patient.models import Patient


class LoginTest(BaseUnitTest):
    """
    Tests the login functions, login block after to many
    incorrect logins and functions on the User model
    that were not covered.
    """
    fixtures = ['test_data/test_users.json']

    def check_logins(self):
        """
        Checks the basic tests logins
        """
        self.login('frank@example.com')
        self.login('dominique@example.com')
        self.login('patrick@example.com')
        self.login('cindy@example.com')
        self.login('maria@example.com')
        self.login('john@example.com')
        self.login('harry@example.com')

        # Check upper/lower case does not matter
        self.login('hArRy@eXaMplE.cOm')

    def check_block_system(self):
        """
        Checks login block system which temporarily
        blocks the user after to many invalid login
        attempts.
        """
        self.reset_stores()
        self.get('/logout/')
        self.get('/login/')
        email = 'frank@example.com'
        for i in range(1, 11):
            res = self.post('/login/', {'username': email,
                                        'password': 'FAULTYPASSWORD',
                                        'do_sms_code': '0'},
                            status_code=200)

            if i > 9:
                # Check block
                self.assertEqual(res.context['block_nr'], 10)
                self.assertEqual(res.context['block_time'], 5)

        # Check no SMS has been sent
        self.assertEqual(len(self.SMS_STORE), 0)

    def check_invalid_login(self):
        """
        Check that an user cannot login with a faulty password
        """
        self.reset_stores()
        self.get('/logout/')
        self.get('/login/')
        # Check with everything incorrect
        res = self.post('/login/', {'username': 'unknown@example.com',
                                    'password': 'FAULTYPASSWORD',
                                    'do_sms_code': '0'},
                        status_code=200)

        self.assertEqual(len(res.context['form'].errors), 1)

        # Check with correct username but incorrect password
        res = self.post('/login/', {'username': 'john@example.com',
                                    'password': 'FAULTYPASSWORD',
                                    'do_sms_code': '0'},
                        status_code=200)

        self.assertEqual(len(res.context['form'].errors), 1)

        # Check if filled in empty
        res = self.post('/login/', {'username': '',
                                    'password': '',
                                    'do_sms_code': '0'},
                        status_code=200)

        self.assertEqual(len(res.context['form'].errors), 2)

        # Check no SMS has been sent
        self.assertEqual(len(self.SMS_STORE), 0)

    def check_model(self):
        """
        Check extra property and functions on the User model
        """
        patient = Patient.objects.all()[0]
        user = User.objects.get(healthperson=patient)
        user.get_date_of_birth
        user.prefix = 'van'
        user.title = 'dr'

        self.assertEqual(user.new_questionnaire_request, False)
        self.assertEqual(user.new_message_count, 'no')
        self.assertEqual(
            user.full_name,
            user.first_name + ' ' + user.prefix + ' ' + user.last_name)
        self.assertEqual(
            user.professional_name,
            user.get_title_display() + ' ' +
            user.initials + ' ' +
            user.prefix + ' ' + user.last_name)
        self.assertEqual(user.is_deleted, False)

    def test_check_logins(self):
        '''
        Test the login features
        '''
        self.check_logins()
        self.check_invalid_login()
        self.check_block_system()
        self.check_model()

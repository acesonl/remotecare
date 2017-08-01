# -*- coding: utf-8 -*-
"""
Test the feedback system and check that the predefined
information pages give a 200

:subtitle:`Class definitions:`
"""
from django.core import mail
from core.unittest.baseunittest import BaseUnitTest
from apps.information.views import TEMPLATES


class InformationAndFeedbackTest(BaseUnitTest):
    '''
    Information and feedback tests
    '''

    fixtures = ['test_data/test_users.json', ]

    def check_feedback(self):
        '''
        Check if the feedback process/form works as expected
        '''
        mail.outbox = []

        self.login('frank@example.com')
        res = self.get('/information/feedback/')
        # post feedback
        res = self.post('/information/feedback/',
                        {'feedback': 'Feedback for Remote Care application'})
        res = self.get(res.url)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.from_email, 'remotecare@example.com')
        self.assertIn('Feedback for Remote Care application', email.body)

    def test_information_and_feedback(self):
        '''
        Simple test for information pages (result_code=200)
        '''
        self.login('frank@example.com')
        # Check static pages
        self.get('/information/about_security/')
        self.get('/information/feedback/')
        self.get('/information/feedback_sent/')

        # Check content pages
        for page in TEMPLATES:
            self.get('/information/' + page + '/')

        # Check content pages not present
            self.get('/information/notexisting/', status_code=404)

        # test feedback
        self.check_feedback()

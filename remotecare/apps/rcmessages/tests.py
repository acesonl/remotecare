# -*- coding: utf-8 -*-
"""
Module containing message tests.

:subtitle:`Class definitions:`
"""
from core.unittest.baseunittest import BaseUnitTest
from apps.rcmessages.models import RCMessage
from apps.healthperson.secretariat.models import Secretary


class RCMessageTest(BaseUnitTest):
    """
    Test adding and viewing messages.
    """
    fixtures = ['test_data/test_users.json', ]

    def test_messages(self):
        """
        Test adding messages with different senders and
        test if encryption works correctly.
        """
        # print 'Running integration messages tests'
        self.login('gerald@example.com')
        res = self.post('/patient/search/',
                        {'last_name': 'davis'},
                        status_code=200)

        patient = res.context['patients'][0]
        session_key = self.get_session_key(patient.health_person_id)
        url = '/messages/patient/' + session_key + '/add/'
        res = self.get(url)

        subject = 'Bericht van uitslag.'
        internal_message = 'Er zijn geen opmerkelijke bevindingen gedaan.'

        form = res.context_data['form']
        form1 = form.__class__(initial={'subject': subject,
                                        'internal_message': internal_message})
        post_data = self.get_post_data(form1)

        res = self.post(url, post_data, status_code=302)
        res = self.get(res.url)

        # Check picking secretary if healthprofessional not set
        message = RCMessage.objects.latest('pk')
        self.assertEqual(message.sender, message.healthprofessional)
        message.healthprofessional = None
        message.secretary = Secretary.objects.all()[0]
        self.assertEqual(message.sender, message.secretary)

        # Check if the same
        self.assertEqual(message.internal_message, internal_message)
        self.assertEqual(message.subject, subject)

        # Check if message is present for Frank
        self.login('frank@example.com')
        res = self.get('/')
        patient = res.context_data['patient']
        session_key = self.get_session_key(patient.health_person_id)

        res = self.get('/messages/patient/' + session_key + '/' +
                       str(message.id) + '/details/')
        message = res.context['message']

        # Check if the same
        self.assertEqual(message.internal_message, internal_message)
        self.assertEqual(message.subject, subject)

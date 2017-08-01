# -*- coding: utf-8 -*-
"""
Unittest for checking the healthprofessional functionality

:subtitle:`Class definitions:`
"""
from datetime import datetime
from core.unittest.baseunittest import BaseUnitTest
from apps.rcmessages.models import RCMessage
from apps.healthperson.patient.models import Patient


class HealthprofessionalTest(BaseUnitTest):
    """
    Test message sending, searching, and all patient
    related pages like reports/messages etc.
    """
    fixtures = ['test_data/test_users.json',
                'test_data/report_repost_data.json']

    def check_sent_messages(self):
        """
        Checks if healthprofessional can sent a message
        to a patient and if it can be found via the search
        page.
        """
        # Setup
        res = self.get('/')
        healthprofessional = res.context['healthprofessional']
        session_key = self.get_session_key(
            healthprofessional.health_person_id)

        # Get frank@example.com
        patient = Patient.objects.get(id=4)
        RCMessage.objects.all().delete()

        # Add message
        message = RCMessage()
        message.patient = patient
        message.added_on = datetime.now()
        message.subject = 'Test message'
        message.internal_message = 'Test message voor Frank'
        message.healthprofessional = healthprofessional
        message.changed_by_user = healthprofessional.user
        message.save()

        # Check message sent details view
        res = self.get(
            '/messages/sent/' + session_key +
            '/' + str(message.id) + '/sent/details/',
            check_status_code=False)

        self.assertEqual(len(res.context_data['rc_messages']), 1)

        # Check search
        res = self.post(
            '/messages/sent/' + session_key + '/search/',
            {'BSN': '1234567894', 'last_name': 'Davis'},
            status_code=200)

        self.assertEqual(len(res.context_data['search_results']), 1)

        # Hit overview
        self.get('/messages/sent/' + session_key + '/')

        # Hit messages overview
        session_key = self.get_session_key(patient.health_person_id)
        self.get('/patient/' + session_key + '/view/messages/?message=' +
                 str(message.id))
        self.get('/patient/' + session_key + '/view/messages/')

        # Check message search
        res = self.post('/patient/' + session_key + '/view/messages/',
                        {'searchterm': 'Frank'}, status_code=200)

        self.assertEqual(len(res.context_data['rc_messages']), 1)

    def check_search(self):
        """
        Check general search for patients
        """
        search_terms = ['Davis', '2-1-1997', '1234567894']
        for search_term in search_terms:
            res = self.post('/search/', {'searchterm': search_term},
                            check_status_code=False)
            self.assertEqual(len(res.context_data['patients']), 1)

    def check_patient_pages(self):
        """
        Check pages which can be opened by an healhtprofessional
        for a patient including controls. appointments, reports
        and filled in questionnaire information
        """
        patient = Patient.objects.get(id=4)
        session_key = self.get_session_key(patient.health_person_id)

        # Hit controles overview
        self.get('/patient/' + session_key + '/view/controles/')

        # Hit appointments overview
        self.get('/patient/' + session_key + '/view/appointments/')

        # Hit appointments overview
        self.get('/patient/' + session_key + '/view/reports/')

        # Hit questionnaire for diagnose (normally AJAX json call)
        # also without patient session_key
        self.get('/patient/' + session_key + '/questionnaire_exclude_list/' +
                 '?questionnaire=chron')
        self.get('/patient/questionnaire_exclude_list/?questionnaire=chron')

    def test_healthprofessional_functions(self):
        """
        Test runner for all healhtprofessional checks

        .. note:: Adding and editing reports, messages etc. are\
                  not tested here but in their own apps.
        """
        self.login('gerald@example.com')

        # Make patient.user BSN unique
        user = Patient.objects.get(id=4).user
        user.BSN = '1234567894'
        user.changed_by_user = user
        user.save()

        # Do checks
        # First do search so the session_keys are set
        self.check_search()
        self.check_sent_messages()
        self.check_patient_pages()

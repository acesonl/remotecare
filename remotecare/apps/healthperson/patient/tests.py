# -*- coding: utf-8 -*-
"""
This module defines the tests done patient functionality
that is not part of other apps

:subtitle:`Class definitions:`
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from core.unittest.baseunittest import BaseUnitTest
from apps.rcmessages.models import RCMessage
from apps.healthperson.patient.models import Patient, add_weken


class PatientTest(BaseUnitTest):
    """
    Unittest definitions for patients
    """
    fixtures = ['test_data/test_users.json',
                'test_data/report_repost_data.json']

    def check_account(self, base_url):
        """
        Check viewing/editing the account (profile) information
        for a patient
        """
        res = self.get(base_url + 'view/profile/')
        res = self.get(base_url + 'edit/profile/')
        prefix = ''
        if res.context['form'].prefix:
            prefix = res.context['form'].prefix

        post_data = self.get_post_data(res.context['form'], prefix)

        post_data.update({'change_password': 'yes',
                          'password': 'RemoTecare12',
                          'password2': 'RemoTecare12'})

        # Check with changing password
        res = self.post(base_url + 'edit/profile/', post_data)

        post_data.update({'password': None,
                          'password2': None})
        del post_data['change_password']

        # Check without changing password
        res = self.post(base_url + 'edit/profile/', post_data)

        # Check if login works with new password
        self.login('frank@example.com', 'RemoTecare12')

    def check_notification(self, base_url):
        """
        Check viewing/editing the notification settings
        for a patient
        """

        res = self.get(base_url + 'view/notification/')
        res = self.get(base_url + 'edit/notification/')
        prefix = ''
        if res.context['form'].prefix:
            prefix = res.context['form'].prefix

        post_data = self.get_post_data(res.context['form'], prefix)

        # Check if can save (very basic test)
        res = self.post(base_url + 'edit/notification/', post_data, )

    def check_messages(self, base_url):
        """
        Check viewing messages
        """
        res = self.get('/')
        patient = res.context['patient']

        for i in range(1, 3):
            message = RCMessage()
            message.patient = patient
            message.added_on = datetime.now()
            message.subject = 'Test message' + str(i)
            message.internal_message = 'Test message voor Frank' + str(i)
            message.healthprofessional = patient.current_practitioner
            message.changed_by_user = patient.user
            message.save()
        res = self.get('/')

        for i, message in enumerate(res.context_data['rc_messages']):
            i += 1
            res = self.get(
                '/messages' + base_url + str(message.id) + '/details/')
            message_to_test = res.context['message']

            self.assertEqual(message_to_test.subject, 'Test message' + str(i))
            self.assertEqual(message_to_test.internal_message,
                             'Test message voor Frank' + str(i))
        # Hit MessageOverview
        self.get('/messages' + base_url)

    def check_search(self):
        """
        Check the search function in the homepage
        """
        res = self.get('/')
        patient = res.context['patient']
        message = RCMessage()
        message.patient = patient
        message.added_on = datetime.now()
        message.subject = 'ABCDEF message'
        message.internal_message = 'ABCDEF message voor Frank'
        message.healthprofessional = patient.current_practitioner
        message.changed_by_user = patient.user
        message.save()

        # Try to find the just added message
        res = self.post('/search/', {'searchterm': 'ABCDEF'},
                        check_status_code=False)
        self.assertEqual(res.context_data['objects'][0].internal_message,
                         'ABCDEF message voor Frank')

        # try to find a questionnaire
        res = self.post('/search/', {'searchterm': 'bijster'},
                        check_status_code=False)

        self.assertEqual(len(res.context_data['objects']), 1)

    def check_questionnaire_helper(self, url, count, test_value):
        """
        Helper function for testing the filled-in questionnaire details
        """
        res = self.get(url)
        selected_questionnaire = res.context_data[
            'select_disease_activity_questionnaire']

        self.assertEqual(
            len(res.context_data['disease_activity_questionnaires']), count)

        if test_value:
            self.assertEqual(selected_questionnaire.display_name, test_value)
        else:
            self.assertEqual(selected_questionnaire, None)

    def check_questionnaire_details(self, base_url):
        """
        Check the filled-in questionnaire detail pages
        """
        # Check 'Ziekteactiviteit'
        self.check_questionnaire_helper(
            base_url + 'questionnaire/disease_activity/',
            1, 'Ziekteactiviteit')

        # Check 'Kwaliteit van leven'
        self.check_questionnaire_helper(
            base_url + 'questionnaire/quality_of_life/',
            1, 'Kwaliteit van leven')

        # Check 'Kwaliteit van zorg'  (is not present in test data)
        self.check_questionnaire_helper(
            base_url + 'questionnaire/healthcare_quality/',
            0, None)

    def check_model(self):
        """
        Check functions in model.py not covered
        by other tests but very important
        for correctly adding new questionnaires etc.
        """
        # check the add_weken function
        self.assertEqual(add_weken(1), '1 week')
        self.assertEqual(add_weken(2), '2 weken')
        self.assertEqual(add_weken('1'), '1 week')
        self.assertEqual(add_weken('2'), '2 weken')
        self.assertEqual(add_weken('A'), 'A')

        # Get frank@example.com
        patient = Patient.objects.get(id=4)

        patient.blood_sample_frequency = 'sameasregular'
        patient.blood_taken_freq_display
        patient.blood_sample_frequency = 'other'
        patient.blood_taken_freq_display

        # next_questionnaire_date tests
        patient.regular_control_frequency = '3_months'

        self.assertEqual(
            patient.next_questionnaire_date,
            patient.last_questionnaire_date + relativedelta(months=+3))

        patient.regular_control_frequency = '6_months'
        self.assertEqual(
            patient.next_questionnaire_date,
            patient.last_questionnaire_date + relativedelta(months=+6))

        patient.regular_control_frequency = '12_months'
        self.assertEqual(
            patient.next_questionnaire_date,
            patient.last_questionnaire_date + relativedelta(months=+12))

        patient.regular_control_frequency = '1'
        self.assertEqual(
            patient.next_questionnaire_date,
            patient.last_questionnaire_date + relativedelta(weeks=+1))

        patient.regular_control_frequency = 'A'
        self.assertEqual(patient.next_questionnaire_date, None)

        patient.regular_control_frequency = '1'
        self.assertEqual(
            patient.next_questionnaire_ready,
            patient.next_questionnaire_date <= date.today())

        # include_blood_taken_questions tests
        patient.regular_control_frequency = '3_months'
        patient.blood_sample_frequency = 'sameasregular'
        self.assertEqual(
            patient.include_blood_taken_questions,
            date.today() >=
            (patient.last_blood_taken_date + relativedelta(months=+3)))

        patient.blood_sample_frequency = '6_months'
        del patient.patient_include_blood_taken_questions
        self.assertEqual(
            patient.include_blood_taken_questions,
            date.today() >=
            (patient.last_blood_taken_date + relativedelta(months=+6)))

        patient.blood_sample_frequency = '12_months'
        del patient.patient_include_blood_taken_questions
        self.assertEqual(
            patient.include_blood_taken_questions,
            date.today() >=
            (patient.last_blood_taken_date + relativedelta(months=+12)))

        patient.blood_sample_frequency = '2'
        del patient.patient_include_blood_taken_questions
        self.assertEqual(
            patient.include_blood_taken_questions,
            date.today() >=
            (patient.last_blood_taken_date + relativedelta(weeks=+2)))

        patient.blood_sample_frequency = 'A'
        del patient.patient_include_blood_taken_questions
        self.assertEqual(patient.include_blood_taken_questions, False)

    def test_patient_functions(self):
        """
        Run all checks for a patient
        """
        self.login('frank@example.com')
        res = self.get('/')
        session_key = self.get_session_key(
            res.context['patient'].health_person_id)
        base_url = '/patient/' + session_key + '/'

        self.check_notification(base_url)
        self.check_questionnaire_details(base_url)
        self.check_messages(base_url)
        self.check_account(base_url)
        self.check_search()
        self.check_model()

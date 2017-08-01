# -*- coding: utf-8 -*-
"""
Unittests for the service functions

:subtitle:`Class definitions:`
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.core import mail
from django.conf import settings
from core.unittest.baseunittest import BaseUnitTest
from apps.service.utils import send_questionnaire_reminder_sms,\
    send_questionnaire_fillin_sms, send_urgent_report_reminder,\
    send_report_reminder, remove_deleted_patients,\
    check_questionnaire_fillin_deadlines, insert_new_questionnaire_requests,\
    check_unhandled_questionnaires, check_unhandled_urgent_questionnaires
from apps.account.models import User
from apps.healthperson.patient.models import Patient
from apps.healthperson.secretariat.models import Secretary
from apps.questionnaire.models import QuestionnaireRequest


class ServiceTest(BaseUnitTest):
    '''
    Test the service functions
    '''
    fixtures = ['test_data/test_users.json',
                'test_data/report_repost_data.json']

    def reminder_checks(self, healthperson, body_test, check_email, check_sms):
        """
        Checks if reminders have been sent via the SMS
        and e-mail stores that catch SMS and e-mail traffic
        during testing

        Args:
            - healthperson: healthperson to pick the e-mail address to test\
                from
            - body_test: the body of the message to test for
            - check_email: do need to check e-mail?
            - check_sms: do need to check sms?
        """
        if check_email:
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertIn(healthperson.user.email, email.to)
            self.assertEqual(email.body, body_test)
        else:
            self.assertEqual(len(mail.outbox), 0)

        if check_sms:
            self.assertEqual(len(settings.SMS_STORE), 1)
            sms = settings.SMS_STORE[0]
            self.assertEqual(
                healthperson.user.mobile_number, sms['recipients'])
            self.assertEqual(sms['message'], body_test)
        else:
            self.assertEqual(len(settings.SMS_STORE), 0)

    def do_reminder_check(self, body_test, function, attr_name,
                          function_instance, attr_instance, check_instance):
        """
        Runner for checking reminders, highly abstracted

        Args:
            - body_test: the body to test for
            - function: the function to call with function_instance
            - attr_name: the attr_name to set on attr_instance
            - function_instance: the param to sent to the function
            - check_instance: the instance to check, should be a healthperson

        See example in 'do_test_questionnaire_fillin_sms' to see what is sent.
        for the specific args
        """
        self.reset_stores()
        setattr(attr_instance, attr_name, 'sms_and_email')
        function(function_instance)
        self.reminder_checks(check_instance, body_test, True, True)

        self.reset_stores()
        setattr(attr_instance, attr_name, 'email_only')
        function(function_instance)
        self.reminder_checks(check_instance, body_test, True, False)

        self.reset_stores()
        setattr(attr_instance, attr_name, 'sms_only')
        function(function_instance)
        self.reminder_checks(check_instance, body_test, False, True)

    def do_questionnaire_check(self, body_test, function, attr_name):
        """
        Helper function for checking questionnaire reminder functions

        Args:
            - body_test: the body to test for
            - function: the function to call before checking
            - attr_name: the attr_name to set before checking
        """
        patient = Patient.objects.all()[0]

        body_test = body_test.format(patient.get_diagnose_display())

        self.do_reminder_check(
            body_test,
            function,
            attr_name,
            patient,
            patient,
            patient)

    def do_report_check(self, body_test, function, attr_name):
        """
        Helper function for checking report reminder functions

        Args:
            - body_test: the body to test for
            - function: the function to call before checking
            - attr_name: the attr_name to set before checking
        """
        questionnaire = QuestionnaireRequest.objects.filter(urgent=True)[0]
        healthprofessional = questionnaire.patient.current_practitioner

        self.do_reminder_check(
            body_test,
            function,
            attr_name,
            questionnaire,
            healthprofessional,
            healthprofessional)

        secretary = Secretary.objects.all()[0]
        healthprofessional.urgent_control_secretary = secretary

        self.do_reminder_check(
            body_test,
            function,
            attr_name,
            questionnaire,
            healthprofessional,
            secretary)

    # Test specifications
    def do_test_questionnaire_fillin_sms(self):
        """
        Check if the questionnaire fillin sms/email function
        works correctly
        """
        body_test = u'\nZou u via Remote Care uw controle voor ' +\
                    u'{0} willen invullen?\n\n'
        self.do_questionnaire_check(
            body_test,
            send_questionnaire_fillin_sms,
            'regular_control_start_notification')

    def do_test_questionnaire_reminder_sms(self):
        """
        Check if the questionnaire reminder sms/email function
        works correctly
        """
        body_test = u'\nHerinnering: Zou u via Remote Care uw ' +\
                    u'controle voor {0} willen invullen?\n\n\n'

        self.do_questionnaire_check(
            body_test,
            send_questionnaire_reminder_sms,
            'regular_control_reminder_notification')

    def do_test_urgent_report_reminder(self):
        """
        Check if the urgent report reminder sms/email function
        works correctly
        """
        body_test = u'\nEr zijn onafgehandelde Urgente Afspraken die meer' +\
                    u' dan 3 dagen geleden door de patient zijn ingevuld.' +\
                    u' \nWilt u deze Urgente Afspraken afhandelen?\n\n'

        self.do_report_check(
            body_test,
            send_urgent_report_reminder,
            'urgent_control_notification')

    def do_test_report_reminder(self):
        """
        Check if the report reminder sms/email function
        works correctly
        """
        body_test = u'\nEr zijn onafgehandelde Controles die meer dan 3' +\
                    u' weken geleden door de patient zijn ingevuld. \nWilt' +\
                    u' u deze Controles afhandelen?\n\n\n'

        self.do_report_check(
            body_test,
            send_report_reminder,
            'urgent_control_notification')

    def do_test_remove_deleted_patients(self):
        """
        Check if patients are automatically deleted
        """
        patient_count = Patient.objects.count()
        patient = Patient.objects.latest('id')
        patient.user.deleted_on = date.today()
        patient.user.save()

        user_id = patient.user.id

        remove_deleted_patients()
        self.assertEqual(Patient.objects.count(), patient_count)

        patient.user.deleted_on = date.today() - relativedelta(weeks=+2)
        patient.user.save()
        remove_deleted_patients()
        self.assertEqual(Patient.objects.count(), patient_count - 1)

        with self.assertRaises(Patient.DoesNotExist):
            Patient.objects.get(id=patient.id)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)

    def do_test_check_questionnaire_fillin_deadlines(self):
        """
        Check if the questionnaire fillin deadlines function works
        """
        self.reset_stores()
        questionnaire = QuestionnaireRequest.objects.filter(urgent=False)[0]
        patient = questionnaire.patient

        questionnaire.deadline = date.today() - relativedelta(days=+1)
        questionnaire.finished_on = None
        questionnaire.changed_by_user = patient.user
        questionnaire.save()

        patient.regular_control_reminder_notification = 'sms_and_email'
        patient.changed_by_user = patient.user
        patient.save()

        check_questionnaire_fillin_deadlines()

        self.assertEqual(len(settings.SMS_STORE), 1)
        self.assertEqual(len(mail.outbox), 1)

        new_questionnaire =\
            QuestionnaireRequest.objects.get(id=questionnaire.id)

        self.assertEqual(new_questionnaire.deadline,
                         date.today() + relativedelta(weeks=+1))
        self.assertEqual(new_questionnaire.deadline_nr,
                         questionnaire.deadline_nr + 1)

    def create_questionnaire_request(self, patient, date_time, is_handled):
        """
        Creates a questionnaire request

        Args:
            - patient: the patient to couple to the questionnaire request
            - date_time: the date & time to set as finished date
            - is_handled: set the handled_on to date_time if True
        """
        questionnaire_request = QuestionnaireRequest(patient=patient)
        questionnaire_request.urgent = False
        questionnaire_request.practitioner = patient.current_practitioner
        questionnaire_request.finished_on = date_time
        if is_handled:
            questionnaire_request.handled_on = date_time
        questionnaire_request.changed_by_user = patient.user
        questionnaire_request.save()

    def do_test_insert_new_questionnaire_requests(self):
        """
        Checks if insert new questionnaire request functions
        works correctly by testing a range of different scenario's
        """
        self.reset_stores()

        # No regular control frequency, should not be picked up
        patient = Patient.objects.get(id=5)
        patient.regular_control_frequency = 'never'
        patient.changed_by_user = patient.user
        patient.save()

        # Has an open questionnaire, should not be picked up
        patient = Patient.objects.get(id=6)
        self.create_questionnaire_request(
            patient,
            datetime.now(),
            False)

        # Filled in questionnaire one year ago, should be picked up
        patient = Patient.objects.get(id=7)
        self.create_questionnaire_request(
            patient,
            datetime.now() - relativedelta(years=+1),
            True)

        # Filled in questionnaire 6 months ago, should be picked up
        patient = Patient.objects.get(id=8)
        patient.regular_control_frequency = '6_months'
        patient.changed_by_user = patient.user
        patient.save()
        self.create_questionnaire_request(
            patient,
            datetime.now() - relativedelta(months=+6),
            True)

        # Filled in questionnaire within 6 months ago, should not be picked up
        patient = Patient.objects.get(id=9)
        patient.regular_control_frequency = '6_months'
        patient.changed_by_user = patient.user
        patient.save()
        self.create_questionnaire_request(
            patient,
            datetime.now() - relativedelta(months=+5),
            True)

        # Filled in questionnaire within 5 weeks, should not be picked up
        patient = Patient.objects.get(id=11)
        patient.regular_control_frequency = '5'
        patient.changed_by_user = patient.user
        patient.save()
        self.create_questionnaire_request(
            patient,
            datetime.now() - relativedelta(weeks=+4),
            True)

        # Filled in questionnaire 5 weeks ago, should be picked up
        patient = Patient.objects.get(id=13)
        patient.regular_control_frequency = '5'
        patient.changed_by_user = patient.user
        patient.save()
        self.create_questionnaire_request(
            patient,
            datetime.now() - relativedelta(weeks=+5),
            True)

        questionnaire_request_count = QuestionnaireRequest.objects.count()

        insert_new_questionnaire_requests()

        self.assertEqual(
            questionnaire_request_count + 3,
            QuestionnaireRequest.objects.count())

        # asserts
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=5).count(),
            0)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=6).count(),
            1)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=7).count(),
            2)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=8).count(),
            2)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=9).count(),
            1)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=11).count(),
            1)
        self.assertEqual(
            QuestionnaireRequest.objects.filter(
                patient__id=13).count(),
            2)

        self.assertEqual(len(settings.SMS_STORE), 3)
        self.assertEqual(len(mail.outbox), 3)

    def unhandeld_questionnaires_helper(self, urgent):
        """
        Helper functions for testing unhandeld questionnaires

        Args:
            - urgent: check urgent or not urgent
        """
        self.reset_stores()
        questionnaire = QuestionnaireRequest.objects.filter(urgent=urgent)[0]
        questionnaire.urgent = urgent
        hp = questionnaire.patient.current_practitioner
        hp.urgent_control_notification = 'sms_and_email'
        hp.changed_by_user = hp.user
        hp.save()
        questionnaire.finished_on = datetime.now()
        questionnaire.handled_on = None
        questionnaire.changed_by_user = hp.user
        questionnaire.save()

        if urgent:
            check_unhandled_urgent_questionnaires()
        else:
            check_unhandled_questionnaires()

        self.assertEqual(len(settings.SMS_STORE), 0)
        self.assertEqual(len(mail.outbox), 0)

        questionnaire.finished_on = datetime.now() - relativedelta(weeks=+3)
        questionnaire.handled_on = None
        questionnaire.save()

        if urgent:
            check_unhandled_urgent_questionnaires()
        else:
            check_unhandled_questionnaires()

        self.assertEqual(len(settings.SMS_STORE), 1)
        self.assertEqual(len(mail.outbox), 1)

    def do_test_unhandeld_questionnaires(self):
        """
        Check if reminder are sent to an healhprofessional
        for unhandeld filled-in questionnaires
        """
        self.unhandeld_questionnaires_helper(False)
        self.unhandeld_questionnaires_helper(True)

    def test_service_functions(self):
        """
        Test runner which performs all checks
        """
        # Speed up by using one test function so only
        # loading the fixtures once
        self.do_test_questionnaire_fillin_sms()
        self.do_test_questionnaire_reminder_sms()
        self.do_test_urgent_report_reminder()
        self.do_test_report_reminder()
        self.do_test_check_questionnaire_fillin_deadlines()
        self.do_test_insert_new_questionnaire_requests()
        self.do_test_unhandeld_questionnaires()

        # Do this one last or you probably get an error
        self.do_test_remove_deleted_patients()

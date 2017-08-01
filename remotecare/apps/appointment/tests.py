# -*- coding: utf-8 -*-
"""
Module provides tests for adding appointments

:subtitle:`Class definitions:`
"""
import locale
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse
from core.unittest.baseunittest import BaseUnitTest
from apps.questionnaire.models import QuestionnaireRequest


class AppointmentTest(BaseUnitTest):
    '''
    Test the appointment functionality by adding
    a appointment for a controle
    and an urgent controle
    '''
    fixtures = ['test_data/test_users.json',
                'test_data/report_repost_data.json']

    def check_appointment(self):
        """
        Add an appointment and check that it
        has been saved correctly
        """
        self.reset_stores()
        res = self.get(reverse('index'))

        questionnaire = res.context_data['controle_list'][0]

        session_key = self.get_session_key(
            questionnaire.patient.health_person_id)

        url = reverse(
            'appointment_edit',
            args=(session_key, questionnaire.id))

        questionnaire.finished_on = datetime.now()
        questionnaire.changed_by_user = questionnaire.patient.user
        questionnaire.save()

        # Check warning after trying to set appointment
        # outside the period the patient asked for.
        test_date =\
            questionnaire.appointment_period_date + relativedelta(days=+1)

        res = self.post_form(
            url,
            initial={'appointment_date': test_date,
                     'appointment_hour': str(test_date.hour).zfill(2),
                     'appointment_minute':
                     str(test_date.minute / 5 * 5).zfill(2),
                     'appointment_healthprofessional':
                     questionnaire.practitioner},
            check_status_code=False)

        self.assertEqual(res.context_data['show_warning'], True)

        # Repost the with the hiddenfield to overrule the warning

        res = self.post_form(
            url,
            initial={'appointment_date': test_date,
                     'appointment_hour': str(test_date.hour).zfill(2),
                     'appointment_minute':
                     str(test_date.minute / 5 * 5).zfill(2),
                     'appointment_healthprofessional':
                     questionnaire.practitioner},
            extra_data={'appointment_warning': 'True'},
            check_status_code=False)

        res = self.get(res.url)
        self.assertEqual(len(res.context_data['controle_list']), 0)

        questionnaire = QuestionnaireRequest.objects.get(id=questionnaire.id)
        appointment = questionnaire.appointment_set.all()[0]

        # sudo apt-get install language-pack-nl
        # sudo dpkg-reconfigure locales
        locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
        date = test_date.strftime("%A %e %B %Y")
        date = date.replace('  ', ' ')
        time = '{0}:{1}'.format(
            str(test_date.hour).zfill(2),
            str(test_date.minute / 5 * 5).zfill(2))

        # Check sms content
        sms_content = self.SMS_STORE[0]['message']
        self.assertIn(date, sms_content)
        self.assertIn(time, sms_content)
        self.assertIn(
            questionnaire.practitioner.user.professional_name,
            sms_content)

        message = questionnaire.rcmessage_set.all()[0]

        # Check message contents
        self.assertIn(date, message.internal_message)
        self.assertIn(time, message.internal_message)
        self.assertIn(
            questionnaire.practitioner.user.professional_name,
            message.internal_message)
        self.assertIn(
            questionnaire.practitioner.user.professional_name,
            message.internal_message)
        self.assertIn(
            appointment.appointment_healthprofessional.telephone,
            message.internal_message)

    def test_adding_appointment(self):
        """
        Run the check for both a non-urgent control
        and urgent-control
        """
        self.login('jim@example.com')

        # Check urgent appointment
        self.check_appointment()

        # Reset questionnaire (non urgent one)
        questionnaires = QuestionnaireRequest.objects.filter(urgent=False)
        for questionnaire in questionnaires:
            questionnaire.appointment_added_on = None
            questionnaire.appointment_needed = True
            questionnaire.handled_on = datetime.now()
            questionnaire.appointment_set.all().delete()
            questionnaire.rcmessage_set.all().delete()
            questionnaire.changed_by_user = questionnaire.patient.user
            questionnaire.save()

        # Check normal appointment
        self.check_appointment()

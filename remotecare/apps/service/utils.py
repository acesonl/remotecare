# -*- coding: utf-8 -*-
"""
Module providing reminder functions.

.. note:: The main function on the bottom should be run daily via a deamon
          or other solution around 9:00.

:subtitle:`Function definitions:`
"""
import sys
import os
import django
from django.db.models import Q
from datetime import date
from apps.questionnaire.models import QuestionnaireRequest
from dateutil.relativedelta import relativedelta
from django.template import loader
from apps.healthperson.patient.models import Patient
from apps.account.models import User
from apps.utils.utils import send_sms_to, send_email_to
from apps.questionnaire.views import\
    insert_new_questionnaire_request_for_patient as\
    insert_new_questionnaire_request_for_patient_func

sys.path.append('/srv/remotecare/default/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'remotecare.settings'
django.setup()


# ### Send questionnaire reminder sms
def send_questionnaire_reminder_sms(patient):
    '''
    Send a sms reminder to a patient who has not filled
    in a questionnaire
    '''
    current_date = date.today()
    healthprofessional = patient.current_practitioner

    context = {
        'patient': patient,
        'healthprofessional': healthprofessional,
        'current_date': current_date,
        'is_male': patient.user.gender == 'male'}

    sms_template = 'service/sms/questionnaire_reminder_sms.html'
    sms_template = loader.get_template(sms_template)
    sms_content = sms_template.render(context)

    email_template = 'service/email/questionnaire_reminder_email.html'
    email_template = loader.get_template(email_template)
    email_content = email_template.render(context)

    do_sms = (patient.regular_control_reminder_notification != 'email_only')
    do_email = (patient.regular_control_reminder_notification != 'sms_only')

    if do_sms:
        # send sms to patient
        send_sms_to(patient.user.mobile_number, sms_content)

    if do_email:
        send_email_to(patient.user.email, email_content)


# ### Send questionnaire fillin sms
def send_questionnaire_fillin_sms(patient):
    '''
    Send a sms and/or email
    message to a patient that a new series of questionnaires that
    should be filled in
    '''
    current_date = date.today()
    healthprofessional = patient.current_practitioner

    context = {
        'patient': patient,
        'healthprofessional': healthprofessional,
        'current_date': current_date,
        'is_male': patient.user.gender == 'male'}

    sms_template = 'service/sms/questionnaire_fillin_sms.html'
    sms_template = loader.get_template(sms_template)
    sms_content = sms_template.render(context)

    email_template = 'service/email/questionnaire_fillin_email.html'
    email_template = loader.get_template(email_template)
    email_content = email_template.render(context)

    do_sms = (patient.regular_control_start_notification != 'email_only')
    do_email = (patient.regular_control_start_notification != 'sms_only')

    if do_sms:
        # send sms to patient
        send_sms_to(patient.user.mobile_number, sms_content)

    if do_email:
        send_email_to(patient.user.email, email_content)


# ### Send urgent report reminder sms
def send_urgent_report_reminder(urgent_questionnaire_request):
    '''
    Send a message to healthprofessional about an urgent control
    which he/she has not created a report for.
    '''
    healthprofessional =\
        urgent_questionnaire_request.patient.current_practitioner

    context = {'healthprofessional': healthprofessional}

    sms_template = 'service/sms/urgent_report_reminder_sms.html'
    sms_template = loader.get_template(sms_template)
    sms_content = sms_template.render(context)

    email_template = 'service/email/urgent_report_reminder_email.html'
    email_template = loader.get_template(email_template)
    email_content = email_template.render(context)

    # check if to send sms or e-mail or both, or both to secretary.

    do_sms = True
    do_email = True

    mobile_number = healthprofessional.user.mobile_number
    email = healthprofessional.user.email

    if healthprofessional.urgent_control_secretary:
        mobile_number =\
            healthprofessional.urgent_control_secretary.user.mobile_number
        email = healthprofessional.urgent_control_secretary.user.email

    do_sms = (healthprofessional.urgent_control_notification != 'email_only')
    do_email = (healthprofessional.urgent_control_notification != 'sms_only')

    if do_sms:
        # send sms to healthprofessional
        send_sms_to(mobile_number, sms_content)

    if do_email:
        send_email_to(email, email_content)


# ### Send report reminder sms
def send_report_reminder(questionnaire_request):
    '''
    Send a message to healthprofessional about an controle
    which he/she has not created a report for.
    '''
    healthprofessional = questionnaire_request.patient.current_practitioner

    context = {'healthprofessional': healthprofessional}

    sms_template = 'service/sms/report_reminder_sms.html'
    sms_template = loader.get_template(sms_template)
    sms_content = sms_template.render(context)

    email_template = 'service/email/report_reminder_email.html'
    email_template = loader.get_template(email_template)
    email_content = email_template.render(context)

    mobile_number = healthprofessional.user.mobile_number
    email = healthprofessional.user.email

    if healthprofessional.urgent_control_secretary:
        mobile_number =\
            healthprofessional.urgent_control_secretary.user.mobile_number
        email = healthprofessional.urgent_control_secretary.user.email

    do_sms = (healthprofessional.urgent_control_notification != 'email_only')
    do_email = (healthprofessional.urgent_control_notification != 'sms_only')

    if do_sms:
        # send sms to healthprofessional
        send_sms_to(mobile_number, sms_content)

    if do_email:
        send_email_to(email, email_content)


def remove_deleted_patients():
    """
    Automatically remove patients that are set for deletion
    after 2 weeks
    """
    deadline = date.today() - relativedelta(weeks=+2)
    users = User.objects.filter(
        groups__name='patients',
        deleted_on__isnull=False,
        deleted_on__lte=deadline)

    # really delete all information..
    if users:
        for user in users:
            healthperson = user.healthperson
            healthperson.delete()
            user.delete()


# ## CHECK DEADLINE QUESTIONNAIRES
def check_questionnaire_fillin_deadlines():
    '''
    Check if deadlines for filling in questionnaires are passed
    '''
    # Get all (non urgent) questionnaire requests
    questionnaire_requests = QuestionnaireRequest.objects.filter(
        urgent=False, finished_on__isnull=True, deadline__lte=date.today())

    for questionnaire_request in questionnaire_requests:
        # update questionnaire request deadline
        questionnaire_request.deadline = date.today() + relativedelta(weeks=+1)
        questionnaire_request.deadline_nr =\
            questionnaire_request.deadline_nr + 1
        # Auditing, there is no service user so put the patient itselves
        questionnaire_request.changed_by_user =\
            questionnaire_request.patient.user
        questionnaire_request.save()

        # send reminder sms
        send_questionnaire_reminder_sms(questionnaire_request.patient)


# ## ADD QUESTIONNAIRE REQUEST ####
def insert_new_questionnaire_request_for_patient(patient):
    '''
    Add a new questionnaire request for a patient for periodic
    checking a patient.
    '''
    insert_new_questionnaire_request_for_patient_func(patient)

    # Send a sms to the patient, that he/she needs to fillin the questionnaire
    send_questionnaire_fillin_sms(patient)


def insert_new_questionnaire_requests():
    '''
    Helper function for adding a new questionnaire request
    '''
    # checks for which patients a new questionnaire request need to be added
    # check if has no open questionnaire request,
    # if so these should be finished first!
    patient_filter = Q(regular_control_frequency='never') |\
        (Q(questionnairerequest__finished_on__isnull=False) &
         Q(questionnairerequest__urgent=False) &
         Q(questionnairerequest__handled_on__isnull=True))

    for patient in Patient.objects.exclude(patient_filter):
        # check if need to sent new one.
        next_questionnaire_date = patient.next_questionnaire_date
        if ((not next_questionnaire_date or
             next_questionnaire_date <= date.today())):
            insert_new_questionnaire_request_for_patient(patient)


def check_unhandled_questionnaires():
    '''
    Check if there are unhandeld controls by healthprofessionals
    '''
    # check if the deadline (weeks +3) is passed, if so sent a reminder..

    deadline = date.today() - relativedelta(weeks=+3)
    urgent_questionnaire_requests = QuestionnaireRequest.objects.filter(
        urgent=False, finished_on__lte=deadline, handled_on__isnull=True)

    for urgent_questionnaire_request in urgent_questionnaire_requests:
        send_report_reminder(urgent_questionnaire_request)


def check_unhandled_urgent_questionnaires():
    '''
    Check if there are unhandeld urgent controls by healthprofessionals
    '''
    # check if the deadline (days +3) is passed, if so sent a reminder..
    deadline = date.today() - relativedelta(weeks=+3)
    urgent_questionnaire_requests = QuestionnaireRequest.objects.filter(
        urgent=True, finished_on__lte=deadline, handled_on__isnull=True)

    for urgent_questionnaire_request in urgent_questionnaire_requests:
        send_urgent_report_reminder(urgent_questionnaire_request)


# Run all daily checks and other services
def main_run_daily():  # pragma: no cover
    '''
    Function which can be called daily to perform all necessary checks.

    .. note:: Should be run around 09:00. !!NOT AT MIDNIGHT!!
              since people are going to get SMS notifications.
    '''
    # step 1: remove patients that are set to be deleted
    remove_deleted_patients()

    # step 2: insert new questionnaires
    insert_new_questionnaire_requests()

    # step 3: check and sms accordingly to the questionnaire deadlines
    check_questionnaire_fillin_deadlines()

    # step 3: check and sms accordingly to unhandled urgent questionnaires
    check_unhandled_urgent_questionnaires()

    # step 4: check and sms accordingly to unhandled questionnaires
    check_unhandled_questionnaires()

if __name__ == '__main__':  # pragma: no cover
    '''
    Note: Run this command around 09:00 daily
    '''
    main_run_daily()

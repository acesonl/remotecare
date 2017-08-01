# -*- coding: utf-8 -*-
"""
This module contains functions for sending email and SMS messages
to Remote Care users.

:subtitle:`Function definitions:`
"""
import messagebird
from datetime import date
from core.encryption.hash import create_hmac
from apps.mollie.api import Mollie
from apps.mollie.exceptions import MollieException
from apps.account.models import User
from django.conf import settings

from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from core.encryption.random import randomkey

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


def send_email_to(email_adres, email_content,
                  subject='Remote Care - notificatie'):
    '''
    Generic function for sending email to email_adres with email_content

    Args:
        - email_adres: the receiver of the email
        - email_content: the body of the email
    '''

    from_email, to = 'remotecare@example.com', email_adres

    # this strips the html, so people will have the text as well.
    text_content = strip_tags(email_content)

    # create the email, and attach the HTML version as well.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(email_content, "text/html")
    msg.send()


def send_authorisation_sms_to(mobile_number, auth_code):
    '''
    Wrapper function for later usage

    Args:
        - mobile_number: the mobile number to sent auth_code to
        - auth_code: the SMS message to sent
    '''
    send_sms_to(mobile_number, auth_code)


def send_sms_to_patient(patient, content):
    '''
    Generic function for sending an SMS message to a patient
    Automatic strips the content so it fits within 160 characters.

    Args:
        - patient: the patient to sent the SMS to
        - content: The content of the SMS message
    '''
    content = str(content)
    if len(content) > 160:
        content = content[:160]
    send_sms_to(patient.user.mobile_number, content)


def send_sms_to(mobile_number, auth_code):
    '''
    Generic function which sents the sms using Mollie services.

    Args:
        - mobile_number: the mobile_number to sent the SMS message to
        - auth_code: The content of the SMS message
    '''
    succes = False
    if not settings.MOLLIE_FAKE:
#        try:
#            Mollie.sendsms(username=settings.MOLLIE_USERNAME,
#                           password=settings.MOLLIE_PASSWORD,
#                           originator='RemoteCare',
#                           recipients=mobile_number,
#                           message=auth_code,
#                           molliegw=Mollie.SECURE_MOLLIEGW,
#                           gateway=Mollie.DUTCH_GW
#                           )
#            succes = True
#        except MollieException:
#            raise
#            succes = False
        try:
            client = messagebird.Client(settings.MESSAGE_BIRD_ACCESS_KEY)
            msg = client.message_create('RemoteCare', mobile_number, auth_code, {'reference': 'RemoteCare'})
            print(msg.__dict__)
        except messagebird.client.ErrorException as e:
            raise
            success = False
    else:
        settings.SMS_STORE.append({'recipients': mobile_number,
                                   'message': auth_code})

        if not settings.AUTOMATIC_TESTING and settings.DEBUG:
            print(('sms_to: {0}, message: {1}'.format(
                mobile_number, auth_code)))
    return succes


def generic_sent_notification_to_patient(patient, sms_template,
                                         email_template,
                                         notification_setting):
    '''
    Generic function which is used for sending regular control
    reminders to a patient

    Args:
        - patient: the patient to sent the message(s) to
        - sms_template: the sms message to sent to a patient
        - email_template: the email message to sent to a patient
    '''
    current_date = date.today()
    context = {
        'patient': patient,
        'current_date': current_date,
        'is_male': patient.user.gender == 'male'}

    do_sms = (notification_setting != 'email_only')
    do_email = (notification_setting != 'sms_only')

    if do_sms:
        sms_template = loader.get_template(sms_template)
        sms_content = sms_template.render(context)
        send_sms_to(patient.user.mobile_number, sms_content)
    if do_email:
        email_template = loader.get_template(email_template)
        email_content = email_template.render(context)
        send_email_to(patient.user.email, email_content)


def send_notification_of_new_report(patient):
    '''
    Send a notification of a new report to a patient

    Args:
        - patient: the patient to sent the message(s) to
    '''
    generic_sent_notification_to_patient(
        patient,
        'utils/sms/report_notify_sms.html',
        'utils/email/report_notify_email.html',
        patient.healthprofessional_handling_notification)


def send_notification_of_new_message(patient):
    '''
    Send a notification of a new message to a patient

    Args:
        - patient: the patient to sent the message(s) to
    '''
    generic_sent_notification_to_patient(
        patient,
        'utils/sms/message_notify_sms.html',
        'utils/email/message_notify_email.html',
        patient.message_notification)


def get_password_change_request(email_key):
    '''
    Try to get the current password request and
    automatically remove expired ones.

    Args:
        - email_key: The original email_key stored in HMAC format in the\
                     passwordchangerequest.

    Returns:
        The associated PasswordChangeRequest instance or None
    '''
    from apps.account.models import PasswordChangeRequest
    hmac_email_key = create_hmac(settings.EMAIL_KEY, str(email_key))

    # Automatically remove expired requests
    try:
        passwordchangerequest = PasswordChangeRequest.objects.get(
            hmac_email_key=hmac_email_key)
        if passwordchangerequest.is_expired:
            passwordchangerequest.delete()
            return None
        else:
            return passwordchangerequest
    except PasswordChangeRequest.DoesNotExist:
        return None


def get_user_for_password_change_request(email_key):
    '''
    Retrieves the user coupled to a password change_request

    Args:
        - email_key: The original email_key stored in HMAC format in the\
                     passwordchangerequest.

    Returns:
        The User for the associated PasswordChangeRequest instance or None
    '''
    from apps.account.models import PasswordChangeRequest

    hmac_email_key = create_hmac(settings.EMAIL_KEY, str(email_key))
    passwordchangerequest = PasswordChangeRequest.objects.get(
        hmac_email_key=hmac_email_key)

    return passwordchangerequest.user


def change_password(email_key, password, sms_code):
    '''
    Change password by checking email_key, password and sms_code

    Args:
        - email_key: The original email_key stored in HMAC format in the\
                     passwordchangerequest.
        - password: the new password to set
        - sms_code: the SMS authorization code to check

    Returns:
        True if the password has been changed else False
    '''
    from apps.account.models import PasswordChangeRequest
    from apps.account.models import OldPassword
    hmac_email_key = create_hmac(settings.EMAIL_KEY, str(email_key))
    hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))

    passwordchangerequest = PasswordChangeRequest.objects.get(
        hmac_email_key=hmac_email_key)

    # Check if sms code is correct
    if passwordchangerequest.hmac_sms_code != hmac_sms_code:
        return False

    user = passwordchangerequest.user
    user.changed_by_user = user
    # Set password and add to old passwords for password validation rules
    user.set_password(password)
    OldPassword.objects.create(user=user, password_hash=user.password)
    user.save()
    password = None

    # delete the passwordchangerequest
    passwordchangerequest.delete()
    return True


def sent_password_change_sms(email_key, email, date_of_birth,
                             sent_sms=True, sms_code=None):
    '''
    Sent password change sms, last two parameters are for debugging which
    can be removed in production stage.

    Args:
        - email_key: The original email_key stored in HMAC format in the\
                     passwordchangerequest.
        - date_of_birth: the date_of_birth to check
        - sent_sms: need to sent SMS authorization code? (default=True)
        - sms_code: override sms authorization code

    Returns:
        True if the password change authorization SMS has been sent
    '''
    from apps.account.models import PasswordChangeRequest
    hmac_email_key = create_hmac(settings.EMAIL_KEY, str(email_key))
    passwordchangerequest = PasswordChangeRequest.objects.get(
        hmac_email_key=hmac_email_key)

    # Create random sms_code if not provided
    if not sms_code:
        sms_code = User.objects.make_random_password(length=8)
    hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))
    user = passwordchangerequest.user

    if user.email != email or user.date_of_birth != date_of_birth:
        return False

    passwordchangerequest.hmac_sms_code = hmac_sms_code
    passwordchangerequest.save()

    if sent_sms:
        send_authorisation_sms_to(user.mobile_number, sms_code)

    # Remove old reference
    sms_code = None

    return True


def send_password_change_email(url_prefix, request_id, email_adres, email_key,
                               change_request_by_manager=False,
                               new_account=False):
    from apps.account.models import PasswordChangeRequest
    '''
    Function which sents the password reset e-mail
    containing a link to the password reset page.

    Args:
        - url_prefix: the url prefix to use in the email
        - request_id: the PasswordChangeRequest id
        - email_adres: the email_adres to sent the email to
        - email_key: the key to include in the email
        - change_request_by_manager: did a manager requested the change?
        - new_account: is this a new user?
    '''
    passwordchangerequest = get_object_or_404(
        PasswordChangeRequest, pk=request_id)

    context = {
        'passwordchangerequest': passwordchangerequest,
        'email_key': email_key,
        'url_prefix': url_prefix,
        'change_request_by_manager': change_request_by_manager,
        'new_account': new_account
    }

    html_content = render_to_string(
        'emails/link_to_change_password_email.html', context=context)

    send_email_to(email_adres, html_content,
                  'Remote Care - Wachtwoord instellen')


def sent_password_change_request(user, url_prefix,
                                 change_request_by_manager=False,
                                 new_account=False):
    '''
    Sent an e-mail with a password change request to an users e-mail address

    Args:
        - user: the user to sent the password change request email to.
        - url_prefix: the url prefix to use in the email
        - change_request_by_manager: is this change initialized by a manager?
        - new_account: is this a new user?
    '''
    from apps.account.models import PasswordChangeRequest
    email_key = randomkey(40)

    hmac_email_key = create_hmac(settings.EMAIL_KEY, str(email_key))
    passwordchangerequest = PasswordChangeRequest.objects.filter(user=user)

    # remove all past requests..
    for pass_request in passwordchangerequest:
        pass_request.delete()

    # Create a new one..
    passwordchangerequest = PasswordChangeRequest(
        user=user,
        hmac_email_key=hmac_email_key,
        attempt_nr=None)
    passwordchangerequest.save()

    # sent email
    send_password_change_email(
        url_prefix, passwordchangerequest.id, user.email, email_key,
        change_request_by_manager, new_account)

    # Set current password to invalid
    user.set_unusable_password()
    user.save()


# create and send sms_code..
def create_login_sms_code(user, send_sms=True, sms_code=None):
    '''
    Create and sent a login SMS code to an user
    the sms_code is stored in HMAC format.

    Args:
        - user: the user to sent the login SMS authorization code to.
        - send_sms: do sent a SMS authorization code? (default=True)
        - sms_code: override the random sms_code
    '''
    from apps.account.models import LoginSMSCode

    # Always use the same one, no need to create multiple instances
    [loginsmscode, created] = LoginSMSCode.objects.get_or_create(user=user)

    if not sms_code:
        sms_code = User.objects.make_random_password(length=8)
        hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))
        while ((LoginSMSCode.objects.filter(
                hmac_sms_code=hmac_sms_code).count() != 0)):
            sms_code = User.objects.make_random_password(length=8)
            hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))
    else:
        # DEBUG!!
        hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))
        LoginSMSCode.objects.filter(hmac_sms_code=hmac_sms_code).delete()

    loginsmscode.hmac_sms_code = hmac_sms_code

    if send_sms:
        send_authorisation_sms_to(user.mobile_number, sms_code)
    sms_code = None
    loginsmscode.save()


def check_login_sms_code(sms_code):
    '''
    Check if the sms_code is correct, returns the user coupled
    to this sms_code which can be further validated.

    Args:
        - sms_code: the SMS authorization code sent during login, stored\
                    in HMAC form in a LoginSMSCode instance.

    Returns:
        The User instance for the login SMS authorization code or None
    '''
    from apps.account.models import LoginSMSCode
    hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))

    try:
        loginsmscode = LoginSMSCode.objects.get(hmac_sms_code=hmac_sms_code)
    except LoginSMSCode.DoesNotExist:
        loginsmscode = None

    if loginsmscode:
        return loginsmscode.user

    return None

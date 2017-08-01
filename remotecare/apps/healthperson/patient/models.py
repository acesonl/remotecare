# -*- coding: utf-8 -*-
"""
This module contains the patient model definition.
The patient is coupled to a :class:`apps.account.models.User`
instance via the :class:`apps.healthperson.models.HealthPerson` baseclass.

Inheritance-diagram:

.. inheritance-diagram::\
    apps.healthperson.patient.models.Patient

:subtitle:`Class and function definitions:`
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.translation import ugettext as _
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.healthperson.models import HealthPerson
from core.models import ChoiceOtherField, AuditBaseModel
from django.utils.functional import cached_property

DIAGNOSIS_CHOICES = (
    ('rheumatoid_arthritis', ('Reumatoide artritis')),
    ('chron', ('Ziekte van Crohn')),
    ('colitis_ulcerosa', ('Colitis Ulcerosa')),
    ('intestinal_transplantation', ('Dunnedarmtransplantatie')),
)

REGULAR_CONTROL_FREQ = (
    ('never', ('Nooit')),
    ('3_months', ('3 maanden')),
    ('6_months', ('6 maanden')),
    ('12_months', ('12 maanden')),
    ('other', ('Anders, vul aantal weken in')),
)

BLOOD_SAMPLE_FREQ = (
    ('sameasregular', ('Zelde als freq. regulier controle')),
    ('3_months', ('3 maanden')),
    ('6_months', ('6 maanden')),
    ('12_months', ('12 maanden')),
    ('other', ('Anders, vul aantal weken in')),
)

CLINIC_VISIT_CHOICES = (
    ('alwaysclinicvisit', ('Altijd na invullen vragenlijsten')),
    ('onlyifwanted', ('Alleen als gewenst of vereist')),
)

NOTIFICATION_CHOICES = (
    ('sms_and_email', ('Zowel per e-mail als per sms')),
    ('sms_only', ('Alleen per sms')),
    ('email_only', ('Alleen per e-mail')),
)


def add_weken(number):
    """
    Adds 'week' or 'weken' to the provided number

    Args:
        - number: the number of weeks

    Returns:
        the number with 'week' or 'weken' appended
    """
    rt = ''

    try:
        number = int(number)
        if number == 1:
            rt = str(number) + ' ' + _('week')
        else:
            rt = str(number) + ' ' + _('weken')
    except ValueError:
        rt = str(number)
    return rt


class Patient(HealthPerson, AuditBaseModel):
    '''
    Stores patient specific information.
    '''
    rc_registration_number = models.CharField(
        max_length=128,
        unique=True)

    diagnose = models.CharField(
        choices=DIAGNOSIS_CHOICES,
        max_length=128,
        verbose_name=_('Diagnose'))

    excluded_questionnaires = models.TextField(
        null=True,
        blank=True)

    current_practitioner = models.ForeignKey(
        HealthProfessional,
        verbose_name=_('Hoofd-behandelaar'))

    regular_control_frequency = ChoiceOtherField(
        choices=REGULAR_CONTROL_FREQ,
        max_length=128,
        verbose_name=_('Frequentie reguliere controle'))

    blood_sample_frequency = ChoiceOtherField(
        choices=BLOOD_SAMPLE_FREQ,
        max_length=128,
        verbose_name=_('Frequentie bloedprikken'))

    last_blood_sample = models.DateField(
        null=True,
        blank=True)

    always_clinic_visit = models.CharField(
        choices=CLINIC_VISIT_CHOICES,
        max_length=128,
        verbose_name=_('Volgt altijd een polikliniekbezoek?'))

    # Notification settings
    regular_control_start_notification = models.CharField(
        choices=NOTIFICATION_CHOICES,
        default='sms_and_email',
        max_length=32,
        verbose_name=_('Starten van een reguliere controle'))

    regular_control_reminder_notification = models.CharField(
        choices=NOTIFICATION_CHOICES,
        default='sms_and_email',
        max_length=32,
        verbose_name=_('Herinneringen bij een reguliere controle, ' +
                       'indien deze niet binnen 1 week is ingevuld.'))

    healthprofessional_handling_notification = models.CharField(
        choices=NOTIFICATION_CHOICES,
        default='sms_and_email',
        max_length=32,
        verbose_name=_('Uitslag van een controle of' +
                       ' "het gaat niet goed" nadat de' +
                       ' behandelaar deze heeft' +
                       ' beoordeeld en verwerkt.'))

    message_notification = models.CharField(
        choices=NOTIFICATION_CHOICES,
        default='sms_and_email',
        max_length=32,
        verbose_name=_('Overige berichten van een arts of verpleegkundige.'))

    @cached_property
    def last_questionnaire_date(self):
        """
        Returns:
            The last questionnaire date or None
        """
        if hasattr(self, 'patient_last_questionnaire_date'):
            return self.patient_last_questionnaire_date

        from apps.questionnaire.models import QuestionnaireRequest
        try:
            questionnaire_request = self.questionnairerequest_set.filter(
                finished_on__isnull=False, urgent=False).latest('id')
        except QuestionnaireRequest.DoesNotExist:
            questionnaire_request = None

        if questionnaire_request:
            self.patient_last_questionnaire_date =\
                questionnaire_request.finished_on
            return questionnaire_request.finished_on

        return None

    @property
    def timedelta_since_last_questionnaire(self):
        """
        Returns:
            The timedelta since the last questionnaire date or None
        """
        finished_date = self.last_questionnaire_date

        if finished_date:
            time_delta = date.today() - finished_date
            return time_delta

        return None

    @property
    def days_since_last_questionnaire(self):
        """
        Returns:
            The days since the last questionnaire date or None
        """
        time_delta = self.timedelta_since_last_questionnaire

        if time_delta is not None:
            return time_delta.days
        return None

    @property
    def next_questionnaire_ready(self):
        """
        Returns:
            True if the next questionnaire is ready, which means it should\
            be filled in. False otherwise.
        """
        next_date = self.next_questionnaire_date

        if next_date:
            if next_date <= date.today():
                return True
        else:
            return True

        return False

    @property
    def next_questionnaire_date(self):
        """
        Returns:
            The next questionnaire date based on the last_questionnaire_date\
            and the control_frequency setting or None
        """
        finished_on = self.last_questionnaire_date

        control_freq = self.regular_control_frequency
        if control_freq != 'never' and finished_on:
            if control_freq == '3_months':
                time_delta = relativedelta(months=+3)
            elif control_freq == '6_months':
                time_delta = relativedelta(months=+6)
            elif control_freq == '12_months':
                time_delta = relativedelta(months=+12)
            else:
                try:
                    time_delta = relativedelta(weeks=+int(control_freq))
                except ValueError:
                    return None
            return finished_on + time_delta
        return None

    @property
    def always_appointment(self):
        """
        Returns:
            True if there should always follow an appointment after the
            periodic control
        """
        return self.always_clinic_visit == 'alwaysclinicvisit'

    @property
    def display_regular_control_frequency(self):
        """
        Returns:
            The regular control frequency in readable format.
        """
        if ((self.regular_control_frequency not in
             [x for (x, y) in REGULAR_CONTROL_FREQ])):
            frequency = add_weken(self.regular_control_frequency)
        else:
            frequency = self.get_regular_control_frequency_display()
        return frequency

    @property
    def display_blood_sample_frequency(self):
        """
        Returns:
            The blood sample frequency in readable format.
        """
        if ((self.blood_sample_frequency not in
             [x for (x, y) in BLOOD_SAMPLE_FREQ])):
            frequency = add_weken(self.blood_sample_frequency)
        else:
            frequency = self.get_blood_sample_frequency_display()
        return frequency

    @property
    def include_blood_taken_questions(self):
        """
        Returns:
            True if the blood taken questions should be included,
            which is based on the blood sample frequency and
            the last last_blood_taken_date. False otherwise.
        """
        if not hasattr(self, 'patient_include_blood_taken_questions'):
            self.patient_include_blood_taken_questions = False
            last_blood_taken_date = self.last_blood_taken_date
            # check based on the current date and blood_sample_frequency
            # if the questions need to be included...
            current_date = date.today()

            control_freq = None
            time_delta = None
            if self.blood_sample_frequency == 'sameasregular':
                control_freq = self.regular_control_frequency
            else:
                control_freq = self.blood_sample_frequency

            if control_freq != 'never':
                if control_freq == '3_months':
                    time_delta = relativedelta(months=+3)
                elif control_freq == '6_months':
                    time_delta = relativedelta(months=+6)
                elif control_freq == '12_months':
                    time_delta = relativedelta(months=+12)
                else:
                    try:
                        time_delta = relativedelta(weeks=+int(control_freq))
                    except ValueError:
                        self.patient_include_blood_taken_questions = False
                        return self.patient_include_blood_taken_questions

                # if last_blood_taken_date is not set, return true
                if not last_blood_taken_date:
                    self.patient_include_blood_taken_questions = True
                else:
                    # calculate the date to test
                    test_date = last_blood_taken_date + time_delta

                    # if the current_date is larger or
                    # equal to the test date return true
                    if current_date >= test_date:
                        self.patient_include_blood_taken_questions = True

        return self.patient_include_blood_taken_questions

    @property
    def blood_taken_freq_display(self):
        """
        Returns:
            Returns the blood taken frequency in readable format
        """
        if self.blood_sample_frequency == 'sameasregular':
            frequency = self.display_regular_control_frequency
        else:
            frequency = self.display_blood_sample_frequency

        return frequency

    @property
    def last_blood_taken_date(self):
        """
        Returns:
            The last date when blood was taken or None
        """
        from apps.questionnaire.default.models import FinishQuestionnaire
        # return the last date or None
        try:
            # search via request_step__questionnairerequest__patient
            finishquestionnaire = FinishQuestionnaire.objects.filter(
                request_step__questionnairerequest__patient=self).latest('id')
            blood_taken_date = finishquestionnaire.blood_sample_date
        except FinishQuestionnaire.DoesNotExist:
            blood_taken_date = None

        return blood_taken_date

    @property
    def name(self):
        return _('Patient')

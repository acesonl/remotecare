# -*- coding: utf-8 -*-
"""
Appointments can be requested by a patient during filling in the
questionnaires or by a healthprofessional.

The appointment is created by a secretary and coupled to a healthprofessional.
The patient is automatically notified when the appointment has been created.

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.dates import WEEKDAYS
from django.utils.translation import ugettext as _

from core.models import DateField, AuditBaseModel
from apps.healthperson.secretariat.models import Secretary
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.questionnaire.models import QuestionnaireRequest

HOUR_CHOICES = (
    ('01', '01'),
    ('02', '02'),
    ('03', '03'),
    ('04', '04'),
    ('05', '05'),
    ('06', '06'),
    ('07', '07'),
    ('08', '08'),
    ('09', '09'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
)

MINUTE_CHOICES = (
    ('00', '00'),
    ('05', '05'),
    ('10', '10'),
    ('15', '15'),
    ('20', '20'),
    ('25', '25'),
    ('30', '30'),
    ('35', '35'),
    ('40', '40'),
    ('45', '45'),
    ('50', '50'),
    ('55', '55'),
)


class Appointment(AuditBaseModel):
    '''
    An appointment is coupled to a questionnaire_request which couples it
    to a patient. The appointment is created by a secretary and takes
    place with a healthprofessional.
    '''
    questionnaire_request = models.ForeignKey(QuestionnaireRequest)
    created_by = models.ForeignKey(Secretary)
    created_on = models.DateField(auto_now_add=True)

    appointment_date = DateField(
        future=True, allow_future_date=True, verbose_name=_('Afspraak datum'))
    appointment_hour = models.CharField(
        choices=HOUR_CHOICES, max_length=4, verbose_name=_('Afspraak tijd'))
    appointment_minute = models.CharField(choices=MINUTE_CHOICES, max_length=4)
    appointment_healthprofessional = models.ForeignKey(
        HealthProfessional, verbose_name=_('Behandelaar'))

    @property
    def get_day(self):
        """
        Returns te day of the week (monday, tuesday, etc)
        """
        return WEEKDAYS[self.appointment_date.weekday()]

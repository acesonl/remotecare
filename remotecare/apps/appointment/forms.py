# -*- coding: utf-8 -*-
"""
Contains the form for adding and editing appointments

:subtitle:`Class and function definitions:`
"""
import datetime
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.appointment.models import Appointment
from core.forms import BaseModelForm
from apps.healthperson.healthprofessional.models import HealthProfessional


def change_empty_choice(field, to_set):
    """
    Change the empty choice (first entry) of a Select field
    """
    choices = field.choices
    choices[0] = ('', to_set)
    field.choices = choices


class AppointmentAddEditForm(BaseModelForm):
    '''
    Form class for adding/editing appointments

    '''
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        user = kwargs.pop('user', None)

        self.questionnaire_request = kwargs.pop('questionnaire_request', None)
        super(AppointmentAddEditForm, self).__init__(*args, **kwargs)

        if user:
            health_professionals_list = HealthProfessional.objects.filter(
                user__hospital=user.hospital)
        else:
            health_professionals_list = []

        health_professionals = [
            (hp.health_person_id,
                hp.user.professional_name) for hp in health_professionals_list]

        health_professionals.insert(0, ('', '---------'))
        self.fields['appointment_healthprofessional'].choices =\
            health_professionals

        if instance:
            self.fields['appointment_healthprofessional'].initial =\
                instance.current_practitioner.health_person_id
        change_empty_choice(self.fields['appointment_hour'], '---')
        change_empty_choice(self.fields['appointment_minute'], '---')

    def clean(self):
        cleaned_data = super(AppointmentAddEditForm, self).clean()

        if (('appointment_hour' in cleaned_data and
             'appointment_minute' in cleaned_data and
             'appointment_date' in cleaned_data)):
            date = cleaned_data['appointment_date']
            time = datetime.time(
                int(cleaned_data['appointment_hour']),
                int(cleaned_data['appointment_minute']))
            if ((datetime.datetime.combine(date, time) <
                 datetime.datetime.now())):
                self.errors['appointment_date'] = ErrorList(
                    [_('Tijdstip moet in de toekomst liggen.')])

        return cleaned_data

    class Meta:
        model = Appointment
        exclude = ('questionnaire_request', 'created_by', 'created_on',)
        fields = ['appointment_date', 'appointment_hour',
                  'appointment_minute', 'appointment_healthprofessional']

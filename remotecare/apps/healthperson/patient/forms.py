# -*- coding: utf-8 -*-
"""
This module only contains the forms for a patient for searching filled-in
information, editing notifications settings, and editing personalia.
For managers/secretary/healthprofessionals forms are included for
administration of patients.

:subtitle:`Class definitions:`
"""
from django import forms
from datetime import date
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from core.forms import BaseModelForm, BaseForm,\
        ChoiceOtherField, FormDateField, MultipleChoiceField
from apps.healthperson.patient.models import Patient,\
    DIAGNOSIS_CHOICES, REGULAR_CONTROL_FREQ,\
    BLOOD_SAMPLE_FREQ, CLINIC_VISIT_CHOICES
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.account.forms import BaseProfileEditForm, BasePasswordProfileEditForm

PASSWORD_CHOICES = (
    ('', ('---------')),
    ('yes', ('Ja')),
    ('no', ('Nee')),
)


class PatientSearchForm(BaseForm):
    """
    Search for a patient.
    Used by all healthpersons except for patients.
    """
    BSN = forms.CharField(
        max_length=128, label=_('BSN'), required=False)
    local_hospital_number = forms.CharField(
        max_length=128, label=_('Lokaal ziekenhuisnummer'), required=False)
    last_name = forms.CharField(
        max_length=128, label=_('Achternaam'), required=False)
    years = list(range(date.today().year - 100, date.today().year + 1))
    date_of_birth = FormDateField(
        label=_('Geboortedatum'), years=years, allow_future_date=False,
        future=False, required=False)


class PatientDiagnoseControleEditForm(BaseModelForm):
    """
    Edit the diagnose and controle settings.
    Used by a healthprofessional or manager.
    """
    exclude_questionnaires = MultipleChoiceField(
        label=_('Selecteer vragenlijsten'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(PatientDiagnoseControleEditForm, self).__init__(*args, **kwargs)

        health_professionals = []
        hospital = None
        if instance.user:
            hospital = instance.user.hospital

        health_professionals_list = HealthProfessional.objects.filter(
            user__hospital=hospital)

        for health_professional in health_professionals_list:
            health_professionals.append(
                (health_professional.id,
                 health_professional.user.professional_name))

        health_professionals.insert(0, ('', '---------'))
        self.fields['current_practitioner'].choices = health_professionals

        # self.fields['exclude_questionnaires'].choices = health_professionals

        if instance:
            self.fields['current_practitioner'].initial =\
                instance.current_practitioner.id

        self.fields['diagnose'].widget.attrs.update(
            {'class': 'choice_display_diagnose'})

    def clean(self):
        cleaned_data = super(PatientDiagnoseControleEditForm, self).clean()
        del self.errors['exclude_questionnaires']
        return cleaned_data

    class Meta:
        model = Patient
        exclude = ('rc_registration_number', 'last_blood_sample',
                   'health_person_id', 'added_on', 'added_by',
                   'regular_control_start_notification',
                   'regular_control_reminder_notification',
                   'healthprofessional_handling_notification',
                   'message_notification')
        fieldsets = (
            (None, {'fields': ('diagnose',)}),
            ('diagnose', {'fields': ('exclude_questionnaires', )}),
            (None, {'fields': ('current_practitioner',
                               'regular_control_frequency',
                               'blood_sample_frequency',
                               'always_clinic_visit')}),
        )


class PatientNotificationEditForm(BaseModelForm):
    """
    Edit the notification settings.
    Used by a patient.
    """
    class Meta:
        model = Patient
        exclude = ('health_person_id', 'rc_registration_number',
                   'diagnose', 'current_practitioner', 'prefix',
                   'regular_control_frequency',
                   'blood_sample_frequency', 'last_blood_sample',
                   'always_clinic_visit', 'excluded_questionnaires')
        fieldsets = (
            (None, {'fields': ('regular_control_start_notification',
                               'regular_control_reminder_notification',
                               'healthprofessional_handling_notification',
                               'message_notification',)}),
        )


class PatientProfileEditForm(BasePasswordProfileEditForm):
    '''
    Edit patient profile form
    used by the patient self
    '''
    class Meta(BasePasswordProfileEditForm.Meta):
        exclude = BasePasswordProfileEditForm.Meta.exclude + (
            'BSN', 'local_hospital_number',
            'initials', 'prefix', 'gender', 'date_of_birth',
            'last_name', 'first_name',
            'title', 'hospital',)

        fieldsets = (
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'change_password')}),
            ('change_password', {'fields': ('password', 'password2')}),
        )


class PatientPersonaliaEditForm(BasePasswordProfileEditForm):
    '''
    Edit patient profile form
    used by an healthprofessional and secretary
    '''
    class Meta(BasePasswordProfileEditForm.Meta):
        exclude = BasePasswordProfileEditForm.Meta.exclude
        fieldsets = (
            (None, {'fields': ('BSN',
                               'local_hospital_number', 'hospital',
                               'title', 'first_name', 'initials',
                               'prefix', 'last_name', 'gender',
                               'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2')}),
        )


class PatientPersonaliaEditFormManager(BasePasswordProfileEditForm):
    '''
    Edit patient profile form
    used by an manager.
    '''
    # Validators
    change_password = forms.TypedChoiceField(
        choices=PASSWORD_CHOICES,
        label=_('Maak wachtwoord ongeldig?'), required=False)

    class Meta(BasePasswordProfileEditForm.Meta):
        exclude = BasePasswordProfileEditForm.Meta.exclude
        fieldsets = (
            (None, {'fields': ('BSN',
                               'local_hospital_number',
                               'hospital', 'title',
                               'first_name', 'initials', 'prefix',
                               'last_name', 'gender',
                               'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'change_password')}),
        )


class PatientAddForm(BaseProfileEditForm):
    '''
    Add new patient form
    '''
    # Diagnose
    diagnose = forms.TypedChoiceField(
        label=_('Diagnose'), required=True)

    # current_practitioner
    current_practitioner = forms.ChoiceField(
        label=_('Hoofdbehandelaar'), required=True)

    # Regular control freq.
    reqular_control_choices = list(REGULAR_CONTROL_FREQ)
    reqular_control_choices.insert(0, ('', '---------'))
    regular_control_frequency = ChoiceOtherField(
        choices=reqular_control_choices,
        other_field=forms.TextInput,
        label=_('Frequentie reguliere controle'), required=True)

    # Blood sample frequency
    blood_sample_choices = list(BLOOD_SAMPLE_FREQ)
    blood_sample_choices.insert(0, ('', '---------'))
    blood_sample_frequency = ChoiceOtherField(
        choices=blood_sample_choices,
        other_field=forms.TextInput,
        label=_('Frequentie bloedprikken'), required=True)

    # Always clinic visit
    always_clinic_choices = list(CLINIC_VISIT_CHOICES)
    always_clinic_choices.insert(0, ('', '---------'))
    always_clinic_visit = forms.ChoiceField(
        choices=always_clinic_choices,
        label=_('Volgt altijd een polikliniekbezoek?'), required=True)

    exclude_questionnaires = MultipleChoiceField(
        label=_('Selecteer vragenlijsten'))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PatientAddForm, self).__init__(*args, **kwargs)
        self.user = user

        # Set diagnose list
        diagnose_choices = list(DIAGNOSIS_CHOICES)
        diagnose_choices.insert(0, ('', '---------'))
        self.fields['diagnose'].choices = diagnose_choices

        # set health professionals choices
        health_professionals = []
        if user:
            health_professionals_list = HealthProfessional.objects.filter(
                user__hospital=user.hospital)

            for health_professional in health_professionals_list:
                health_professionals.append(
                    (health_professional.health_person_id,
                     health_professional.user.professional_name))

        health_professionals.insert(0, ('', '---------'))
        self.fields['current_practitioner'].choices = health_professionals
        self.fields['diagnose'].widget.attrs.update(
            {'class': 'choice_display_diagnose'})

    def clean(self):
        cleaned_data = super(PatientAddForm, self).clean()

        del self.errors['exclude_questionnaires']

        # Check if 'other' in frequency fields is digit
        if (('regular_control_frequency' in cleaned_data and
             cleaned_data['regular_control_frequency'] not in (None, ''))):
            choices = []
            for choice in self.fields['regular_control_frequency'].choices:
                choices.append(choice[0])
            if cleaned_data['regular_control_frequency'] not in choices:
                if not cleaned_data['regular_control_frequency'].isdigit():
                    self.errors['regular_control_frequency'] = ErrorList(
                        [_('Geef een getal op.')])

        if (('blood_sample_frequency' in cleaned_data and
             cleaned_data['blood_sample_frequency'] not in (None, ''))):
            choices = []
            for choice in self.fields['blood_sample_frequency'].choices:
                choices.append(choice[0])
            if cleaned_data['blood_sample_frequency'] not in choices:
                if not cleaned_data['blood_sample_frequency'].isdigit():
                    self.errors['blood_sample_frequency'] = ErrorList(
                        [_('Geef een getal op.')])

        return cleaned_data

    class Meta(BaseProfileEditForm.Meta):
        exclude = BaseProfileEditForm.Meta.exclude
        fieldsets = (
            (None, {'fields': ('BSN',
                               'local_hospital_number',
                               'hospital', 'title',
                               'first_name', 'initials', 'prefix',
                               'last_name', 'gender',
                               'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'diagnose',)}),
            ('diagnose', {'fields': ('exclude_questionnaires', )}),
            (None, {'fields': ('current_practitioner',
                               'regular_control_frequency',
                               'blood_sample_frequency',
                               'always_clinic_visit')}),
        )

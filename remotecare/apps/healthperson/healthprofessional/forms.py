# -*- coding: utf-8 -*-
"""
This module provides all the forms necessary for the functionality
for an healthprofessional.

:subtitle:`Class definitions:`
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.healthperson.healthprofessional.models import HealthProfessional,\
    FUNCTION_CHOICES, SPECIALISM_CHOICES
from apps.healthperson.secretariat.models import Secretary
from core.forms import BaseForm, BaseModelForm
from apps.account.forms import BaseProfileEditForm,\
    BasePasswordProfileEditForm

PHOTO_CHOICES = (
    ('', ('---------')),
    ('yes', ('Ja')),
    ('no', ('Nee')),
    ('remove', ('Verwijder foto')),
)


class HealthProfessionalSearchForm(BaseForm):
    """
    Search for a healthprofessional by either
    first_name, last_name, function or specialism
    Only provides the form & fields, all logic is in the view.
    """
    first_name = forms.CharField(
        max_length=128,
        label=_('Voornaam'), required=False)
    last_name = forms.CharField(
        max_length=128,
        label=_('Achternaam'), required=False)
    function = forms.TypedChoiceField(label=_('Functie'), required=False)
    specialism = forms.TypedChoiceField(label=_('Specialisme'), required=False)

    def __init__(self, *args, **kwargs):
        super(HealthProfessionalSearchForm, self).__init__(*args, **kwargs)

        # Set function list
        function_choices = list(FUNCTION_CHOICES)
        function_choices.insert(0, ('', '---------'))
        self.fields['function'].choices = function_choices

        # Set specialism list
        specialism_choices = list(SPECIALISM_CHOICES)
        specialism_choices.insert(0, ('', '---------'))
        self.fields['specialism'].choices = specialism_choices


class HealthProfessionalPhotoForm(BaseModelForm):
    """
    Provides a form for adding/editing the photo, using
    an ImageField
    """
    class Meta:
        model = HealthProfessional
        exclude = ('health_person_id', 'function', 'specialism',
                   'telephone', 'urgent_control_notification',
                   'urgent_control_secretary', 'out_of_office_start',
                   'out_of_office_end', 'out_of_office_replacement', )
        fieldsets = (
            ('photo_location', {'fields': ('photo_location',)}),
        )


class HealthProfessionalOutOfOfficeEditForm(BaseModelForm):
    """
    Set the out-of-office information,
    this includes a period and an replacement
    healthprofessional during that period.
    """
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(HealthProfessionalOutOfOfficeEditForm,
              self).__init__(*args, **kwargs)

        # set health professionals choices
        healthprofessionals = []

        healthprofessional_list = HealthProfessional.objects.filter(
            user__hospital=instance.user.hospital)

        for healthprofessional in healthprofessional_list:
            if ((healthprofessional.health_person_id !=
                 instance.health_person_id)):
                healthprofessionals.append(
                    (healthprofessional.health_person_id,
                     healthprofessional.user.professional_name))

        healthprofessionals.insert(0, ('', '---------'))
        self.fields['out_of_office_replacement'].choices = healthprofessionals

    def clean(self):
        cleaned_data = super(HealthProfessionalOutOfOfficeEditForm,
                             self).clean()

        if (('out_of_office_start' in cleaned_data and
             'out_of_office_end' in cleaned_data)):
            if ((cleaned_data['out_of_office_start'] not in (None, '') and
                 cleaned_data['out_of_office_end'] not in (None, ''))):
                if ((cleaned_data['out_of_office_start'] >
                     cleaned_data['out_of_office_end'])):
                    self.errors['out_of_office_end'] =\
                        ('Eind datum is voor start datum')

        if (('out_of_office_start' in cleaned_data and
             cleaned_data['out_of_office_start'] not in (None, ''))):
            if (('out_of_office_end' not in cleaned_data or
                 cleaned_data['out_of_office_end'] in (None, ''))):
                self.errors['out_of_office_end'] = _('Dit veld is verplicht')
            if (('out_of_office_replacement' not in cleaned_data or
                 cleaned_data['out_of_office_replacement'] in (None, ''))):
                self.errors['out_of_office_replacement'] =\
                    _('Dit veld is verplicht')

        return cleaned_data

    class Meta:
        model = HealthProfessional
        exclude = ('health_person_id', 'photo_location', 'function',
                   'specialism', 'telephone', 'urgent_control_notification',
                   'urgent_control_secretary', )
        fieldsets = (
            (None, {'fields': ('out_of_office_start', 'out_of_office_end',
                    'out_of_office_replacement',)}),
        )


class HealthProfessionalNotificationEditForm(BaseModelForm):
    """
    Edit the notification of new messages/finished controls
    """
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(HealthProfessionalNotificationEditForm,
              self).__init__(*args, **kwargs)

        # set health professionals choices
        secretariat = []

        secretary_list = Secretary.objects.filter(
            user__hospital=instance.user.hospital)

        for secretary in secretary_list:
            secretariat.append(
                (secretary.health_person_id,
                 secretary.user.professional_name))

        secretariat.insert(0, ('', '---------'))
        self.fields['urgent_control_secretary'].choices = secretariat
        self.fields['urgent_control_notification'].widget.attrs.update(
            {'class': 'choice_display',
             'choices':
             '''[{'to_secretary': ['urgent_control_notification']}]'''})

    def clean(self):
        cleaned_data = super(HealthProfessionalNotificationEditForm,
                             self).clean()
        if 'urgent_control_notification' in cleaned_data:
            if cleaned_data['urgent_control_notification'] != 'to_secretary':
                if 'urgent_control_notification' in self.errors:
                    del self.errors['urgent_control_notification']
                if 'urgent_control_secretary' in cleaned_data:
                    del cleaned_data['urgent_control_secretary']
            else:
                if (('urgent_control_secretary' in cleaned_data and
                     cleaned_data['urgent_control_secretary'] in (None, ''))):
                    self.errors['urgent_control_secretary'] =\
                        ('Dit veld is verplicht')

        return cleaned_data

    class Meta:
        model = HealthProfessional
        exclude = ('user', 'photo_location', 'function', 'specialism',
                   'telephone', 'out_of_office_start', 'out_of_office_end',
                   'out_of_office_replacement', 'added_by')
        fieldsets = (
            (None, {'fields': ('urgent_control_notification',)}),
            ('urgent_control_notification',
             {'fields': ('urgent_control_secretary',)}),
        )


class HealthProfessionalEditForm(BasePasswordProfileEditForm):
    '''
    Edit healthprofessional information. Add specific healthprofessionals
    fields on top of the default User fields.
    '''
    function = forms.TypedChoiceField(label=_('Functie'), required=True)
    specialism = forms.TypedChoiceField(label=_('Specialisme'), required=True)
    telephone = forms.CharField(
        max_length=128, label=_('Tel.nr. contact polikliniek'), required=True)

    def __init__(self, *args, **kwargs):
        super(HealthProfessionalEditForm, self).__init__(*args, **kwargs)

        # Set function list
        function_choices = list(FUNCTION_CHOICES)
        function_choices.insert(0, ('', '---------'))
        self.fields['function'].choices = function_choices

        # Set specialism list
        specialism_choices = list(SPECIALISM_CHOICES)
        specialism_choices.insert(0, ('', '---------'))
        self.fields['specialism'].choices = specialism_choices

        if self.instance:
            self.fields['function'].initial =\
                self.instance.healthperson.function
            self.fields['specialism'].initial =\
                self.instance.healthperson.specialism
            self.fields['telephone'].initial =\
                self.instance.healthperson.telephone

        # Minimal age is 16, so remove the last 16 year choices..
        self.fields['date_of_birth'].years =\
            self.fields['date_of_birth'].years[:-16]
        self.fields['date_of_birth'].widget.years =\
            self.fields['date_of_birth'].years

    class Meta(BasePasswordProfileEditForm.Meta):
        exclude = BasePasswordProfileEditForm.Meta.exclude + (
            'BSN', 'local_hospital_number',
            'hospital',)
        fieldsets = (
            (None, {'fields': ('title', 'first_name',
                               'initials', 'last_name',
                               'prefix', 'gender',
                               'date_of_birth',)}),
            (None, {'fields': ('mobile_number',
                               'mobile_number2', 'email',
                               'email2',)}),
            (None, {'fields': ('function', 'specialism', 'telephone',
                               'change_password',)}),
            ('change_password', {'fields': ('password', 'password2',)}),
        )


class HealthProfessionalAddForm(BaseProfileEditForm):
    '''
    Add healthprofessional information. Add specific healthprofessionals
    fields on top of the default User fields.
    '''
    function = forms.TypedChoiceField(
        label=_('Functie'),
        required=True)
    specialism = forms.TypedChoiceField(
        label=_('Specialisme'),
        required=True)
    telephone = forms.CharField(
        max_length=128,
        label=_('Tel.nr. contact polikliniek'),
        required=True)

    def __init__(self, *args, **kwargs):
        super(HealthProfessionalAddForm, self).__init__(*args, **kwargs)

        # Set function list
        function_choices = list(FUNCTION_CHOICES)
        function_choices.insert(0, ('', '---------'))
        self.fields['function'].choices = function_choices

        # Set specialism list
        specialism_choices = list(SPECIALISM_CHOICES)
        specialism_choices.insert(0, ('', '---------'))
        self.fields['specialism'].choices = specialism_choices

        # Minimal age is 16, so remove the last 16 year choices..
        self.fields['date_of_birth'].years =\
            self.fields['date_of_birth'].years[:-16]
        self.fields['date_of_birth'].widget.years =\
            self.fields['date_of_birth'].years

    class Meta(BaseProfileEditForm.Meta):
        exclude = BaseProfileEditForm.Meta.exclude
        fieldsets = (
            (None, {'fields': ('title', 'first_name', 'initials',
                               'last_name', 'prefix', 'gender',
                               'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'function', 'specialism',
                               'telephone')}),
        )

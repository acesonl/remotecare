# -*- coding: utf-8 -*-
"""
This module contains the forms for profile editing by a secretary and
als for the manager to search for a secretary.

:subtitle:`Class definitions:`
"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.account.forms import BaseProfileEditForm, BasePasswordProfileEditForm
from apps.healthperson.healthprofessional.models import SPECIALISM_CHOICES
from core.forms import BaseForm


class SecretarySearchForm(BaseForm):
    '''
    Search for a secretary by last_name or specialism, used
    by a manager.
    '''
    last_name = forms.CharField(
        max_length=128, label=_('Achternaam'), required=False)
    specialism = forms.TypedChoiceField(
        label=_('Specialisme'), required=False)

    def __init__(self, *args, **kwargs):
        super(SecretarySearchForm, self).__init__(*args, **kwargs)

        # Set specialism list
        specialism_choices = list(SPECIALISM_CHOICES)
        specialism_choices.insert(0, ('', '---------'))
        self.fields['specialism'].choices = specialism_choices


class SecretaryEditForm(BasePasswordProfileEditForm):
    '''
    Edit secretary profile/personalia form
    '''
    specialism = forms.TypedChoiceField(label=_('Specialisme'), required=True)

    def __init__(self, *args, **kwargs):
        super(SecretaryEditForm, self).__init__(*args, **kwargs)

        # Set specialism list
        specialism_choices = list(SPECIALISM_CHOICES)
        specialism_choices.insert(0, ('', '---------'))
        self.fields['specialism'].choices = specialism_choices

        if self.instance:
            self.fields['specialism'].initial =\
                self.instance.healthperson.specialism

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
                               'prefix', 'gender', 'date_of_birth',)}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2')}),
            (None, {'fields': ('specialism', 'change_password')}),
            ('change_password', {'fields': ('password', 'password2')}),
        )


class SecretaryAddForm(BaseProfileEditForm):
    '''
    Add new secretary form
    '''
    specialism = forms.TypedChoiceField(label=_('Specialisme'), required=True)

    def __init__(self, *args, **kwargs):
        super(SecretaryAddForm, self).__init__(*args, **kwargs)

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
                               'last_name',
                               'prefix', 'gender', 'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'specialism')}),
        )

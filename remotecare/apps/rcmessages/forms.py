# -*- coding: utf-8 -*-
"""
This module contains the forms for messages.

:subtitle:`Class definitions:`
"""
from django import forms
from apps.rcmessages.models import RCMessage
from django.utils.translation import ugettext_lazy as _
from core.forms import BaseForm, BaseModelForm


class MessageAddForm(BaseModelForm):
    '''
    Form for adding a new message
    '''
    def __init__(self, *args, **kwargs):
        super(MessageAddForm, self).__init__(*args, **kwargs)

        self.fields['internal_message'].widget.attrs.update(
            {'class': 'ckeditor'})
        self.fields['subject'].widget.attrs.update(
            {'class': 'subject_field'})

    class Meta:
        model = RCMessage
        exclude = ('read_on', 'added_on', 'patient',
                   'healthprofessional', 'secretary', 'related_to')


class MessageSearchForm(BaseForm):
    '''
    Healthprofessional can search his/hers sent messages
    based on the BSN or/and last_name of the patient
    '''
    BSN = forms.CharField(
        max_length=128,
        label=_('BSN'),
        required=False)
    last_name = forms.CharField(
        max_length=128,
        label=_('Achternaam'),
        required=False)

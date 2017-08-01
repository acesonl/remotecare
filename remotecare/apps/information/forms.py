# -*- coding: utf-8 -*-
"""
Provides a feedback form

:subtitle:`Class definitions:`
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from core.forms import BaseForm


class FeedBackAddEditForm(BaseForm):
    '''
    Form for adding Feedback
    '''
    feedback = forms.CharField(
        label=_('Feedback'),
        widget=forms.Textarea)

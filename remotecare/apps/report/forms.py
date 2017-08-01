# -*- coding: utf-8 -*-
"""
Module providing the forms for adding a report & message during handling
a filled-in control by an healthprofessional.

:subtitle:`Class definitions:`
"""
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.report.models import Report
from apps.rcmessages.models import RCMessage
from core.forms import BaseModelForm


# Items that need to be filled in
report_black_list = ('--Vul aanvullend onderzoek in--',
                     '--Vul conclusie in--',
                     '--Vul beleid in-',
                     '--Vul crp waarde in--',
                     '--Vul CRP waarde in--',
                     '--Vul fecaal calprotectine in--',
                     '--Vul reactie hier in--')


class MessageAddEditForm(BaseModelForm):
    '''
    Add/Edit a message for a patient
    (as part of the report function)
    '''
    def __init__(self, *args, **kwargs):
        kwargs.pop('finishquestionnare', None)
        super(MessageAddEditForm, self).__init__(*args, **kwargs)

        self.fields['internal_message'].widget.attrs.update(
            {'class': 'ckeditor'})

    class Meta:
        model = RCMessage
        fields = ['internal_message']

    def clean(self):
        cleaned_data = super(MessageAddEditForm, self).clean()

        if 'internal_message' in cleaned_data:
            for entry in report_black_list:
                if entry in cleaned_data['internal_message']:
                    self.errors['internal_message'] = ErrorList(
                        [_('"' + entry + '" is niet ingevuld.')])
                    break

        return cleaned_data


class UrgentReportAddEditForm(BaseModelForm):
    '''
    Add edit an urgent report, checks that items that
    are included in the template as placeholder are removed.
    '''
    def __init__(self, *args, **kwargs):
        super(UrgentReportAddEditForm, self).__init__(*args, **kwargs)
        self.fields['report'].widget.attrs.update({'class': 'ckeditor'})
        self.fields['report'].help_text = ''

    def clean(self):
        cleaned_data = super(UrgentReportAddEditForm, self).clean()

        if 'report' in cleaned_data:
            for entry in report_black_list:
                if entry in cleaned_data['report']:
                    self.errors['report'] = ErrorList(
                        [_('"' + entry + '" is niet ingevuld.')])
                    break

        return cleaned_data

    class Meta:
        model = Report
        fields = ['report']


class ReportAddEditForm(BaseModelForm):
    '''
    Add/Edit an normal report. Is merely the same as the urgent
    one but needs some extra initialization.
    '''
    def __init__(self, *args, **kwargs):
        kwargs.pop('post', None)
        finishquestionnare = kwargs.pop('finishquestionnare', None)
        super(ReportAddEditForm, self).__init__(*args, **kwargs)

        do_delete = True

        if finishquestionnare:
            if finishquestionnare.appointment == 'no':
                do_delete = False

        if do_delete:
            del self.fields['patient_needs_appointment']

        self.fields['report'].widget.attrs.update({'class': 'ckeditor'})

    def clean(self):
        cleaned_data = super(ReportAddEditForm, self).clean()

        if 'report' in cleaned_data:
            for entry in report_black_list:
                if entry in cleaned_data['report']:
                    self.errors['report'] = ErrorList(
                        [_('"' + entry + '" is niet ingevuld.')])
                    break

        return cleaned_data

    class Meta:
        model = Report
        fields = ['sent_to_doctor', 'patient_needs_appointment', 'report']

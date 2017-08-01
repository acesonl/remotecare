# -*- coding: utf-8 -*-
"""
This module contains all the default questionnaire forms

See the forms.py in the questionnaire app for documentation on
how to manage the forms.

:subtitle:`Class definitions:`
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.questionnaire.forms import create_exclude_list,\
    BaseQuestionnaireForm
from apps.questionnaire.default.models import StartUrgentQuestionnaire,\
    UrgentProblemQuestionnaire, StartQuestionnaire,\
    FinishQuestionnaire
from core.forms import DisplayWidget


class StartUrgentQuestionnaireForm(BaseQuestionnaireForm):
    '''
    StartUrgentQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/UrgentStartQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = StartUrgentQuestionnaire

        fieldsets = (
            (None, {'fields': ('appointment_period',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class UrgentProblemQuestionnaireForm(BaseQuestionnaireForm):

    '''
    UrgentProblemQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(UrgentProblemQuestionnaireForm, self).__init__(*args, **kwargs)

        # Set different renderer (picked up in the fieldset template)
        self.fields['problem_severity'].listscore_render = True
        self.fields['problems'].widget.attrs.update({'rows': 8})

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = UrgentProblemQuestionnaire

        fieldsets = (
            (None, {'fields': ('problems', 'problem_severity',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class StartQuestionnaireForm(BaseQuestionnaireForm):

    '''
    StartQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(StartQuestionnaireForm, self).__init__(*args, **kwargs)
        self.fields['problems'].widget.attrs.update({'rows': 8})

        self.include_blood_taken_questions = False

        if self.patient:
            self.include_blood_taken_questions =\
                self.patient.include_blood_taken_questions

        if self.include_blood_taken_questions:
            self.fields['current_status'].help_text = _(
                'Let op: voor deze controle moet u bloed laten prikken,' +
                ' voordat u de vragenlijst kan invullen en versturen!')

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = StartQuestionnaire

        fieldsets = (
            ('current_status', {'fields': ('current_status',)}),
            (None, {'fields': ('problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class StartQuestionnaireForm1(BaseQuestionnaireForm):

    '''
    StartQuestionnaireForm1
    '''
    form_nr = 1
    form_template = 'questionnaire/forms/StartQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(StartQuestionnaireForm1, self).__init__(*args, **kwargs)
        self.fields['problem_severity'].listscore_render = True

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = StartQuestionnaire

        fieldsets = (
            (None, {'fields': ('problem_severity', 'hospital_visit',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class FinishQuestionnaireForm(BaseQuestionnaireForm):

    '''
    FinishQuestionnaireForm
    '''

    date_unknown = forms.BooleanField(required=False, label=_('Weet ik niet'))
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 0

    def __init__(self, *args, **kwargs):
        super(FinishQuestionnaireForm, self).__init__(*args, **kwargs)

        self.fields['appointment_period'].required = True
        self.fields['appointment_preference'].required = True
        self.fields['appointment'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes_phone_nurse': ['appointment'],
             'yes_phone_doctor': ['appointment'],
             'yes_nurse': ['appointment'],
             'yes_doctor': ['appointment'] }]'''})
        if self.patient:
            # Remove 'no' from the options if the appointment is mandatory..
            if self.patient.always_appointment:
                choices = list(self.fields['appointment'].choices)

                # remove the first 3 choices from the list
                del choices[0]
                del choices[0]
                del choices[0]

                self.fields['appointment'].choices = choices
                self.fields['appointment'].label = _(
                    'Elke digitale controle dient te worden gevolgd door' +
                    ' een controle op de polikliniek, geef hieronder' +
                    ' uw voorkeur op.')

    def clean(self):
        cleaned_data = super(FinishQuestionnaireForm, self).clean()

        if 'appointment' in cleaned_data:
            if cleaned_data['appointment'] == 'no':
                if 'appointment_period' in self.errors:
                    del self.errors['appointment_period']
                if 'appointment_preference' in self.errors:
                    del self.errors['appointment_preference']
                if 'appointment_period' in cleaned_data:
                    del cleaned_data['appointment_period']

        del cleaned_data['date_unknown']

        return cleaned_data

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = FinishQuestionnaire

        fieldsets = (
            (None, {
                'fields': (
                    'appointment',)}),
            ('appointment', {
                'fields': (
                    'appointment_period',
                    'appointment_preference')}), )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class FinishQuestionnaireForm1(BaseQuestionnaireForm):

    '''
    FinishQuestionnaireForm1
    '''
    date_unknown = forms.BooleanField(required=False, label=_('Weet ik niet'))
    form_template = 'questionnaire/forms/FinishQuestionnaireForm1.html'
    form_nr = 1
    date_display = forms.CharField(
        widget=DisplayWidget,
        label=_('Bloedprikken nog niet nodig.'))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', None)

        # check if
        super(FinishQuestionnaireForm1, self).__init__(*args, **kwargs)
        if self.patient:
            self.include_blood_taken_questions =\
                self.patient.include_blood_taken_questions

            if self.include_blood_taken_questions:
                del self.fields['date_display']
                self.fields['blood_sample_date'].required = True

                if initial:
                    if 'blood_sample_date' in initial and not initial[
                            'blood_sample_date']:
                        self.fields['date_unknown'].widget.attrs.update(
                            {'checked': 'checked'})
            else:
                del self.fields['blood_sample_date']
                del self.fields['date_unknown']
                del self.fields['blood_sample']

                if self.patient.last_blood_taken_date:
                    to_display = 'Laatste keer bloed geprikt op: ' +\
                        self.patient.last_blood_taken_date.strftime(
                            "%d. %b %Y") +\
                        '. De frequentie is: ' +\
                        self.patient.blood_taken_freq_display
                else:
                    to_display = ''
                self.fields['date_display'].initial = to_display
                self.fields['date_display'].required = False

        # print self.fields['blood_sample'].__dict__

    def clean(self):
        cleaned_data = super(FinishQuestionnaireForm1, self).clean()

        # print 'in_form', self.errors

        if self.include_blood_taken_questions:
            if 'blood_sample_date' not in cleaned_data and cleaned_data[
                    'date_unknown']:
                del self.errors['blood_sample_date']

            if (('date_unknown' in cleaned_data and
                 not cleaned_data['date_unknown'] in
                 ('', False, None))):
                cleaned_data['blood_sample_date'] = None
                del cleaned_data['date_unknown']

            # Copy error
            if 'blood_sample_date' in self.errors:
                self.errors['date_unknown'] = self.errors['blood_sample_date']

        else:
            if 'blood_sample_date' in self.errors:
                del self.errors['blood_sample_date']

            if 'blood_sample' in self.errors:
                del self.errors['blood_sample']

        if 'date_unknown' in cleaned_data:
            del cleaned_data['date_unknown']

        if 'date_display' in cleaned_data:
            del cleaned_data['date_display']

        return cleaned_data

    class Meta:
        # from apps.questionnaire.models import FinishQuestionaire
        model = FinishQuestionnaire
        fields = (
            'blood_sample',
            'blood_sample_date',
            'date_unknown',
            'date_display')

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        # exclude = create_exclude_list(model, fieldsets)

# -*- coding: utf-8 -*-
"""
This module contains all the forms for the inflammatory bowel disease (IBD)
questionnaires.

See the forms.py in the questionnaire app for documentation on
how to manage the forms.

:subtitle:`Class definitions:`
"""
from apps.questionnaire.forms import create_exclude_list,\
    BaseQuestionnaireForm
from apps.questionnaire.ibd.models import IBDQuestionnaire
from django.utils.translation import ugettext_lazy as _


class IDBQuestionnaireForm(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 0

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm, self).__init__(*args, **kwargs)
        self.fields['has_stoma'].required = True
        self.fields['has_pouch'].required = True
        self.fields['has_pouch_problems'].required = True

        self.fields['has_pouch'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['has_pouch']}]'''})
        self.fields['has_pouch_problems'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['has_pouch_problems']}]'''})
        self.fields['pouch_problems'].widget.attrs.update({'rows': 4})

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm, self).clean()

        if 'has_pouch' in cleaned_data and cleaned_data['has_pouch'] != 'yes':
            if 'has_pouch_problems' in self.errors:
                del self.errors['has_pouch_problems']
            if 'has_pouch_problems' in cleaned_data:
                del cleaned_data['has_pouch_problems']
            if 'pouch_problems' in cleaned_data:
                del cleaned_data['pouch_problems']

        return cleaned_data

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('has_stoma', 'has_pouch',)}),
            ('has_pouch', {'fields': ('has_pouch_problems',)}),
            ('has_pouch_problems', {'fields': ('pouch_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


# has_stoma = no
class IDBQuestionnaireForm2A(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm2A
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 2

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm2A, self).__init__(*args, **kwargs)
        self.fields['stool_freq'].required = True
        self.fields['stool_thickness'].required = True
        self.fields['diarrhea_at_night'].required = True
        self.fields['stool_has_blood'].required = True
        self.fields['stool_has_slime'].required = True
        self.fields['stool_liquid_freq'].required = True
        self.fields['stool_thickness'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'liquid': ['stool_thickness']}]'''})

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm2A, self).clean()

        if 'stool_thickness' in cleaned_data and cleaned_data[
                'stool_thickness'] != 'liquid':
            if 'stool_liquid_freq' in self.errors:
                del self.errors['stool_liquid_freq']
            if 'stool_liquid_freq' in cleaned_data:
                del cleaned_data['stool_liquid_freq']
        return cleaned_data

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            IDBQuestionnaireForm)
        if cleaned_data:
            if 'has_stoma' in cleaned_data:
                if cleaned_data['has_stoma'] == 'yes':
                    return False
        return True

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {
                'fields': (
                    'stool_freq',
                    'stool_thickness',)}),
            ('stool_thickness', {
                'fields': (
                    'stool_liquid_freq',)}),
            (None, {
                'fields': (
                    'diarrhea_at_night',
                    'stool_has_blood',
                    'stool_has_slime',)}), )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


# has_stoma = no
class IDBQuestionnaireForm3A(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm3A
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 3

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm3A, self).__init__(*args, **kwargs)
        self.fields['stool_urgency'].required = True
        self.fields['stool_planning'].required = True
        self.fields['stool_continence'].required = True

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            IDBQuestionnaireForm)
        if cleaned_data:
            if 'has_stoma' in cleaned_data:
                if cleaned_data['has_stoma'] == 'yes':
                    return False
        return True

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': (
                'stool_urgency', 'stool_planning', 'stool_continence',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


# has_stoma = yes
class IDBQuestionnaireForm2B(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm2B
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 2

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm2B, self).__init__(*args, **kwargs)
        self.fields['stoma_version'].required = True
        self.fields['stoma_empty_freq'].required = True
        self.fields['stoma_has_problems'].required = True

        self.fields['stoma_has_problems'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['stoma_has_problems']}]'''})

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            IDBQuestionnaireForm)
        if cleaned_data:
            if 'has_stoma' in cleaned_data:
                if cleaned_data['has_stoma'] == 'yes':
                    return True
        return False

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm2B, self).clean()

        if 'stoma_empty_freq' in cleaned_data:
            if cleaned_data['stoma_empty_freq'] > 1000:
                self.errors['stoma_empty_freq'] = _(
                    'Geef een getal kleiner dan 1000 op')
        return cleaned_data

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('stoma_version',
                               'stoma_empty_freq', 'stoma_has_problems',)}),
            ('stoma_has_problems', {'fields': ('stoma_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm4(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm4
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 4

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super(IDBQuestionnaireForm4, self).__init__(*args, **kwargs)
        self.fields['nausea_vomit'].required = True
        self.fields['nausea_vomit_time'].required = True
        self.queryset_speed_up()

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm4, self).clean()

        if 'nausea_vomit' in cleaned_data and cleaned_data[
                'nausea_vomit'] != 'yes':
            if 'nausea_vomit_time' in self.errors:
                del self.errors['nausea_vomit_time']
            if 'nausea_vomit_time' in cleaned_data:
                del cleaned_data['nausea_vomit_time']
        return cleaned_data

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('nausea_vomit',)}),
            ('nausea_vomit', {'fields': ('nausea_vomit_time',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm5(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm5
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 5

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self.instance = instance
        super(IDBQuestionnaireForm5, self).__init__(*args, **kwargs)
        self.fields['has_fistel'].required = True
        self.fields['anal_pain'].required = True
        self.fields['anal_problems'].required = True
        self.fields['has_fistel'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['has_fistel']}]'''})
        self.fields['fistel_location'].widget.attrs.update({'rows': 4})

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('has_fistel',)}),
            ('has_fistel', {'fields': ('fistel_location',)}),
            (None, {'fields': ('anal_pain', 'anal_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm6(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm6
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 6

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm6, self).__init__(*args, **kwargs)
        self.fields['appetite'].required = True
        self.fields['patient_weight'].required = True
        self.fields['patient_length'].required = True

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm6, self).clean()

        if 'patient_weight' in cleaned_data:
            if cleaned_data['patient_weight'] > 300:
                self.errors['patient_weight'] = _(
                    'Geef een gewicht kleiner dan 300kg op')
            if cleaned_data['patient_weight'] < 0.3:
                self.errors['patient_weight'] = _(
                    'Geef een gewicht groter dan 0.3kg op')

        if 'patient_length' in cleaned_data:
            if cleaned_data['patient_length'] > 280:
                self.errors['patient_length'] = _(
                    'Geef een lengte kleiner dan 280cm op')
            if cleaned_data['patient_length'] < 15:
                self.errors['patient_length'] = _(
                    'Geef een lengte groter dan 15cm op')

        return cleaned_data

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {
                'fields': (
                    'appetite', 'patient_weight',
                    'patient_length', 'stomach_ache',)}), )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm7(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm7
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 7

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm7, self).__init__(*args, **kwargs)
        self.fields['fatigue'].required = True
        self.fields['fever'].required = True

        self.fields['fever'].widget.attrs.update(
            {'class': 'choice_display', 'choices': '''[{'yes': ['fever']}]'''})
        self.fields['fever_specify'].widget.attrs.update({'rows': 4})

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('fatigue', 'fever',)}),
            ('fever', {'fields': ('fever_specify',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm8(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm8
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 8

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm8, self).__init__(*args, **kwargs)
        self.fields['joint_pain'].required = True

        self.fields['joint_pain'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['joint_pain']}]'''})

        self.fields['joint_pain_complaints'].widget.attrs.update({'rows': 4})

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('joint_pain',)}),
            ('joint_pain', {'fields': ('joint_pain_complaints',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm9(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm9
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 9

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm9, self).__init__(*args, **kwargs)
        self.fields['eye_inflammation'].required = True
        self.fields['skin_disorder'].required = True

        self.fields['eye_inflammation'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['eye_inflammation']}]'''})
        self.fields['skin_disorder'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['skin_disorder']}]'''})

        self.fields['eye_inflammation_complaints'].widget.attrs.update(
            {'rows': 4})
        self.fields['skin_disorder_complaints'].widget.attrs.update(
            {'rows': 4})

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('eye_inflammation',)}),
            ('eye_inflammation', {'fields': ('eye_inflammation_complaints',)}),
            (None, {'fields': ('skin_disorder',)}),
            ('skin_disorder', {'fields': ('skin_disorder_complaints',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class IDBQuestionnaireForm10(BaseQuestionnaireForm):

    '''
    IBDQuestionnaireForm10
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 10

    def __init__(self, *args, **kwargs):
        super(IDBQuestionnaireForm10, self).__init__(*args, **kwargs)
        self.fields['does_smoke'].required = True
        self.fields['smoke_freq'].required = True

        self.fields['does_smoke'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['does_smoke']}]'''})

    def clean(self):
        cleaned_data = super(IDBQuestionnaireForm10, self).clean()

        if 'does_smoke' in cleaned_data:
            if cleaned_data['does_smoke'] != 'yes':
                if 'smoke_freq' in self.errors:
                    del self.errors['smoke_freq']
                if 'smoke_freq' in cleaned_data:
                    del cleaned_data['smoke_freq']
            else:
                if 'smoke_freq' in cleaned_data:
                    if cleaned_data['smoke_freq'] > 1000:
                        self.errors['smoke_freq'] = _(
                            'Geef een getal kleiner dan 1000 op')

        return cleaned_data

    class Meta:
        model = IBDQuestionnaire

        fieldsets = (
            (None, {'fields': ('does_smoke',)}),
            ('does_smoke', {'fields': ('smoke_freq',)}),
            (None, {'fields': ('question_remarks',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)

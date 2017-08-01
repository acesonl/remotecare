# -*- coding: utf-8 -*-
"""
This module contains all the forms for the quality of life (QOL)
questionnaires.

See the forms.py in the questionnaire app for documentation on
how to manage the forms.

:subtitle:`Class definitions:`
"""
from apps.questionnaire.forms import create_exclude_list,\
    BaseQuestionnaireForm
from apps.questionnaire.qol.models import QOLQuestionnaire,\
    QOLChronCUQuestionnaire


class QOLChronCUQuestionnaireForm(BaseQuestionnaireForm):

    '''
    QOLChronCUQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/QOLChronCUForm0.html'

    class Meta:
        model = QOLChronCUQuestionnaire
        fieldsets = (None, {'fields': ()}),
        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLChronCUQuestionnaireForm1(BaseQuestionnaireForm):
    '''
    QOLChronCUQuestionnaireForm
    '''
    form_nr = 1
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLChronCUQuestionnaireForm1, self).__init__(*args, **kwargs)
        self.fields['hasproblems'].vertical_render = True
        self.fields['hasproblems'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['hasproblems'] }]'''})
        self.fields['practical_problems'].double_column = True
        self.queryset_speed_up()

    class Meta:
        model = QOLChronCUQuestionnaire

        fieldsets = (
            (None, {'fields': ('hasproblems',)}),
            ('hasproblems', {'fields': ('practical_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLChronCUQuestionnaireForm2(BaseQuestionnaireForm):

    '''
    QOLChronCUQuestionnaireForm2
    '''
    form_nr = 2
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLChronCUQuestionnaireForm2, self).__init__(*args, **kwargs)
        self.fields['social_problems'].double_column = True
        self.fields['emotional_problems'].double_column = True
        self.queryset_speed_up()

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLChronCUQuestionnaireForm1)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLChronCUQuestionnaire

        fieldsets = (
            ('None', {'fields': ('social_problems', 'emotional_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLChronCUQuestionnaireForm3(BaseQuestionnaireForm):

    '''
    QOLChronCUQuestionnaireForm3
    '''
    form_nr = 3
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLChronCUQuestionnaireForm3, self).__init__(*args, **kwargs)
        self.fields['spiritual_problems'].double_column = True
        self.queryset_speed_up()

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLChronCUQuestionnaireForm1)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLChronCUQuestionnaire

        fieldsets = (
            ('None', {'fields': ('spiritual_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLChronCUQuestionnaireForm4(BaseQuestionnaireForm):

    '''
    QOLChronCUQuestionnaireForm4
    '''
    form_nr = 4
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLChronCUQuestionnaireForm4, self).__init__(*args, **kwargs)
        self.fields['other_problems'].widget.attrs.update({'rows': 8})
        self.fields['need_contact'].required = True

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLChronCUQuestionnaireForm1)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLChronCUQuestionnaire

        fieldsets = (
            ('None', {'fields': ('other_problems', 'need_contact',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLQuestionnaireForm(BaseQuestionnaireForm):

    '''
    QOLQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLQuestionnaireForm, self).__init__(*args, **kwargs)
        self.fields['hasproblems'].vertical_render = True
        self.fields['hasproblems'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['hasproblems'] }]'''})
        self.fields['practical_problems'].double_column = True
        self.queryset_speed_up()

    class Meta:
        model = QOLQuestionnaire

        fieldsets = (
            (None, {'fields': ('hasproblems',)}),
            ('hasproblems', {'fields': ('practical_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLQuestionnaireForm1(BaseQuestionnaireForm):

    '''
    QOLQuestionnaireForm1
    '''
    form_nr = 1
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLQuestionnaireForm1, self).__init__(*args, **kwargs)
        self.fields['social_problems'].double_column = True
        self.fields['emotional_problems'].double_column = True
        self.queryset_speed_up()

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLQuestionnaireForm)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLQuestionnaire

        fieldsets = (
            ('None', {'fields': ('social_problems', 'emotional_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLQuestionnaireForm2(BaseQuestionnaireForm):

    '''
    QOLQuestionnaireForm2
    '''
    form_nr = 2
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLQuestionnaireForm2, self).__init__(*args, **kwargs)
        self.fields['spiritual_problems'].double_column = True
        self.fields['fysical_problems'].triple_column = True
        self.queryset_speed_up()

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLQuestionnaireForm)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLQuestionnaire

        fieldsets = (
            ('None', {'fields': ('spiritual_problems', 'fysical_problems',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOLQuestionnaireForm3(BaseQuestionnaireForm):

    '''
    QOLQuestionnaireForm3
    '''
    form_nr = 3
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    def __init__(self, *args, **kwargs):
        super(QOLQuestionnaireForm3, self).__init__(*args, **kwargs)
        self.fields['other_problems'].widget.attrs.update({'rows': 8})
        self.fields['need_contact'].required = True

    def condition(self, wizard):
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOLQuestionnaireForm)
        if cleaned_data:
            if 'hasproblems' in cleaned_data:
                if cleaned_data['hasproblems'] == 'no':
                    return False
        return True

    class Meta:
        model = QOLQuestionnaire

        fieldsets = (
            ('None', {'fields': ('other_problems', 'need_contact',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)

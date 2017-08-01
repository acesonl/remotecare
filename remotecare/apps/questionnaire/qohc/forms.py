# -*- coding: utf-8 -*-
"""
This module contains all the forms for the quality of healthcare (QOHC)
questionnaires.

See the forms.py in the questionnaire app for documentation on
how to manage the forms.

:subtitle:`Class definitions:`
"""
from apps.questionnaire.forms import create_exclude_list,\
    BaseQuestionnaireForm
from apps.questionnaire.qohc.models import QOHCQuestionnaire


class QOHCQuestionnaireForm(BaseQuestionnaireForm):

    '''
    QOHCQuestionnaireForm
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 0

    def __init__(self, *args, **kwargs):
        super(QOHCQuestionnaireForm, self).__init__(*args, **kwargs)

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = QOHCQuestionnaire

        fieldsets = (
            (None, {'fields': ('not_fill_in',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class QOHCQuestionnaireForm1(BaseQuestionnaireForm):

    '''
    QOHCQuestionnaireForm
    '''
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'
    form_nr = 1

    def __init__(self, *args, **kwargs):
        super(QOHCQuestionnaireForm1, self).__init__(*args, **kwargs)

        # Set different renderer (picked up in the fieldset template)
        self.fields['hc_satisfaction_score'].listscore_render = True
        self.fields['rc_satisfation_score'].listscore_render = True

    def condition(self, wizard):
        # return the name of the form to do the test_condition on
        cleaned_data = wizard.get_cleaned_data_for_form_class(
            QOHCQuestionnaireForm)
        if cleaned_data:
            if 'not_fill_in' in cleaned_data:
                if cleaned_data['not_fill_in'] == 'no':
                    return False
        return True

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = QOHCQuestionnaire

        fieldsets = ((None,
                      {'fields': ('hc_satisfaction_score',
                                  'serious_score',
                                  'friendly_score',
                                  'information_score',
                                  'rc_satisfation_score')}),
                     )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)

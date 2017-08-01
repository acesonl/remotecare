# -*- coding: utf-8 -*-
"""
This module contains all the forms for the rheumatism
questionnaires.

See the forms.py in the questionnaire app for documentation on
how to manage the forms.

:subtitle:`Class definitions:`
"""
from apps.questionnaire.forms import create_exclude_list,\
    BaseQuestionnaireForm
from apps.questionnaire.rheumatism.models import RheumatismSF36,\
    RADAIQuestionnaire


class RheumatismSF36Form(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form
    '''
    form_nr = 0
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        # Make sure to use a , after a list with a single element else it will
        # be seen as a string.
        fieldsets = ((None,
                      {'fields': ('health_general',
                                  'health_changes',
                                  'high_effort_impact',
                                  'poor_effort_impact',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form1(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form1
    '''
    form_nr = 1
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        # Make sure to use a , after a list with a single element else it will
        # be seen as a string.
        fieldsets = ((None,
                      {'fields': ('carrying_impact',
                                  'walking_stairs_impact',
                                  'walking_one_stair_impact',
                                  'bent_over_impact',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form2(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form2
    '''
    form_nr = 2
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        # Make sure to use a , after a list with a single element else it will
        # be seen as a string.
        fieldsets = ((None,
                      {'fields': ('walk_km_impact',
                                  'walk_halfkm_impact',
                                  'walk_tenthkm_impact',
                                  'wash_cloth_impact',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form3(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form3
    '''
    form_nr = 3
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (('Combined',
                      {'fields': ('work_less_problem',
                                  'achieve_problem',
                                  'work_limitation_problem',
                                  'work_effort_problem',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form4(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form4
    '''
    form_nr = 4
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (('Combined',
                      {'fields': ('work_less_emotional_problem',
                                  'achieve_emotional_problem',
                                  'accurate_emotional_problem',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form5(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form5
    '''
    form_nr = 5
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (
            ('None', {
                'fields': (
                    'social_impact', 'pain_score', 'pain_impact',)}), )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form6(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form6
    '''
    form_nr = 6
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (('Combined',
                      {'fields': ('cheerful_score',
                                  'nervious_score',
                                  'blues_score',
                                  'calm_score',
                                  'energetic_score',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form7(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form7
    '''
    form_nr = 7
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (
            ('Combined', {
                'fields': (
                    'depressed_score',
                    'burnout_score',
                    'happiness_score',
                    'tired_score',)}), )

        # auto create exclude based on fieldsets
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form8(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form8
    '''
    form_nr = 8
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (
            (None, {
                'fields': (
                    'social_visit_impact',
                    'easier_ill_score',
                    'even_healthy_score',)}), )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class RheumatismSF36Form9(BaseQuestionnaireForm):

    '''
    RheumatismSF36Form9
    '''
    form_nr = 9
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RheumatismSF36

        fieldsets = (
            (None, {'fields': ('health_drop_score',
                               'excellent_health_score',)}),
        )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class RADAIQuestionnaireForm(BaseQuestionnaireForm):

    '''
     RADAIQuestionnaireForm
    '''
    form_nr = 0
    form_template = 'questionnaire/DefaultQuestionnaireForm.html'

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RADAIQuestionnaire

        fieldsets = ((None,
                      {'fields': ('activity_six_month_score',
                                  'activity_today_score',
                                  'pain_today_score',
                                  'stiffness_today_score')}),
                     )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class RADAIQuestionnaireForm1(BaseQuestionnaireForm):

    '''
     RADAIQuestionnaireForm1
    '''
    form_nr = 1
    form_template = 'questionnaire/forms/RADAIQuestionnaireForm1.html'
    # form_template='questionnaire/Radaiform2.html'

    field_nrs = {
        'right_shoulder_pain_score': 1,
        'right_elbow_pain_score': 3,
        'right_wrist_pain_score': 5,
        'right_vingers_pain_score': 7,
        'left_shoulder_pain_score': 2,
        'left_elbow_pain_score': 4,
        'left_wrist_pain_score': 6,
        'left_vingers_pain_score': 8}

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RADAIQuestionnaire

        fieldsets = (('patient_image_right',
                      {'fields': ('right_shoulder_pain_score',
                                  'right_elbow_pain_score',
                                  'right_wrist_pain_score',
                                  'right_vingers_pain_score',
                                  )}),
                     ('patient_image_left',
                      {'fields': ('left_shoulder_pain_score',
                                  'left_elbow_pain_score',
                                  'left_wrist_pain_score',
                                  'left_vingers_pain_score',
                                  )}),
                     )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)


class RADAIQuestionnaireForm2(BaseQuestionnaireForm):

    '''
     RADAIQuestionnaireForm2
    '''
    form_nr = 2
    form_template = 'questionnaire/forms/RADAIQuestionnaireForm1.html'

    field_nrs = {
        'right_hip_pain_score': 1,
        'right_knee_pain_score': 3,
        'right_ankle_pain_score': 5,
        'right_toes_pain_score': 7,
        'left_hip_pain_score': 2,
        'left_knee_pain_score': 4,
        'left_ankle_pain_score': 6,
        'left_toes_pain_score': 8}

    class Meta:
        # from apps.questionnaire.models import QOLQuestionnaire
        model = RADAIQuestionnaire

        fieldsets = (('patient_image_right',
                      {'fields': ('right_hip_pain_score',
                                  'right_knee_pain_score',
                                  'right_ankle_pain_score',
                                  'right_toes_pain_score')}),
                     ('patient_image_left',
                      {'fields': ('left_hip_pain_score',
                                  'left_knee_pain_score',
                                  'left_ankle_pain_score',
                                  'left_toes_pain_score')}),
                     )

        # auto create exclude based on fieldsets
        # print create_exclude_list(model, fieldsets)
        exclude = create_exclude_list(model, fieldsets)

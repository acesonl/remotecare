from django.conf.urls import url
from apps.questionnaire.wizards import QuestionnaireWizard

from apps.questionnaire.views import DiseaseActivityOverview,\
    QualityOfLifeOverview, HealthcareQualityOverview,\
    QuestionnaireFinishedView, QuestionnaireStartControle,\
    QuestionnaireStartUrgent, QuestionnaireRequestRemove

urlpatterns = (
    url('^(?P<questionnaire_request_id>\d+)/finish/$',
        QuestionnaireFinishedView.as_view(),
        name='questionnaire_finish'),

    url('^(?P<questionnaire_request_id>\d+)/remove_controle/$',
        QuestionnaireRequestRemove.as_view(),
        name='questionnaire_request_remove'),

    url('^start_controle/$',
        QuestionnaireStartControle.as_view(),
        name='questionnaire_start_controle'),

    url('^start_urgent/$',
        QuestionnaireStartUrgent.as_view(),
        name='questionnaire_start_urgent'),

    url('^disease_activity/$',
        DiseaseActivityOverview.as_view(),
        name='disease_activity_overview'),

    url('^quality_of_life/$',
        QualityOfLifeOverview.as_view(),
        name='quality_of_life_overview'),

    url('^healthcare_quality/$',
        HealthcareQualityOverview.as_view(),
        name='healthcare_quality_overview'),

    url('^(?P<questionnaire_request_id>\d+)/fillin/$',
        QuestionnaireWizard.as_view(),
        name='questionnaire_fillin'),
    )

# -*- coding: utf-8 -*-
from django.conf.urls import url
from apps.api.views import PatientExists, PrepareNewPatient,\
    ObtainAuthToken, LoginAndAddNewPatient, LoginAndShowPatient, PrepareLoginAndShowPatient,\
    HealthProfessionalExists, AddHealthProfessional, QuestionnaireList, QuestionnaireDetails

urlpatterns = (
    url(
        r'^loginandaddnewpatient/$',
        LoginAndAddNewPatient.as_view(),
        name='login_and_add_patient'),
    url(
        r'^loginandshowpatient/$',
        LoginAndShowPatient.as_view(),
        name='login_and_show_patient'),
    url(
        r'^authtoken/',
        ObtainAuthToken.as_view(),
        name='api_auth_token'),
    url(
        r'^(?P<username>\S+)/(?P<external_patient_id>\d+)/patient_exists/$',
        PatientExists.as_view(),
        name='api_patient_exists'),
    url(
        r'^(?P<username>\S+)/(?P<external_healthprofessional_id>\d+)/healthprofessional_exists/$',
        HealthProfessionalExists.as_view(),
        name='api_healthprofessional_exists'),
    url(
        r'^(?P<username>\S+)/(?P<external_healthprofessional_id>\d+)/add_healthprofessional/$',
        AddHealthProfessional.as_view(),
        name='api_add_healthprofessional'),

    url(
        r'^(?P<username>\S+)/(?P<external_patient_id>\d+)/'
        '(?P<external_healthprofessional_id>\d+)/prepare_new_patient/$',
        PrepareNewPatient.as_view(),
        name='api_prepare_new_patient'),
    url(
        r'^(?P<username>\S+)/(?P<external_patient_id>\d+)/'
        '(?P<external_healthprofessional_id>\d+)/prepare_login_and_show_patient/$',
        PrepareLoginAndShowPatient.as_view(),
        name='api_prepare_login_and_show_patient'),
    url(
        r'^(?P<username>\S+)/(?P<external_patient_id>\d+)/questionnaires/$',
        QuestionnaireList.as_view(),
        name='questionnaires'),
    url(
        r'^(?P<username>\S+)/(?P<external_patient_id>\d+)/(?P<questionnaire_id>\d+)/questionnaire_details/$',
        QuestionnaireDetails.as_view(),
        name='questionnaire_details')

    )



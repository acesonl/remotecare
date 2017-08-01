from django.conf.urls import url

from apps.healthperson.patient.views import\
    PatientNotificationView, PatientNotificationEditView,\
    PatientProfileView, PatientProfileEditView,\
    PatientAppointmentsView, PatientPersonaliaView,\
    PatientMessagesView, PatientReportsView,\
    PatientControlesView, PatientFreqControlView,\
    PatientPersonaliaEditView, QuestionnaireForDiagnose,\
    PatientFreqControlEditView, PatientSearchView,\
    HealthPatientAddView, PatientRemoveView

urlpatterns = (
    # Used for patient self
    url('^(?P<patient_session_id>\S+)/view/notification/$',
        PatientNotificationView.as_view(),
        name='patient_view_notification'),
    url('^(?P<patient_session_id>\S+)/edit/notification/$',
        PatientNotificationEditView.as_view(),
        name='patient_edit_notification'),
    url('^(?P<patient_session_id>\S+)/view/profile/$',
        PatientProfileView.as_view(),
        name='patient_view_profile'),
    url('^(?P<patient_session_id>\S+)/edit/profile/$',
        PatientProfileEditView.as_view(),
        name='patient_edit_profile'),



    # Used for admins
    url('^(?P<patient_session_id>\S+)/view/personalia/$',
        PatientPersonaliaView.as_view(),
        name='patient_view_personalia'),
    url('^(?P<patient_session_id>\S+)/edit/personalia/$',
        PatientPersonaliaEditView.as_view(),
        name='patient_edit_personalia'),

    url('^(?P<patient_session_id>\S+)/view/control_frequency/$',
        PatientFreqControlView.as_view(),
        name='patient_view_freq_control'),
    url('^(?P<patient_session_id>\S+)/edit/control_frequency/$',
        PatientFreqControlEditView.as_view(),
        name='patient_edit_freq_control'),

    url('^(?P<patient_session_id>\S+)/view/controles/$',
        PatientControlesView.as_view(),
        name='patient_view_controles'),
    url('^(?P<patient_session_id>\S+)/view/reports/$',
        PatientReportsView.as_view(),
        name='patient_view_reports'),
    url('^(?P<patient_session_id>\S+)/view/messages/$',
        PatientMessagesView.as_view(),
        name='patient_view_messages'),
    url('^(?P<patient_session_id>\S+)/view/appointments/$',
        PatientAppointmentsView.as_view(),
        name='patient_view_appointments'),

    url('^(?P<patient_session_id>\S+)/remove/$',
        PatientRemoveView.as_view(),
        name='patient_remove'),

    url('^(?P<patient_session_id>\S+)/questionnaire_exclude_list/$',
        QuestionnaireForDiagnose.as_view(),
        name='get_questionnaires_for_diagnose_by_patient'),
    url('^questionnaire_exclude_list/$',
        QuestionnaireForDiagnose.as_view(),
        name='get_questionnaires_for_diagnose'),

    url('^add/$',
        HealthPatientAddView.as_view(),
        name='patient_add'),
    url('^search/$',
        PatientSearchView.as_view(),
        name='patient_search'),
    #    url('^edit/$', 'message_edit', name='message_edit'),
    )

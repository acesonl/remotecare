from django.conf.urls import url


from apps.rcmessages.views import MessageAdd, SentMessageSearch,\
    MessageSent, SentMessageOverview, SentMessageDetails, MessageDetails,\
    MessageOverview

urlpatterns = (
    url('^patient/(?P<patient_session_id>\S+)/add/$',
        MessageAdd.as_view(),
        name='message_add'),

    url('^patient/(?P<patient_session_id>\S+)/message_sent/$',
        MessageSent.as_view(),
        name='message_sent'),

    url('^patient/(?P<patient_session_id>\S+)/(?P<message_id>\d+)/details/$',
        MessageDetails.as_view(),
        name='message_details'),

    url('^patient/(?P<patient_session_id>\S+)/$',
        MessageOverview.as_view(),
        name='message_overview'),

    url('^sent/(?P<healthperson_session_id>\S+)' +
        '/(?P<message_id>\d+)/sent/details/$',
        SentMessageDetails.as_view(),
        name='sent_message_details'),

    url('^sent/(?P<healthperson_session_id>\S+)/search/$',
        SentMessageSearch.as_view(),
        name='sent_message_search'),

    url('^sent/(?P<healthperson_session_id>\S+)/$',
        SentMessageOverview.as_view(),
        name='sent_message_overview'),
)

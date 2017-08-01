from django.conf.urls import include, url
from django.conf import settings
from apps.base.views import IndexView, SearchView, AgreeWithRulesView
from core.views import xsendfileserve
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = [
    # All urls for the different parts.
    url(r'^information/', include('apps.information.urls')),
    url(r'^messages/', include('apps.rcmessages.urls')),
    url(r'^api/', include('apps.api.urls')),
    url(r'^patient/(?P<patient_session_id>\S+)/questionnaire/',
        include('apps.questionnaire.urls')),
    url(r'^patient/(?P<patient_session_id>\S+)/report/',
        include('apps.report.urls')),
    url(r'^patient/(?P<patient_session_id>\S+)/appointment/',
        include('apps.appointment.urls')),
    url(r'^patient/',
        include('apps.healthperson.patient.urls')),
    url(r'^management/',
        include('apps.healthperson.management.urls')),
    url(r'^secretariat/',
        include('apps.healthperson.secretariat.urls')),
    url(r'^healthprofessional/',
        include('apps.healthperson.healthprofessional.urls')),

    # Login & authentication urls
    url(r'^', include('apps.authentication.urls')),
    url(r'^agreewithrules/$',
        AgreeWithRulesView.as_view(),
        name='agree_with_rules'),

    # index for all groups, index automatically
    # invokes the index view for a group
    # Search page does exactly the same.
    url(r'^search/$', SearchView.as_view(), name='index_search'),
    url(r'^$', IndexView.as_view(), name='index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Serve the /media/ directory through Django
    # allowing authentication of the user.
    #
    # if the USE_XSENDFILE is set to True in the
    # settings file it uses the webserver (if configured) to serve the file
    url(r'^media/(?P<path>.*)$',  # pragma: no cover
        xsendfileserve,  # pragma: no cover
        {'document_root': settings.MEDIA_ROOT}),  # pragma: no cover
]

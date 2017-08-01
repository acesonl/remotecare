from django.conf.urls import url

from apps.healthperson.secretariat.views import\
    SecretariatSearchView, SecretariatAddView,\
    SecretariatRemove, SecretariatPersonaliaView,\
    SecretariatPersonaliaEdit

urlpatterns = (
    url('^add/$',
        SecretariatAddView.as_view(),
        name='secretariat_add'),
    url('^search/$',
        SecretariatSearchView.as_view(),
        name='secretariat_search'),
    url('^(?P<secretary_session_id>\S+)/view/personalia/$',
        SecretariatPersonaliaView.as_view(),
        name='secretariat_view_personalia'),
    url('^(?P<secretary_session_id>\S+)/edit/personalia/$',
        SecretariatPersonaliaEdit.as_view(),
        name='secretariat_edit_personalia'),
    url('^(?P<secretary_session_id>\S+)/remove/$',
        SecretariatRemove.as_view(),
        name='secretariat_remove'),
    )

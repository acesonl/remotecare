from django.conf.urls import url

from apps.healthperson.management.views import ManagerPersonaliaView,\
    ManagerPersonaliaEdit

urlpatterns = (
    url('^(?P<manager_session_id>\S+)/view/personalia/$',
        ManagerPersonaliaView.as_view(),
        name='manager_view_personalia'),
    url('^(?P<manager_session_id>\S+)/edit/personalia/$',
        ManagerPersonaliaEdit.as_view(),
        name='manager_edit_personalia'),
)

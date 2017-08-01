from django.conf.urls import url
from apps.appointment.views import AppointmentEdit

urlpatterns = (
    url(
        '^(?P<questionnaire_request_id>\d+)/edit_appointment/$',
        AppointmentEdit.as_view(),
        name='appointment_edit'),)

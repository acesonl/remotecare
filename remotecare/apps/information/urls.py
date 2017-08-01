from django.conf.urls import url
from apps.information.views import InformationPageView, AboutSecurityView,\
    InformationFeedbackSentView, InformationFeedBack

urlpatterns = (
    url('^about_security/$',
        AboutSecurityView.as_view(),
        name='about_security'),
    url('^feedback/$',
        InformationFeedBack.as_view(),
        name='information_feedback'),
    url('^feedback_sent/$',
        InformationFeedbackSentView.as_view(),
        name='information_feedback_sent'),
    url('^(?P<page>\S+)/$',
        InformationPageView.as_view(),
        name='information_page'),
    )

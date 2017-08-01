from django.conf.urls import url

from apps.authentication.views import EmailSentView, ForgotPassword,\
    RequestSMSCodeView, ResetPassword, LoginView, LogoutView, SMScodeView

urlpatterns = (
    url('^resetpassword/smscode/$',
        RequestSMSCodeView.as_view(),
        name='request_sms_code'),
    url('^resetpassword/password/$',
        ResetPassword.as_view(),
        name='reset_password'),
    url('^forgotpassword/$',
        ForgotPassword.as_view(),
        name='forgot_password'),
    url('^emailsent/$',
        EmailSentView.as_view(),
        name='email_sent'),
    url('^smscode/$',
        SMScodeView.as_view(),
        name='smscode'),
    url('^login/$',
        LoginView.as_view(),
        name='login'),
    url(r'^logout/$',
        LogoutView.as_view(),
        name='logout'),
    )

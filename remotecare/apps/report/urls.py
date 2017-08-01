from django.conf.urls import url

from apps.report.views import QuestionnaireView, ReportView,\
    ReportDocX, ReportPDF, PrintReport,\
    UrgentReportEdit, ReportEdit, MessageView,\
    MessageEdit, HandlingFinish


urlpatterns = (
    url('^(?P<questionnaire_request_id>\d+)/edit_report/$',
        ReportEdit.as_view(),
        name='report_edit'),
    url('^(?P<questionnaire_request_id>\d+)/urgent_edit_report/$',
        UrgentReportEdit.as_view(),
        name='urgent_report_edit'),
    url('^(?P<questionnaire_request_id>\d+)/view_report/$',
        ReportView.as_view(),
        name='report_view'),
    url('^(?P<questionnaire_request_id>\d+)/print_report/$',
        PrintReport.as_view(),
        name='report_print'),
    url('^(?P<questionnaire_request_id>\d+)/pdf_report/$',
        ReportPDF.as_view(),
        name='report_pdf'),
    url('^(?P<questionnaire_request_id>\d+)/docx_report/$',
        ReportDocX.as_view(),
        name='report_docx'),
    url('^(?P<questionnaire_request_id>\d+)/view_questionnaire/$',
        QuestionnaireView.as_view(),
        name='questionnaire_view'),
    url('^(?P<questionnaire_request_id>\d+)/edit_message/$',
        MessageEdit.as_view(),
        name='message_edit'),
    url('^(?P<questionnaire_request_id>\d+)/view_message/$',
        MessageView.as_view(),
        name='message_view'),
    url('^(?P<questionnaire_request_id>\d+)/finish/$',
        HandlingFinish.as_view(),
        name='handling_finish'),
    )

# -*- coding: utf-8 -*-
"""
This module contains a class for generating report templates and
views for adding/editing and exporting reports.

:subtitle:`Class definitions:`
"""
from datetime import date
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from apps.utils.utils import send_notification_of_new_report
from apps.questionnaire.models import QuestionnaireRequest
from apps.questionnaire.qohc.models import QOHCQuestionnaire
from apps.report.models import Report
from apps.report.forms import ReportAddEditForm,\
    MessageAddEditForm, UrgentReportAddEditForm
from apps.rcmessages.models import RCMessage
from django.utils.translation import ugettext as _
from apps.utils.pdf import render_to_PDF
from apps.utils.docxhelper import render_to_DocX
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.patient.views import PatientBaseView

# Templates definitions for included diseases
URGENT_TEMPLATES = {
    'rheumatoid_arthritis': 'report/letter/rheumatism_urgent.html',
    'chron': 'report/letter/ibd_urgent.html',
    'intestinal_transplantation': 'report/letter/if_urgent.html',
    'colitis_ulcerosa': 'report/letter/ibd_urgent.html'
    }

DEFAULT_TEMPLATES = {
    'rheumatoid_arthritis': 'report/letter/rheumatism.html',
    'chron': 'report/letter/ibd.html',
    'intestinal_transplantation': 'report/letter/if.html',
    'colitis_ulcerosa': 'report/letter/ibd.html'
    }


class ReportTemplateGenerator:
    '''
    Class for generating a template of a report
    to be edited by an healthprofessional resulting
    in the final report.
    '''
    finishquestionnaire = None

    def get_questionnaires(self, questionnaire_request):
        """
        Get the questionnaires for a questionnaire_request

        Args:
            - questionnaire_request: the questionnaire_request to get\
              the questionnaires for.

        Returns:
            A list of questionnaires for the given questionnaire_request
        """
        questionnaire_all_steps =\
            questionnaire_request.requeststep_set.all().order_by('step_nr')

        questionnaires = []
        for questionnaire_step in questionnaire_all_steps:
            questionnaire_model_class = questionnaire_step.model_class
            questionnaire = get_object_or_404(
                questionnaire_model_class, request_step=questionnaire_step)
            questionnaires.append(questionnaire)

        return questionnaires

    def get_context(self, patient, healthprofessional, questionnaire_request):
        """
        Generate the default context used to render all report templates

        Args:
            - patient: the patient instance to include
            - healthprofessional: the healthprofessional instance to include
            - questionnaire_request: the questionnaire_request instance to\
                                     include

        Returns:
            the context dict
        """

        current_date = date.today()
        context = {
            'patient': patient,
            'questionnaire_request': questionnaire_request,
            'current_date': current_date,
            'healthprofessional': healthprofessional,
            'is_male': patient.user.gender == 'male'
            }

        questionnaires = self.get_questionnaires(questionnaire_request)

        for questionnaire in questionnaires:
            if questionnaire.lower_case_name == 'finishquestionnaire':
                self.finishquestionnaire = questionnaire
            context.update({questionnaire.lower_case_name: questionnaire})

        return context

    def render_template(self, request, patient,
                        healthprofessional, questionnaire_request,
                        template_name):
        """
        Render the template based on the given arguments

        Args:
            - request: the current request
            - patient: the patient coupled to the report
            - healthprofessional: the healthprofessional of the patient
            - questionnaire_request: the questionnaire_request coupled to this\
                                     report
            - template_name: the (relative) path & name of the template

        Returns:
            The rendered template
        """
        template = loader.get_template(template_name)
        context = self.get_context(
                patient,
                healthprofessional,
                questionnaire_request)

        return template.render(context, request)


class ReportBaseView(PatientBaseView):
    '''
    Base class based view for all report generating views.
    Conditionally adds report, message to the view if present.
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        questionnaire_request_id = kwargs.get('questionnaire_request_id', None)
        self.questionnaire_request = get_object_or_404(
            QuestionnaireRequest, id=questionnaire_request_id)
        self.healthprofessional = self.request.user.healthperson

        try:
            self.report = Report.objects.get(
                questionnaire_request=self.questionnaire_request)
        except Report.DoesNotExist:
            self.report = None

        try:
            self.message = RCMessage.objects.get(
                related_to=self.questionnaire_request,
                healthprofessional=self.healthprofessional
            )
        except RCMessage.DoesNotExist:
            self.message = None

        return super(ReportBaseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReportBaseView, self).get_context_data(**kwargs)

        context.update(
            {'report': self.report,
             'rc_message': self.message,
             'questionnaire_request': self.questionnaire_request})

        return context


class QuestionnaireView(ReportBaseView, TemplateView):
    '''
    Class based view for showing all filled in data
    of a questionnaire. Uses the same templates as
    used for the patient questionnaire views.
    '''
    template_name = 'report/questionnaire_view.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionnaireView, self).get_context_data(**kwargs)

        questionnaire_all_steps =\
            self.questionnaire_request.requeststep_set.all().order_by(
                'step_nr')

        questionnaires = []

        for questionnaire_step in questionnaire_all_steps:

            questionnaire_model_class = questionnaire_step.model_class
            questionnaire = questionnaire_model_class.objects.get(
                request_step=questionnaire_step)

            # Don't add the quality of health
            # care questionnaire: QOHCQuestionnaire
            if not isinstance(questionnaire, QOHCQuestionnaire):
                questionnaires.append(questionnaire)

        selected_questionnaire = questionnaires[0]

        if 'questionnaire' in self.request.GET:
            try:
                index = int(str(self.request.GET['questionnaire']))
                if index > 0 and index < len(questionnaires):
                    selected_questionnaire = questionnaires[index]
            except ValueError:
                selected_questionnaire = questionnaires[0]

        context.update(
            {'questionnaires': questionnaires,
             'selected_questionnaire': selected_questionnaire,
             'section': 'questionnaire'}
        )
        return context


class ReportView(ReportBaseView, TemplateView):
    '''
    Shows the (decrypted) report
    '''
    template_name = 'report/report_view.html'

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        context.update({'section': 'report'})
        return context


class ReportExportBase(ReportBaseView):
    '''
    Class based view which is the base for
    all export views (currently DocX and PDF)
    '''
    def get_body(self):
        """
        Returns:
            The body in HTML to export.
        """
        template = 'report/report_print.html'
        template = loader.get_template(template)

        context = {
            'report': self.report, 'rc_message': self.message,
            'section': 'report',
            'questionnaire_request': self.questionnaire_request}

        return template.render(context, self.request)


class ReportDocX(ReportExportBase):
    '''
    Returns the report in DocX format
    '''
    def get(self, request, *args, **kwargs):
        return render_to_DocX(request, self.get_body())


class ReportPDF(ReportExportBase):
    '''
    Returns the report in PDF format
    '''
    def get(self, request, *args, **kwargs):
        return render_to_PDF(request, self.get_body())


# Currently unused.
class PrintReport(ReportExportBase):  # pragma: no cover
    '''
    Returns the report in HTML for easy printing
    (Not used on the moment)
    '''
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.get_body())


class ReportEditbase(ReportBaseView, FormView):
    '''
    Class based view which is the base
    for the editing/adding reports views
    '''
    template_name = 'report/report_edit.html'

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'report_view',
            args=[self.kwargs.get('patient_session_id'),
                  self.kwargs.get('questionnaire_request_id')]
        )
        return super(ReportEditbase, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReportEditbase, self).get_form_kwargs()

        if self.report:
            kwargs.update({'instance': self.report})
        else:
            report_initial =\
                _("Voor dit ziektebeeld is nog geen template gedefineerd.")
            if self.patient.diagnose in self._templates:
                template = self._templates[self.patient.diagnose]
                self.report_generator = ReportTemplateGenerator()
                report_initial = self.report_generator.render_template(
                    self.request,
                    self.patient,
                    self.healthprofessional,
                    self.questionnaire_request,
                    template
                )
            initial = {'report': report_initial}
            kwargs.update({'initial': initial})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReportEditbase, self).get_context_data(**kwargs)
        context.update(
            {'section': 'report', 'rc_message': self.message,
             'questionnaire_request': self.questionnaire_request}
        )
        return context

    def form_valid(self, form):
        report = form.save(commit=False)
        report.created_by = self.healthprofessional
        report.questionnaire_request = self.questionnaire_request
        report.save()
        return super(ReportEditbase, self).form_valid(form)


class UrgentReportEdit(ReportEditbase):
    '''
    Edit reports for urgent controls
    '''
    form_class = UrgentReportAddEditForm
    _templates = URGENT_TEMPLATES


class ReportEdit(ReportEditbase):
    '''
    Edit reports for normal controls
    '''

    form_class = ReportAddEditForm
    _templates = DEFAULT_TEMPLATES

    def get_form_kwargs(self):
        kwargs = super(ReportEdit, self).get_form_kwargs()

        report_generator = ReportTemplateGenerator()
        questionnaires = report_generator.get_questionnaires(
            self.questionnaire_request)
        finishquestionnaire = questionnaires[len(questionnaires) - 1]

        kwargs.update({'finishquestionnare': finishquestionnaire})

        if self.request.POST:
            kwargs.update({'post': True})

        return kwargs


class MessageView(ReportView):
    '''
    Show the (decrypted) message
    '''

    template_name = 'report/message_view.html'

    def get_context_data(self, **kwargs):
        context = super(MessageView, self).get_context_data(**kwargs)
        context.update(
            {'section': 'message', 'rc_message': self.message,
             'questionnaire_request': self.questionnaire_request}
        )

        return context


class MessageEdit(ReportBaseView, FormView):
    '''
    Edit an existing message
    '''

    template_name = 'report/message_edit.html'
    form_class = MessageAddEditForm

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'message_view',
            args=[self.kwargs.get('patient_session_id'),
                  self.kwargs.get('questionnaire_request_id')]
        )
        return super(MessageEdit, self).dispatch(*args, **kwargs)

    def get_questionnaires(self):
        questionnaire_all_steps =\
            self.questionnaire_request.requeststep_set.all().order_by(
                'step_nr')

        questionnaires = []
        for questionnaire_step in questionnaire_all_steps:
            questionnaire_model_class = questionnaire_step.model_class
            questionnaire = get_object_or_404(
                questionnaire_model_class, request_step=questionnaire_step)
            questionnaires.append(questionnaire)

        return questionnaires

    def get_default_urgent_message_template(self):
        current_date = date.today()
        template_name =\
            'report/message/healthprofessional_default_urgent_response.html'
        template = loader.get_template(template_name)
        context = {
            'patient': self.patient,
            'questionnaire_request': self.questionnaire_request,
            'current_date': current_date,
            'healthprofessional': self.healthprofessional,
            'report': self.report,
            'is_male': self.patient.user.gender == 'male'}

        return template.render(context, self.request)

    def get_default_message_template(self):
        questionnaires = self.get_questionnaires()
        current_date = date.today()
        startquestionnaire = questionnaires[0]
        finishquestionnaire = questionnaires[len(questionnaires) - 1]

        template_name =\
            'report/message/healthprofessional_default_response.html'
        template = loader.get_template(template_name)
        context = {
            'patient': self.patient,
            'questionnaire_request': self.questionnaire_request,
            'current_date': current_date,
            'startquestionnaire': startquestionnaire,
            'finishquestionnaire': finishquestionnaire,
            'healthprofessional': self.healthprofessional,
            'report': self.report,
            'is_male': self.patient.user.gender == 'male'}

        return template.render(context, self.request)

    def get_form_kwargs(self):
        """Include the healthprofessional instance"""
        kwargs = super(MessageEdit, self).get_form_kwargs()

        if self.message:
            kwargs.update({'instance': self.message})
        else:
            if self.questionnaire_request.urgent:
                message_initial = self.get_default_urgent_message_template()
            else:
                message_initial = self.get_default_message_template()

            initial = {'internal_message': message_initial}
            kwargs.update({'initial': initial})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MessageEdit, self).get_context_data(**kwargs)
        context.update(
            {'section': 'message',
             'rc_message': self.message,
             'questionnaire_request': self.questionnaire_request}
        )
        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.patient = self.patient
        message.related_to = self.questionnaire_request
        message.healthprofessional = self.healthprofessional
        message.save()
        return super(MessageEdit, self).form_valid(form)


class HandlingFinish(ReportView):
    '''
    When a report and message has been added the
    questionnaire handling can be 'finished'
    by the healthprofessional. During this step the message is
    sent to the patient and the report becomes read-only.
    '''
    template_name = 'report/finish.html'

    def post(self, args, **kwargs):
        self.questionnaire_request.handled_on = date.today()
        self.questionnaire_request.handled_by = self.healthprofessional

        # save if an appointment should be made by the secretariat
        appointment_needed = False
        if self.questionnaire_request.patient_needs_appointment:
            # patient has requested an appointment
            appointment_needed = True
        else:
            # If the patient has not requested an appointment,
            # check if the healthprofessional has
            # set this instead.
            appointment_needed = self.report.patient_needs_appointment

        # appointment_needed is used for the secretary view
        self.questionnaire_request.appointment_needed = appointment_needed
        self.questionnaire_request.changed_by_user = self.request.user
        self.questionnaire_request.save()

        self.message.added_on = date.today()
        self.message.save()

        self.report.finished_on = date.today()
        self.report.created_by = self.healthprofessional
        self.report.changed_by_user = self.request.user
        self.report.save()

        # send notification to patient
        send_notification_of_new_report(self.patient)

        return HttpResponseRedirect(reverse('index'))

    def get_context_data(self, **kwargs):
        context = super(HandlingFinish, self).get_context_data(**kwargs)
        context.update(
            {'section': 'finish', 'rc_message': self.message,
             'questionnaire_request': self.questionnaire_request}
        )

        return context

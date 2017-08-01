# -*- coding: utf-8 -*-
"""
This module contains all views used by the patient self
or by other healhtpersons that administrate patients.

:subtitle:`Class definitions:`
"""
from datetime import datetime
import json as simplejson
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from apps.healthperson.patient.models import Patient
from apps.healthperson.healthprofessional.models import HealthProfessional

from apps.account.models import User
from apps.healthperson.patient.forms import PatientAddForm, PatientSearchForm,\
    PatientPersonaliaEditForm, PatientPersonaliaEditFormManager,\
    PatientDiagnoseControleEditForm, PatientProfileEditForm,\
    PatientNotificationEditForm

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from apps.utils.utils import sent_password_change_request
from django.db.models import Q
from apps.healthperson.utils import is_allowed_patient_admins,\
    is_allowed_patient, is_allowed_healthprofessional, login_url
from apps.questionnaire.models import QuestionnaireRequest,\
    QUESTIONNAIRE_EXCLUDE_LIST, get_model_class
from apps.rcmessages.models import RCMessage

from django.utils.html import strip_tags

from apps.report.models import Report
from apps.appointment.models import Appointment

from django.contrib.sites.requests import RequestSite
from core.encryption.random import randomkey
from django.http import Http404

from apps.base.views import BaseIndexTemplateView
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.views import BaseAddView
from apps.api.models import TempPatientData, PatientCoupling, APIUser


# Helper function for getting the patient from a session
def get_patient(request, patient_session_id):
    """
    Helper function for getting the patient from a patient_session_id

    Args:
        - request: the request instance
        - patient_session_id: the patient_session_id coupled to the patient

    Returns:
        the patient instance
    """
    healthperson_ptr_id = request.session[patient_session_id][8:]
    try:
        patient = Patient.objects.select_related(
            'user__personal_encryption_key').get(
            healthperson_ptr_id=healthperson_ptr_id)
    except Patient.DoesNotExist:
        raise Http404
    return patient


class PatientBaseView(View):
    """Base view which adds the patient by using the patient_session_id
       or logged in user"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Add patient to the view class"""
        if 'patient_session_id' in kwargs:
            patient_session_id = kwargs.get('patient_session_id')
            if patient_session_id not in self.request.session:
                raise Http404
            self.patient = get_patient(self.request, patient_session_id)
        else:
            # set secretary to self.
            self.patient = self.request.user.healthperson
        return super(PatientBaseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Base context, include the patient by default"""
        context = super(PatientBaseView, self).get_context_data(**kwargs)
        context.update({'patient': self.patient})
        return context


class PatientIndexView(BaseIndexTemplateView):
    """
    View which shows the homepage of the patient
    """
    template_name = 'patient/index.html'

    def get_all_messages_for_patient_index(self, patient):
        """
        Get all messages for a patient

        Args:
            - patient: the patient for with the messages should be returned

        Returns:
             A list with all messages for a patient
        """
        from apps.rcmessages.views import get_all_messages_for_patient
        # Get RCMessages
        rc_messages = get_all_messages_for_patient(patient)

        message_unread_count = rc_messages.filter(read_on__isnull=True).count()

        if patient.diagnose == 'intestinal_transplantation':
            self.template_name = 'patient/intestinal_transplantation.html'

        # RCMessage.objects.select_related(
        #    'secretary__user',
        #    'healthprofessional__user',
        #    'patient__user').filter(
        #    patient=patient,
        #    read_on__isnull=True).order_by('-added_on')

        # remove rc_messages with questionnaire_request that are not handled
        # new_rc_messages = []
        # for rc_message in rc_messages:
        #     if rc_message.related_to:
        #         if ((rc_message.related_to.handled_on or
        #              rc_message.related_to.urgent)):
        #             new_rc_messages.append(rc_message)
        #     else:
        #        new_rc_messages.append(rc_message)

        # rc_messages = new_rc_messages

        # message_unread_count = len(rc_messages)

        # add 2 read messages if count < 2
        rc_messages = rc_messages.select_related(
            'secretary__user',
            'healthprofessional__user',
            'patient__user').filter(
            patient=patient).order_by('-read_on', '-added_on')[:2]

        return [rc_messages, message_unread_count]

    def get_context_data(self, **kwargs):
        context = super(PatientIndexView, self).get_context_data(**kwargs)

        patient = Patient.objects.select_related(
            'current_practitioner__user').get(user=self.request.user)

        context.update({'practitioner': patient.current_practitioner})
        context.update({'patient': patient})

        [rc_messages, message_unread_count] =\
            self.get_all_messages_for_patient_index(patient)

        try:
            first_rc_message = rc_messages[0]
        except IndexError:
            first_rc_message = None

        context.update({'first_rc_message': first_rc_message})
        context.update({'message_unread_count': message_unread_count})
        context.update({'rc_messages': rc_messages})

        return context


class PatientGenericView(PatientBaseView, TemplateView):
    """
    Generic view based on the patient baseview and TemplateView
    """
    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientGenericView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientGenericView, self).get_context_data(**kwargs)
        context.update({'submenu': self.submenu})
        return context


class PatientNotificationView(PatientGenericView):
    """
    Show the notification settings
    used by a different roles
    """
    template_name = 'patient/notification_view.html'
    submenu = 'notification'


class PatientNotificationEditView(PatientBaseView, FormView):
    """
    Edit the notification settings
    used by a patient
    """
    template_name = 'patient/edit_view.html'
    form_class = PatientNotificationEditForm

    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'patient_view_notification',
            args=(self.kwargs['patient_session_id'],))
        return super(PatientNotificationEditView,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PatientNotificationEditView, self).get_form_kwargs()
        kwargs.update({'instance': self.patient})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PatientNotificationEditView,
                        self).get_context_data(**kwargs)
        context.update({'section': _('Notificatie instellingen'),
                        'cancel_url': self.success_url})
        return context

    def form_valid(self, form):
        form.save()
        return super(PatientNotificationEditView, self).form_valid(form)


class PatientProfileView(PatientGenericView):
    """
    Shows the profile information of a patient
    used by a multiple roles
    """
    template_name = 'patient/profile_view.html'
    submenu = 'personalia'


class PatientProfileEditView(PatientBaseView, FormView):
    """
    Edit the profile information of a patient
    used by a patient
    """
    template_name = 'patient/edit_view.html'
    form_class = PatientProfileEditForm

    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'patient_view_profile',
            args=(self.kwargs['patient_session_id'],))
        return super(
            PatientProfileEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PatientProfileEditView, self).get_form_kwargs()
        kwargs.update({'instance': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(
            PatientProfileEditView, self).get_context_data(**kwargs)
        context.update({'section': _('Account'),
                        'cancel_url': self.success_url,
                        'extra_message': _(
                            'Let op: Zorg dat u deze gegevens correct' +
                            ' invoert. Zonder deze gegevens kunt u niet' +
                            ' meer inloggen in Remote Care.')})
        return context

    def form_valid(self, form):
        user = form.save(commit=False)

        # Change password
        if form.cleaned_data['change_password'] == 'yes':
            user.set_password(form.cleaned_data['password'])

        # save user
        user.save()
        return super(PatientProfileEditView, self).form_valid(form)


class PatientAppointmentsView(PatientBaseView, TemplateView):
    """
    Show the appointments information of a patient
    used by a healthprofessional
    """
    template_name = 'patient/appointments.html'

    @method_decorator(user_passes_test(
        is_allowed_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientAppointmentsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientAppointmentsView,
                        self).get_context_data(**kwargs)
        appointments = Appointment.objects.filter(
            questionnaire_request__patient=self.patient).order_by(
            '-created_on')

        context.update({'submenu': 'appointments',
                        'appointments': appointments})
        return context


class PatientPersonaliaView(PatientBaseView, TemplateView):
    """
    Show the profile information of a patient
    used by a patient admins
    """
    template_name = 'patient/personalia_view.html'

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientPersonaliaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientPersonaliaView, self).get_context_data(**kwargs)
        context.update({'submenu': 'personalia'})
        return context


class PatientMessagesView(PatientBaseView, TemplateView):
    """
    Show the messages sent to a patient
    used by healthprofessionals
    """
    template_name = 'patient/messages.html'

    @method_decorator(user_passes_test(
        is_allowed_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientMessagesView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientMessagesView, self).get_context_data(**kwargs)
        messages = RCMessage.objects.filter(
            patient=self.patient).order_by('-added_on')

        messages = messages.select_related(
            'secretary__user',
            'healthprofessional__user',
            'patient__user')

        selected_message = None

        if messages:
            if self.request.GET and 'message' in self.request.GET:
                try:
                    message_id = int(str(self.request.GET['message']))
                    selected_message = messages.get(id=message_id)
                except RCMessage.DoesNotExist:
                    selected_message = None

        has_searched = False

        if not selected_message and 'last_searchterm' in self.request.session:
            del self.request.session['last_searchterm']

        if ((self.request.POST and 'searchterm' in self.request.POST or
             'last_searchterm' in self.request.session)):
            has_searched = True

            results = []
            if 'searchterm' in self.request.POST:
                searchterm = self.request.POST['searchterm']
                self.request.session['last_searchterm'] =\
                    self.request.POST['searchterm']
            else:
                searchterm = self.request.session['last_searchterm']

            if len(searchterm) > 0:
                for message in messages:
                    if ((searchterm.lower() in
                         message.internal_message.lower() or
                         searchterm.lower() in message.subject.lower())):
                        results.append(message)

            messages = results

        if has_searched and len(messages) == 1:
            selected_message = messages[0]

        context.update({'submenu': 'message',
                        'has_searched': has_searched,
                        'rc_messages': messages,
                        'selected_message': selected_message})
        return context


class PatientReportsView(PatientBaseView, TemplateView):
    """
    Show the report for a patient
    used by healthprofessionals
    """
    template_name = 'patient/reports.html'

    @method_decorator(user_passes_test(
        is_allowed_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientReportsView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientReportsView, self).get_context_data(**kwargs)

        reports = Report.objects.filter(
            questionnaire_request__patient=self.patient).order_by(
            '-finished_on')

        selected_report = None

        if reports:
            if self.request.GET and 'report' in self.request.GET:
                try:
                    report_id = int(str(self.request.GET['report']))
                    selected_report = Report.objects.get(id=report_id)
                except Report.DoesNotExist:
                    selected_report = None

        if selected_report:
            # If post, make selected report invalid
            if self.request.POST and 'make_invalid' in self.request.POST:
                selected_report.invalid = True
                selected_report.save()

        context.update({'submenu': 'reports', 'reports': reports,
                        'selected_report': selected_report})

        return context


class PatientControlesView(PatientBaseView, TemplateView):
    """
    Show the finished controls for a patient
    used by healthprofessionals
    """
    template_name = 'patient/controles.html'

    @method_decorator(user_passes_test(
        is_allowed_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientControlesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientControlesView, self).get_context_data(**kwargs)

        controles = QuestionnaireRequest.objects.filter(
            patient=self.patient,
            finished_on__isnull=False).order_by('-finished_on')

        context.update({'submenu': 'controles', 'controles': controles})
        return context


class PatientFreqControlView(PatientBaseView, TemplateView):
    """
    Show the control and blood taken frequencies for a patient
    used by patient admins
    """
    template_name = 'patient/freq_controle_view.html'

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(PatientFreqControlView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            PatientFreqControlView, self).get_context_data(**kwargs)

        exclude_list = []
        questionnaire_list = []

        for entry in QUESTIONNAIRE_EXCLUDE_LIST:
            if entry[0] == self.patient.diagnose:
                exclude_list = entry[1]
                break

        # Add display name
        if exclude_list != []:
            questionnaire_list = []
            for questionnaire in exclude_list:
                questionnaire_step_name = get_model_class(
                    questionnaire).display_name

                excluded = False
                if self.patient.excluded_questionnaires:
                    if questionnaire in self.patient.excluded_questionnaires:
                        excluded = True
                if not excluded:
                    questionnaire_list.append(questionnaire_step_name)

        context.update({'questionnaire_list': questionnaire_list,
                        'submenu': 'control_freq'})
        return context


class PatientPersonaliaEditView(PatientBaseView, FormView):
    """
    Edit the personalia of a patient
    used by patient admins.

    ..Note::
        Managers use a different form for editing, including options\
        for resetting the password.
    """
    template_name = 'patient/edit_view.html'
    form_class = PatientPersonaliaEditForm

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'patient_view_personalia',
            args=(self.kwargs['patient_session_id'],))

        # from class override
        if self.request.user.default_group == 'managers':
            self.form_class = PatientPersonaliaEditFormManager

        return super(PatientPersonaliaEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PatientPersonaliaEditView, self).get_form_kwargs()
        kwargs.update({'instance': self.patient.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PatientPersonaliaEditView,
                        self).get_context_data(**kwargs)
        context.update({'is_manager':
                        self.request.user.default_group == 'managers',
                        'show_warning': True,
                        'cancel_url': self.success_url,
                        'section': _('Personalia & Account')})
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        old_user_email = user.email
        user.email = form.cleaned_data['email']
        test_email = user.email

        # save user
        user.save()

        resent_password_change_request = False
        if not user.has_usable_password() and test_email != old_user_email:
            resent_password_change_request = True

        if 'change_password' in form.cleaned_data:
            if form.cleaned_data['change_password'] == 'yes':
                resent_password_change_request = True

        # Change password required
        if resent_password_change_request:
            # if form.cleaned_data['change_password'] == 'yes':
            # user.set_password(form.cleaned_data['password'])
            rq = RequestSite(self.request)
            url_prefix = 'http'
            if self.request.is_secure():
                url_prefix += 's'
            url_prefix += '://' + rq.domain
            sent_password_change_request(user, url_prefix, True)

        return super(PatientPersonaliaEditView, self).form_valid(form)


class QuestionnaireForDiagnose(View):
    """
    Returns a JSON list of questionnaires available for a diagnose
    """
    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        if 'patient_session_id' in kwargs:
            patient_session_id = kwargs.get('patient_session_id')
            if patient_session_id not in self.request.session:
                raise Http404
            self.patient = get_patient(self.request, patient_session_id)
        else:
            self.patient = None
        return super(QuestionnaireForDiagnose, self).dispatch(*args, **kwargs)

    def get_questionnaires_for_diagnose_helper(self, selected_questionnaire):
        """
        Helper function for getting the questionnaires

        Returns:
            The list of questionnaires for the selected_questionnaire
        """
        exclude_list = []

        for entry in QUESTIONNAIRE_EXCLUDE_LIST:
            if entry[0] == selected_questionnaire:
                exclude_list = entry[1]
                break

        # Add display name
        if exclude_list is not []:
            l = []
            for questionnaire in exclude_list:
                questionnaire_step_name = get_model_class(
                    questionnaire).display_name
                excluded = False
                if self.patient:
                    if self.patient.excluded_questionnaires:
                        if ((questionnaire in
                             self.patient.excluded_questionnaires)):
                            excluded = True
                l.append([questionnaire, questionnaire_step_name, excluded])

            exclude_list = l

        return exclude_list

    def get(self, *args, **kwargs):
        selected_questionnaire = self.request.GET['questionnaire']
        exclude_list = self.get_questionnaires_for_diagnose_helper(
            selected_questionnaire)
        response = simplejson.dumps(
            exclude_list,
            skipkeys=True,
            indent=4,)
        return HttpResponse(response)


class PatientFreqControlEditView(PatientBaseView, FormView):
    """
    Edit the patient control and blood take frequency
    used by patient admins
    """
    template_name = 'patient/edit_view.html'
    form_class = PatientDiagnoseControleEditForm

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'patient_view_freq_control',
            args=(self.kwargs['patient_session_id'],))
        return super(
            PatientFreqControlEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PatientFreqControlEditView, self).get_form_kwargs()
        kwargs.update({'instance': self.patient})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PatientFreqControlEditView,
                        self).get_context_data(**kwargs)

        excluded_questionnaire_posted = None

        if self.request.POST:
            excluded_questionnaire_posted = self.request.POST.getlist(
                'exclude_questionnaires')
            if excluded_questionnaire_posted:
                excluded_questionnaire_posted = '[' + ', '.join(
                    '"' + str(x) + '"' for x in
                    excluded_questionnaire_posted) + ']'

        context.update({'add_diagnose_script': True,
                        'cancel_url': self.success_url,
                        'excluded_questionnaire_posted':
                        excluded_questionnaire_posted,
                        'section': _('Controle frequentie')})
        return context

    def form_valid(self, form):
        exclude_questionnaires = self.request.POST.getlist(
            'exclude_questionnaires')
        exclude_list = []

        for entry in QUESTIONNAIRE_EXCLUDE_LIST:
            if entry[0] == form.cleaned_data['diagnose']:
                exclude_list = entry[1]
                break

        exclude_list =\
            [item for item in
             exclude_list if item not in exclude_questionnaires]
        patient = form.save(commit=False)
        patient.excluded_questionnaires = ', '.join(
            str(x) for x in exclude_list)

        patient.save()
        return super(PatientFreqControlEditView, self).form_valid(form)


class PatientSearchView(FormView):
    """
    Search for patients view
    used by patient admins
    """
    template_name = 'patient/search.html'
    form_class = PatientSearchForm

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.has_searched = False
        self.patients = None
        return super(PatientSearchView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatientSearchView, self).get_context_data(**kwargs)
        context.update({'patients': self.patients,
                        'has_searched': self.has_searched})
        return context

    def get_initial(self):
        """Get initial data, used for showing the old results
           and form data when
           the user uses the back button to return to the form"""
        if (('last_search' in self.request.session and
             'back' in self.request.GET)):
            return self.request.session['last_search']
        return None

    def get(self, request, *args, **kwargs):
        """Re-execute the search if the user has used the back button"""
        if 'last_search' in request.session and 'back' in request.GET:
            form_class = self.get_form_class()
            form = form_class(request.session['last_search'])
            if form.is_valid():
                self.form_valid(form)
        return super(PatientSearchView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Perform the search action, search for a healthprofessional"""
        self.has_searched = True
        patients = None
        filter_valid = False

        # Build up search filter for persons
        hospital = self.request.user.hospital
        user_filter = Q(groups__name='patients') &\
            Q(hospital=hospital) & Q(deleted_on__isnull=True)



        if form.cleaned_data['last_name'] not in ('', None):
            filter_valid = True
            user_filter = user_filter & Q(
                hmac_last_name=form.cleaned_data['last_name'])

        if form.cleaned_data['local_hospital_number'] not in ('', None):
            filter_valid = True
            local_hospital_number = form.cleaned_data['local_hospital_number']
            user_filter = user_filter & Q(
                hmac_local_hospital_number=local_hospital_number)

        if form.cleaned_data['BSN'] not in ('', None):
            filter_valid = True
            user_filter = user_filter & Q(hmac_BSN=form.cleaned_data['BSN'])
        if form.cleaned_data['date_of_birth'] not in ('', None):
            filter_valid = True
            user_filter = user_filter & Q(
                date_of_birth=form.cleaned_data['date_of_birth'])

        if filter_valid:
            # Execute filter
            users = User.objects.filter(user_filter)

            if users:
                if self.request.POST:
                    self.request.session['last_search'] = self.request.POST

                patients = []
                for user in users:
                    patients.append(user.healthperson)

        self.patients = patients

        return super(PatientSearchView, self).get(
            self.request, *self.args, **self.kwargs)


class SearchView(TemplateView):
    """
    Search view for in the homepage of the patient
    allows searching for answers on questionnaires and messages
    """
    template_name = 'patient/search_index.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.objects = []
        self.no_search_term = False
        self.searchterm = None
        self.patient = self.request.user.healthperson
        return super(SearchView, self).dispatch(*args, **kwargs)

    # Helper function for getting all answers of
    # specific questionnaire categories
    def get_inner_context(self, request, patient, model_display_name):
        """
        Gets the questionnaires to be included into the results.

        Args:
            - request: the current request
            - patient: the patient who is searching
            - model_display_name: the model_display_name of the questionnaire\
              to search for.

        Returns:
            a list of questionnaires
        """
        questionnaire_requests = QuestionnaireRequest.objects.filter(
            patient=patient, finished_on__isnull=False).order_by(
            '-finished_on')

        # Get the 'model_display_name' questionnaires..
        disease_activity_questionnares = []
        for questionnaire_request in questionnaire_requests:
            questionnaire_all_steps =\
                questionnaire_request.requeststep_set.all().order_by('step_nr')

            for questionnaire_step in questionnaire_all_steps:
                questionnaire_model_class = questionnaire_step.model_class
                if ((questionnaire_model_class.display_name ==
                     model_display_name)):
                    questionnaire = questionnaire_model_class.objects.get(
                        request_step=questionnaire_step)
                    questionnaire.model_display_name = model_display_name
                    disease_activity_questionnares.append(questionnaire)

        return disease_activity_questionnares

    def post(self, request, *args, **kwargs):
        """
        Execute the search for questionnaires and messages based on
        'searchterm'
        """
        from apps.rcmessages.views import get_all_messages_for_patient
        objects = []

        if 'searchterm' in request.POST:
            # Build up search filter for persons
            searchterm = request.POST['searchterm'].lower()
            if searchterm not in (None, ''):
                rc_messages = get_all_messages_for_patient(self.patient)

                searchterm = searchterm.lower()

                # Search through messages
                for rc_message in rc_messages:
                    internal_message = strip_tags(
                        rc_message.internal_message).lower()
                    if searchterm in internal_message:
                        objects.append(rc_message)

                # Search through filled in questionnaires
                disease_activity = self.get_inner_context(
                    request, self.patient, 'Ziekteactiviteit')
                quality_of_life = self.get_inner_context(
                    request, self.patient, 'Kwaliteit van leven')
                quality_of_care = self.get_inner_context(
                    request, self.patient, 'Kwaliteit van zorg')

                # Concat
                questionnaires =\
                    disease_activity + quality_of_life + quality_of_care

                # Search through questionnaires
                for questionnaire in questionnaires:
                    for field in questionnaire._meta.fields:
                        # Check if search item is in the choices
                        value = getattr(questionnaire, field.name)
                        if value not in (None, '') and field.name != 'id':
                            if field.choices != []:
                                field_choice =\
                                    str([val for key, val in
                                        field.choices if key == value][0])
                                field_choice = field_choice.lower()
                                if searchterm in field_choice:
                                    objects.append(questionnaire)
                                    break
                            elif searchterm in str(value).lower():
                                objects.append(questionnaire)
                                break
            else:
                self.no_search_term = True

            self.objects = objects
            self.searchterm = searchterm
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({'objects': self.objects,
                        'patient': self.patient,
                        'searchterm': self.searchterm,
                        'no_search_term': self.no_search_term})

        return context


class HealthPatientAddView(BaseAddView):
    """
    Class based view for adding a new patient
    used by patient admins
    """
    form_class = PatientAddForm
    template_name = 'patient/add.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        """Check permissions"""
        self.succes_url = reverse('index')
        return super(HealthPatientAddView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HealthPatientAddView, self).get_context_data(**kwargs)
        if self.request.POST:
            excluded_questionnaire_posted =\
                self.request.POST.getlist('exclude_questionnaires')
            if excluded_questionnaire_posted:
                excluded_questionnaire_posted = '[' + ', '.join(
                    '"' + str(x) + '"' for x in
                    excluded_questionnaire_posted) + ']'
        else:
            excluded_questionnaire_posted = None

        if 'temppatientdata_id' in self.request.GET:
            context.update(
                {'extra_params': "?temppatientdata_id={0}".format(
                    self.request.GET['temppatientdata_id'])})

        context.update({'add_diagnose_script': True,
                        'excluded_questionnaire_posted':
                        excluded_questionnaire_posted})

        return context

    def get_form_kwargs(self):
        kwargs = super(HealthPatientAddView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})

        if 'temppatientdata_id' in self.request.GET:
            try:
                temp_patient_data = TempPatientData.objects.get(
                    id=self.request.GET['temppatientdata_id'])
            except TempPatientData.DoesNotExist:
                temp_patient_data = None

            if temp_patient_data is not None:
                initial = temp_patient_data.get_json_data()

                kwargs.update({'initial': initial})

        return kwargs

    def form_valid(self, form):
        user = self.get_user_for_form(form)

        patient = Patient()

        random_key = randomkey()
        #while (Patient.objects.filter(rc_registration_number=random_key).count() > 0):
        #    random_key = randomKey()

        patient.rc_registration_number = random_key

        patient.diagnose = form.cleaned_data['diagnose']
        patient.current_practitioner = HealthProfessional.objects.get(
            id=form.cleaned_data['current_practitioner'])
        patient.regular_control_frequency =\
            form.cleaned_data['regular_control_frequency']
        patient.blood_sample_frequency =\
            form.cleaned_data['blood_sample_frequency']
        patient.always_clinic_visit =\
            form.cleaned_data['always_clinic_visit']

        # Set questionnaire exclude list
        exclude_questionnaires =\
            self.request.POST.getlist('exclude_questionnaires')
        exclude_list = []

        for entry in QUESTIONNAIRE_EXCLUDE_LIST:
            if entry[0] == form.cleaned_data['diagnose']:
                exclude_list = entry[1]
                break

        exclude_list =\
            [item for item in exclude_list if item not
             in exclude_questionnaires]
        patient.excluded_questionnaires = ', '.join(
            str(x) for x in exclude_list)
        patient.changed_by_user = self.request.user
        patient.save()

        # add to patient group
        user.groups = [Group.objects.get(name='patients')]
        user.healthperson = patient
        user.save()

        patient_session_id = randomkey()
        self.request.session[patient_session_id] =\
            'storage_{0}'.format(patient.health_person_id)

        self.success_url = reverse(
            'patient_view_personalia',
            args=(patient_session_id,))

        # Create coupling data
        if 'temppatientdata_id' in self.request.GET:
            try:
                temp_patient_data = TempPatientData.objects.get(
                    id=self.request.GET['temppatientdata_id'])
            except TempPatientData.DoesNotExist:
                temp_patient_data = None

            if temp_patient_data is not None:
                initial = temp_patient_data.get_json_data()

                api_user = APIUser.objects.get(
                        username=initial['API_username'])

                patient_coupling = PatientCoupling(
                    patient=patient,
                    external_patient_id=initial['external_patient_id'],
                    api_user=api_user
                )
                patient_coupling.save()

        sent_password_change_request(user, self.url_prefix, False, True)

        return super(HealthPatientAddView, self).form_valid(form)


class PatientRemoveView(PatientBaseView, TemplateView):
    """
    Class based view for removing a patient
    used by patient admins
    """
    template_name = 'patient/remove_confirmation.html'

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.cancel_url = reverse('patient_search')
        return super(PatientRemoveView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Remove the patient by setting the user to inactive"""
        # remove password and set to inactive
        user = self.patient.user
        user.set_unusable_password()
        user.is_active = False
        user.deleted_on = datetime.now()
        user.changed_by_user = self.request.user
        user.save()
        return HttpResponseRedirect(self.cancel_url)

    def get_context_data(self, **kwargs):
        context = super(PatientRemoveView, self).get_context_data(**kwargs)
        context.update({'cancel_url': self.cancel_url})
        return context

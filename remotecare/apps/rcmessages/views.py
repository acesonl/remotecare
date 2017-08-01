# -*- coding: utf-8 -*-
"""
This module contains the class based views and functions
for messages.

:subtitle:`Class and function definitions:`
"""
from datetime import date
from django.core.urlresolvers import reverse
from apps.rcmessages.models import RCMessage
from apps.rcmessages.forms import MessageAddForm, MessageSearchForm
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.healthperson.secretariat.models import Secretary
from apps.utils.utils import send_notification_of_new_message
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.patient.views import PatientBaseView
from apps.healthperson.utils import is_allowed_patient_admins,\
    is_allowed_patient, login_url
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import Http404


def remove_not_handled_messages(rc_messages):
    """
    Function which removes messages that are coupled to a
    questionnaire which is not finished by a healthprofessional

    Args:
        - rc_messages: list of RCMessage instances to strip

    Returns:
        list of RCMessage instances
    """
    extra_filter = Q(related_to__isnull=True) |\
        (Q(related_to__isnull=False) &
         Q(related_to__handled_on__isnull=False)) |\
        (Q(related_to__isnull=False) &
         Q(related_to__urgent=True))

    return rc_messages.filter(extra_filter)

    # new_rc_messages = []

    # for rc_message in rc_messages:
    #    if rc_message.related_to:
    #        #Add messages for non urgent questionnaire request or ones
    #        #that are handled (=finished) by the healthprofessional
    #        if ((rc_message.related_to.handled_on or
    #             rc_message.related_to.urgent)):
    #            new_rc_messages.append(rc_message)
    #    else:
    #        new_rc_messages.append(rc_message)

    # return new_rc_messages


def get_all_messages_for_secretary(secretary):
    """
    Args:
        - secretary: the secretary to get all messages for

    Returns:
        all messages for a secretary
    """
    rc_messages = RCMessage.objects.filter(
        secretary=secretary).order_by('-added_on')

    # remove rc_messages with questionnaire_request that is not handled
    rc_messages = remove_not_handled_messages(rc_messages)

    return rc_messages


def get_all_messages_for_healthprofessional(healthprofessional):
    """
    Args:
        - healthprofessional: the healthprofessional to get all messages for

    Returns:
        all messages for a healthprofessional
    """
    rc_messages = RCMessage.objects.filter(
        healthprofessional=healthprofessional).order_by('-added_on')

    # remove rc_messages with questionnaire_request that is not handled
    rc_messages = remove_not_handled_messages(rc_messages)

    return rc_messages


def get_all_messages_for_patient(patient):
    """
    Args:
        - patient: the patient to get all messages for

    Returns:
        all messages for a patient
    """
    # Get RCMessages
    rc_messages = RCMessage.objects.filter(
        patient=patient).order_by('-added_on')

    # remove rc_messages with questionnaire_request that is not handled
    rc_messages = remove_not_handled_messages(rc_messages)

    return rc_messages


class MessageAdd(PatientBaseView, FormView):
    '''
    Class based view for adding a new message by a
    secretary or healthprofessional
    '''
    template_name = 'messages/add.html'
    form_class = MessageAddForm

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'message_sent', args=[self.kwargs.get('patient_session_id')])
        return super(MessageAdd, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        message = form.save(commit=False)
        if self.request.user.groups.filter(name='secretariat').exists():
            message.secretary = self.request.user.healthperson
        else:
            message.healthprofessional = self.request.user.healthperson

        message.patient = self.patient
        message.save()

        # Send notification to patient
        send_notification_of_new_message(self.patient)

        return super(MessageAdd, self).form_valid(form)


class SentMessageSearch(FormView):
    '''
    Search through sent messages
    either as an healthprofessional or secretary
    '''
    form_class = MessageSearchForm
    template_name = 'messages/search.html'

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        healthperson_ptr_id =\
            self.request.session[
                self.kwargs.get('healthperson_session_id')][8:]
        try:
            healthprofessional = HealthProfessional.objects.get(
                healthperson_ptr_id=healthperson_ptr_id)
            self.messages = get_all_messages_for_healthprofessional(
                healthprofessional)
            self.healthperson = healthprofessional
        except HealthProfessional.DoesNotExist:
            secretary = Secretary.objects.get(
                healthperson_ptr_id=healthperson_ptr_id)
            self.messages = get_all_messages_for_secretary(secretary)
            self.healthperson = secretary

        self.search_results = []
        self.searched = False

        return super(SentMessageSearch, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Return the found patients in a context"""
        context = super(SentMessageSearch, self).get_context_data(**kwargs)
        context.update({'healthperson': self.healthperson,
                        'search_results': self.search_results,
                        'rc_messages': self.messages, 'search': True,
                        'searched': self.searched,
                        'sent_view': True})
        return context

    def form_valid(self, form):
        # do_search
        self.searched = True
        self.search_results = []

        # TODO:Move to DB query, to speed up
        for message in self.messages:
            if ((form.cleaned_data['last_name'].lower() ==
                 message.patient.user.last_name.lower())):
                self.search_results.append(message)
            elif ((form.cleaned_data['BSN'].lower() ==
                   message.patient.user.BSN.lower())):
                self.search_results.append(message)

        return super(SentMessageSearch, self).get(
            self.request, *self.args, **self.kwargs)


class MessageSent(PatientBaseView, TemplateView):
    '''
    Shows a confirmation
    message that the message has been sent.
    '''
    template_name = 'messages/message_sent.html'


class SentMessageOverview(TemplateView):
    '''
    Generates an overview of all sent messages
    of either a healthprofessional or secretary
    when there are no messages, otherwise the sentmessagedetails
    view is used.
    '''
    template_name = 'messages/overview.html'

    def get_context_data(self, **kwargs):
        context = super(SentMessageOverview, self).get_context_data(**kwargs)
        context.update({'overview': True, 'sent_view': True})
        return context


class SentMessageDetails(TemplateView):
    '''
    Shows the contents of a sent message
    '''
    template_name = 'messages/detail.html'

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        healthperson_ptr_id = self.request.session[self.kwargs.get(
            'healthperson_session_id')][8:]
        try:
            healthprofessional = HealthProfessional.objects.get(
                healthperson_ptr_id=healthperson_ptr_id)
            self.messages = get_all_messages_for_healthprofessional(
                healthprofessional)
            self.healthperson = healthprofessional
        except HealthProfessional.DoesNotExist:
            secretary = Secretary.objects.get(
                healthperson_ptr_id=healthperson_ptr_id)
            self.messages = get_all_messages_for_secretary(secretary)
            self.healthperson = secretary

        return super(SentMessageDetails, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SentMessageDetails, self).get_context_data(**kwargs)

        self.messages = self.messages.select_related(
            'secretary__user',
            'healthprofessional__user',
            'patient__user')

        try:
            message = self.messages.get(pk=self.kwargs.get('message_id'))
        except:
            raise Http404

        context.update({'message': message, 'rc_messages': self.messages,
                        'healthperson': self.healthperson, 'sent_view': True})
        return context


class MessageOverview(PatientBaseView, TemplateView):
    '''
    Shows an overview of all messages of a patient
    '''
    template_name = 'messages/overview.html'

    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(MessageOverview, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessageOverview, self).get_context_data(**kwargs)
        messages = get_all_messages_for_patient(self.patient)

        messages = messages.select_related(
            'secretary__user',
            'healthprofessional__user',
            'patient__user')
        context.update({'rc_messages': messages, 'overview': True})
        return context


class MessageDetails(PatientBaseView, TemplateView):
    '''
    Shows the contents of a message to a patient
    '''
    template_name = 'messages/detail.html'

    @method_decorator(user_passes_test(
        is_allowed_patient, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(MessageDetails, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessageDetails, self).get_context_data(**kwargs)
        messages = get_all_messages_for_patient(self.patient)

        try:
            message = messages.get(pk=self.kwargs.get('message_id'))
        except RCMessage.DoesNotExist:
            raise Http404

        if not message.read_on:
            message.read_on = date.today()
            message.changed_by_user = self.request.user
            message.save()

        messages = messages.select_related(
            'secretary__user',
            'healthprofessional__user',
            'patient__user')

        context.update({'rc_messages': messages, 'message': message})
        return context

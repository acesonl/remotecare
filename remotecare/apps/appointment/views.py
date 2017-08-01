# -*- coding: utf-8 -*-
"""
Module containing a view for adding/editing appointments

:subtitle:`Class definitions:`
"""
from datetime import date
from django.template import loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from apps.utils.utils import send_sms_to_patient
from apps.questionnaire.models import QuestionnaireRequest
from apps.appointment.forms import AppointmentAddEditForm
from apps.rcmessages.models import RCMessage
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.patient.views import PatientBaseView
from apps.healthperson.utils import is_allowed_patient_admins, login_url
from django.contrib.auth.decorators import user_passes_test


class AppointmentEdit(PatientBaseView, FormView):
    '''
    Class based view for adding/editing appointment
    information by a secretary
    '''
    template_name = 'appointment/appointment_edit.html'
    form_class = AppointmentAddEditForm

    def render_sms_and_template(self, appointment, message_template,
                                sms_template):
        '''
        Renders both sms and template at once
        since the context is the same.

        Args:
            - appointment: the appointment instance
            - message_template: the template_name to load for the message
            - sms_template: the template_name to load for the sms

        Returns:
            [message_template, sms_template]
        '''
        current_date = date.today()

        context = {'patient': self.patient,
                   'questionnaire_request': self.questionnaire_request,
                   'current_date': current_date,
                   'secretary': self.secretary,
                   'appointment': appointment,
                   'is_male': self.patient.user.gender == 'male'}

        message_template = loader.get_template(message_template)
        sms_template = loader.get_template(sms_template)

        return [message_template.render(context, self.request),
                sms_template.render(context, self.request)]

    def get_default_urgent_message_and_sms(self, appointment):
        '''
        Renders both sms and template at once
        for urgent controls

        Args:
            - appointment: the appointment instance

        Returns:
            [message_template, sms_template]
        '''
        message_template = 'appointment/message/default_urgent_response.html'
        sms_template = 'appointment/sms/default_urgent_response.html'
        return self.render_sms_and_template(
            appointment, message_template, sms_template)

    def get_default_message_and_sms(self, appointment):
        '''
        Renders both sms and template at once
        for non-urgent controls

        Args:
            - appointment: the appointment instance

        Returns:
            [message_template, sms_template]
        '''
        message_template = 'appointment/message/default_response.html'
        sms_template = 'appointment/sms/default_response.html'
        return self.render_sms_and_template(
            appointment, message_template, sms_template)

    @method_decorator(user_passes_test(
        is_allowed_patient_admins, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.questionnaire_request = get_object_or_404(
            QuestionnaireRequest, id=self.kwargs.get(
                'questionnaire_request_id'))
        self.success_url = reverse('index')
        self.show_warning = False
        self.message_content = None
        self.sms_content = None
        self.secretary = self.request.user.healthperson
        return super(AppointmentEdit, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AppointmentEdit, self).get_form_kwargs()
        kwargs.update({'questionnaire_request': self.questionnaire_request,
                       'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AppointmentEdit, self).get_context_data(**kwargs)
        context.update({'show_warning': self.show_warning,
                        'questionnaire_request': self.questionnaire_request,
                        'message_content': self.message_content,
                        'sms_content': self.sms_content})
        return context

    def form_valid(self, form):
        '''
        Save the appointment and notify the patient
        of the planned appointment
        '''
        # check if appointment is within the requested period
        self.show_warning = False

        if ((form.cleaned_data['appointment_date'] >
             self.questionnaire_request.appointment_period_date)):
            self.show_warning = True

        if not self.show_warning or 'appointment_warning' in self.request.POST:
            appointment = form.save(commit=False)
            appointment.created_by = self.secretary
            appointment.questionnaire_request = self.questionnaire_request

            if self.questionnaire_request.urgent:
                rendered_templates = self.get_default_urgent_message_and_sms(
                    appointment)
            else:
                rendered_templates = self.get_default_message_and_sms(
                    appointment)

            [self.message_content, self.sms_content] = rendered_templates
            # Save message
            message = RCMessage()
            message.patient = self.patient
            message.secretary = self.secretary
            message.related_to = self.questionnaire_request
            message.internal_message = self.message_content

            # Sent sms
            send_sms_to_patient(self.patient, self.sms_content)

            self.questionnaire_request.appointment_added_on = date.today()
            self.questionnaire_request.appointment_added_by = self.secretary

            message.changed_by_user = self.request.user
            message.save()
            appointment.save()
            self.questionnaire_request.changed_by_user = self.request.user
            self.questionnaire_request.save()

            return super(AppointmentEdit, self).form_valid(form)

        return super(AppointmentEdit, self).get(
            self.request, *self.args, **self.kwargs)

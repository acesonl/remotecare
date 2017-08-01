# -*- coding: utf-8 -*-
"""
This module contains the views for displaying filled in
questionnaires and the start and finish questionnaire views.

The questionnaire fillin process is handled by the
:class:`apps.questionnaire.wizards.QuestionnaireWizard` view.

:subtitle:`Class and function definitions:`
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404

from apps.healthperson.patient.models import Patient
from apps.questionnaire.models import QuestionnaireRequest,\
    AVAILABLE_URGENT_QUESTIONNAIRE_LIST, RequestStep,\
    AVAILABLE_CONTROL_QUESTIONNAIRE_LIST
from apps.questionnaire.qohc.models import QOHCQuestionnaire
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator


# ## ADD QUESTIONNAIRE REQUEST ####
def insert_new_questionnaire_request_for_patient(patient):
    """
    Adds a new questionnaire request for a patient including
    the requeststeps

    Args:
        - patient: the patient to add the questionnaire_request for

    Returns:
        The created questionnaire_request
    """
    questionnaire_list = None
    for l in AVAILABLE_CONTROL_QUESTIONNAIRE_LIST:
        if l[0] == patient.diagnose:
            questionnaire_list = l[1]

    # questionnaire_list
    questionnaire_request = QuestionnaireRequest(patient=patient)
    questionnaire_request.deadline = date.today() + relativedelta(weeks=+1)
    questionnaire_request.deadline_nr = 1
    questionnaire_request.patient_diagnose = patient.diagnose
    questionnaire_request.practitioner = patient.current_practitioner
    # Added for auditing
    questionnaire_request.changed_by_user = patient.user
    questionnaire_request.save()

    # add steps of request.
    # Check if we need to add the QOHC questionnaire (=only asked once a year)
    do_add_QOHC = True

    try:
        QOHC_questionnaire = QOHCQuestionnaire.objects.filter(
            request_step__questionnairerequest__patient=patient).latest(
            'request_step__questionnairerequest__finished_on')
    except QOHCQuestionnaire.DoesNotExist:
        QOHC_questionnaire = None

    # QOHC needs to be filled in once a year,
    # check if a year has passed since the last one.
    if QOHC_questionnaire:
        if (((QOHC_questionnaire.finished_on + relativedelta(years=+1)) >
             date.today())):
            do_add_QOHC = False

    # add steps of request
    # if not in exclude_questionnaires list..
    step = 1
    for questionnaire in questionnaire_list:
        do_add = True
        if questionnaire == 'QOHCQuestionnaire':
            do_add = do_add_QOHC
        elif patient.excluded_questionnaires:
            if questionnaire in patient.excluded_questionnaires:
                    do_add = False
        if do_add:
            questionnaire_request_step = RequestStep()
            questionnaire_request_step.questionnairerequest =\
                questionnaire_request
            questionnaire_request_step.step_nr = step
            questionnaire_request_step.model = questionnaire
            step = step + 1
            questionnaire_request_step.save()

    return questionnaire_request


class PatientView(View):
    """Basic patient view which checks if the user
       has logged in and automatically sets the patient on the view"""
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.set_patient(**kwargs)
        return super(PatientView, self).dispatch(*args, **kwargs)

    def set_patient(self, **kwargs):
        """
        Sets the patient on the view
        """
        self.patient_session_id = kwargs.get('patient_session_id', None)
        # TODO: generate a custom error
        if self.patient_session_id not in self.request.session:
            raise Http404
        healthperson_ptr_id = self.request.session[self.patient_session_id][8:]
        self.patient = get_object_or_404(
            Patient, healthperson_ptr_id=healthperson_ptr_id)


class PatientTemplateView(PatientView, TemplateView):
    """
    Templateview baseclass view
    """
    pass


class PatientQuestionnaireTemplateView(PatientView, TemplateView):
    """
    Base view for all questionnaire views that use templateview.
    Sets the questionnaire_request on the view
    """
    def get_context_data(self, **kwargs):
        context = super(
            PatientQuestionnaireTemplateView, self).get_context_data(**kwargs)
        questionnaire_request_id = kwargs.get('questionnaire_request_id', None)
        self.questionnaire_request = get_object_or_404(
            QuestionnaireRequest, id=questionnaire_request_id)
        return context


class BaseOverviewTemplateView(PatientTemplateView):
    """
    Base view for overview views that show
    the details pages for filled in questionnaires
    Automatically adds the context.
    """

    def get_questionnaires_for(self, selected_model_class,
                               selected_questionnaire_request):
        """
        Retrieve the questionnaires coupled to the
        selected_questionnaire_request for the selected_model_class

        Args:
            - selected_model_class: the model_class to find the questionnaire\
              for
            - selected_questionnaire_request: the questionnaire_request which\
              should be coupled to the questionnaires.

        Returns:
            [The selected questionnaire, list of questionnaires]
        """
        # get the selected one based on the questionnaire_step
        qr_selected = selected_questionnaire_request
        select_disease_activity_questionnare =\
            selected_model_class.objects.get(
                request_step__questionnairerequest=qr_selected)

        # Get all
        disease_activity_questionnares =\
            selected_model_class.objects.filter(
                request_step__questionnairerequest__patient=self.patient,
                request_step__questionnairerequest__finished_on__isnull=False)

        return [select_disease_activity_questionnare,
                disease_activity_questionnares]

    def get_context(self):
        """
        Creates the context based on the questionnaire request
        and model_display_name adding various information.

        Returns:
            The context dict
        """
        questionnaire_requests = QuestionnaireRequest.objects.filter(
            patient=self.patient,
            finished_on__isnull=False).order_by('-finished_on')
        # default
        if 'qr' in self.request.GET:
            try:
                selected_questionnaire_request =\
                    QuestionnaireRequest.objects.get(
                        patient=self.patient,
                        finished_on__isnull=False,
                        id=int(self.request.GET['qr']))
            except QuestionnaireRequest.DoesNotExist:
                selected_questionnaire_request = None
        else:
            if questionnaire_requests.count() > 0:
                selected_questionnaire_request = questionnaire_requests[0]
            else:
                selected_questionnaire_request = None

        # Get the 'model_display_name' questionnaires and set the
        # selected one..
        select_disease_activity_questionnare = None
        disease_activity_questionnares = []

        selected_model_class = None

        if selected_questionnaire_request:
            questionnaire_all_steps =\
                selected_questionnaire_request.requeststep_set.all().order_by(
                    'step_nr')

            selected_model_class = None

            # Loop through the steps to find the questionnaire that
            # matches with 'model_display_name'
            for questionnaire_step in questionnaire_all_steps:
                questionnaire_model_class = questionnaire_step.model_class

                if ((questionnaire_model_class.display_name ==
                     self.model_display_name)):
                    selected_model_class = questionnaire_model_class

            # Get the selected questionnaire based on the selected_model_class
            # And the list of questionnaires for the plot of the values
            if selected_model_class:
                # get the selected one based on the questionnaire_step
                [select_disease_activity_questionnare,
                 disease_activity_questionnares] = self.get_questionnaires_for(
                    selected_model_class, selected_questionnaire_request)

        return {'patient': self.patient,
                'questionnaire_requests': questionnaire_requests,
                'selected_questionnaire_request':
                selected_questionnaire_request,
                'select_disease_activity_questionnaire':
                select_disease_activity_questionnare,
                'disease_activity_questionnaires':
                disease_activity_questionnares,
                'models1': selected_model_class}

    def get_context_data(self, **kwargs):
        context = super(BaseOverviewTemplateView,
                        self).get_context_data(**kwargs)
        context.update(self.get_context())
        return context


class DiseaseActivityOverview(BaseOverviewTemplateView):
    """Shows the disease activity overview page"""
    template_name = 'questionnaire/disease_activity.html'
    model_display_name = 'Ziekteactiviteit'


class QualityOfLifeOverview(BaseOverviewTemplateView):
    """Shows the quality of life overview page"""
    template_name = 'questionnaire/quality_of_life.html'
    model_display_name = 'Kwaliteit van leven'


class HealthcareQualityOverview(BaseOverviewTemplateView):
    """Shows the healthcare quality overview page"""
    template_name = 'questionnaire/healthcare_quality.html'
    model_display_name = 'Kwaliteit van zorg'


class QuestionnaireStartControle(PatientView):
    """
    Start page for normal (non urgent) controls.
    The view checks if there is a partially filled in
    control and let's the user finish it or redirects the user
    to the first step of the questionnaires fillin procedure.
    """
    def post(self, request, *args, **kwargs):
        self.set_patient(**kwargs)
        unfinished_questionnaire_requests =\
            QuestionnaireRequest.objects.filter(
                patient=self.patient, urgent=False, finished_on__isnull=True)
        unfinished_questionnaire_requests[0].delete()
        return HttpResponseRedirect(reverse('index'))

    def get(self, request, *args, **kwargs):
        self.set_patient(**kwargs)
        unfinished_questionnaire_requests =\
            QuestionnaireRequest.objects.filter(
                patient=self.patient, urgent=False, finished_on__isnull=True)
        add_new_questionnaire = False
        if len(unfinished_questionnaire_requests) > 1:
            # remove all
            unfinished_questionnaire_requests.delete()
            add_new_questionnaire = True
        elif len(unfinished_questionnaire_requests) == 1:
            # Check if unfinished questionnare is still
            # the correct one for the diagnose,
            # else remove it.
            if ((unfinished_questionnaire_requests[0].patient_diagnose !=
                 self.patient.diagnose)):
                unfinished_questionnaire_requests[0].delete()
                add_new_questionnaire = True

            elif unfinished_questionnaire_requests[0].saved_finish_later:
                questionnaire_request = unfinished_questionnaire_requests[0]
                fill_in_url = reverse(
                    'questionnaire_fillin',
                    args=[self.patient_session_id, questionnaire_request.id])

                if questionnaire_request.last_filled_in_form_step:
                    # add extra parameters for start position
                    step =\
                        int(questionnaire_request.last_filled_in_form_step) + 1
                    fill_in_url = "%s?step=%s" % (fill_in_url, step)

                context = {'fill_in_url': fill_in_url}
                return render_to_response(
                    'questionnaire/already_filled_in.html', context)
        else:
            # check if it is already time to fill in the controle..
            if self.patient.next_questionnaire_date:
                if self.patient.next_questionnaire_date > date.today():
                    # Not fill in now..
                    context = {'patient': self.patient}
                    return render_to_response(
                        'questionnaire/wait_till_next_questionnaire.html',
                        context)
            add_new_questionnaire = True

        if add_new_questionnaire:
            questionnaire_request =\
                insert_new_questionnaire_request_for_patient(self.patient)
        else:
            questionnaire_request = unfinished_questionnaire_requests[0]

        # if questionnaire_request.wizarddatabasestorage_set.count() > 0:
        #    print('SAVED DATA!! please check')
        #    #import ipdb; ipdb.set_trace()

        return HttpResponseRedirect(
            reverse(
                'questionnaire_fillin',
                args=[self.patient_session_id, questionnaire_request.id]))


class QuestionnaireStartUrgent(PatientView):
    """
    Start page for urgen controls.
    The view checks if there is a partially filled in
    control and let's the user finish it or redirects the user
    to the first step of the questionnaires fillin procedure.
    """
    def post(self, request, *args, **kwargs):
        unfinished_urgent_questionnaire_requests =\
            QuestionnaireRequest.objects.filter(patient=self.patient,
                                                finished_on__isnull=True,
                                                urgent=True)
        unfinished_urgent_questionnaire_requests[0].delete()
        return HttpResponseRedirect(reverse('index'))

    def get(self, request, *args, **kwargs):
        unfinished_urgent_questionnaire_requests =\
            QuestionnaireRequest.objects.filter(patient=self.patient,
                                                finished_on__isnull=True,
                                                urgent=True)
        # check if saved to complete later on, if so redirect
        if len(unfinished_urgent_questionnaire_requests) > 1:
            # remove all
            unfinished_urgent_questionnaire_requests.delete()
            add_new_questionnaire = True
        elif len(unfinished_urgent_questionnaire_requests) == 1:
            # Check if unfinished questionnare is still
            # the correct one for the diagnose,
            # else remove it.
            if ((unfinished_urgent_questionnaire_requests[0].
                 patient_diagnose != self.patient.diagnose)):
                unfinished_urgent_questionnaire_requests[0].delete()
                add_new_questionnaire = True
            elif ((unfinished_urgent_questionnaire_requests[0].
                   saved_finish_later)):
                questionnaire_request =\
                    unfinished_urgent_questionnaire_requests[0]
                fill_in_url = reverse(
                    'questionnaire_fillin',
                    args=[self.patient_session_id, questionnaire_request.id])

                if questionnaire_request.last_filled_in_form_step:
                    # add extra parameters for start position
                    step =\
                        int(questionnaire_request.last_filled_in_form_step) + 1
                    fill_in_url = "%s?step=%s" % (fill_in_url, step)

                context = {'fill_in_url': fill_in_url,
                     'urgent': True}
                return render_to_response(
                    'questionnaire/already_filled_in.html', context)
            else:
                # else remove
                unfinished_urgent_questionnaire_requests[0].delete()
                add_new_questionnaire = True
        else:
            add_new_questionnaire = True

        # Check if not an unhandled request..
        unhandled_urgent_questionnaire_requests =\
            QuestionnaireRequest.objects.filter(patient=self.patient,
                                                finished_on__isnull=False,
                                                handled_on__isnull=True,
                                                urgent=True)
        if len(unhandled_urgent_questionnaire_requests) > 0:
            context = {'urgent': True}
            return render_to_response(
                'questionnaire/unhandled_urgent.html', context)

        if add_new_questionnaire:
            # Should now be redirected or previous one is removed.
            # add new request with the correct steps included.

            questionnaire_list = None
            for item in AVAILABLE_URGENT_QUESTIONNAIRE_LIST:
                if item[0] == self.patient.diagnose:
                    questionnaire_list = item[1]

            # add questionnaire_request
            questionnaire_request = QuestionnaireRequest(patient=self.patient)
            questionnaire_request.urgent = True

            # already set to true so this does not need to be
            # set after the questionnaire has finished.
            questionnaire_request.appointment_needed = True
            questionnaire_request.patient_diagnose = self.patient.diagnose
            questionnaire_request.practitioner =\
                self.patient.current_practitioner
            questionnaire_request.changed_by_user = self.request.user
            questionnaire_request.save()

            # add steps for this questionnaire request.
            step_nr = 1
            for questionnaire in questionnaire_list:
                request_step = RequestStep()
                request_step.questionnairerequest = questionnaire_request
                request_step.step_nr = step_nr
                request_step.model = questionnaire
                request_step.save()
                step_nr = step_nr + 1

        # redirect to the fillin page
        return HttpResponseRedirect(
            reverse(
                'questionnaire_fillin',
                args=[self.patient_session_id, questionnaire_request.id]))


class QuestionnaireFinishedView(PatientQuestionnaireTemplateView):
    """
    Shows a succesfully finished all questionnaires view.
    Is both used for urgent and non urgent controls.
    """
    template_name = 'questionnaire/finish.html'

    def get_context_data(self, **kwargs):
        context = super(
            QuestionnaireFinishedView, self).get_context_data(**kwargs)

        # Get the current questionnaire step
        questionnaire_all_steps =\
            self.questionnaire_request.requeststep_set.all().order_by(
                'step_nr')

        # add all questionnaire step names, which are used
        # for displaying the menu(list) on the left
        questionnaire_step_names = []
        for questionnaire_step in questionnaire_all_steps:
            questionnaire_step_names.append(
                questionnaire_step.model_class.display_name
            )

        questionnaire_step_names.append('Afsluiting')
        context.update({
            'is_next_step': False,
            'previous_step_url': None, 'patient': self.patient,
            'questionnaire_request': self.questionnaire_request,
            'current_step_name': 'Afsluiting',
            'questionnaire_step_names': questionnaire_step_names,
            'startquestionnaire': None})
        return context


class QuestionnaireRequestRemove(PatientView):
    """
    View which allows to remove a questionnaire request.
    Used when canceling the control.
    """
    def dispatch(self, *args, **kwargs):
        questionnaire_request_id = kwargs.get(
            'questionnaire_request_id', None)
        self.questionnaire_request = get_object_or_404(
            QuestionnaireRequest, id=questionnaire_request_id)
        return super(
            QuestionnaireRequestRemove, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.questionnaire_request.delete()
        return HttpResponse('succes')

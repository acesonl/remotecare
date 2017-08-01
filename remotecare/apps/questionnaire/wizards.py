# -*- coding: utf-8 -*-
"""
This module contains the subclassed WizardView which
allows filling in a list of forms.

The wizard uses a :class:`apps.questionnaire.storage.DatabaseStorage` instance
to store the filled in information.

In short the wizard uses the following internal procedure for displaying forms
and saving data:

    1. The wizard view is called with a questionnaire_request.id.
       The corresponding questionnaire_request is used to get the associated
       requeststeps. From these steps the models are used to get the full
       list of forms for the wizard.
    2. By using the step queryparameter (or by default the first step) the
       corresponding form is selected to be rendered. From the storage the
       cleaned data or unclean data is used to initialize the form with data.
    3. After an HTML post the form is checked for validation. If it validates
       the clean_data is saved as cleaned-data, else it is stored as
       unclean data.
    4. When the last form has been posted all clean data is retrieved from
       the storage instance and used to initalize & save instances of the
       models which are coupled to the forms.

:subtitle:`Class definitions:`
"""

from datetime import date
from django import forms
from django.utils import six
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from formtools.wizard.views import WizardView
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDict
from collections import OrderedDict as SortedDict
from core.forms import FormDateField, ChoiceOtherField

from apps.healthperson.patient.models import Patient
from apps.questionnaire.forms import get_forms_for
from apps.questionnaire.models import QuestionnaireRequest
from django.forms import formsets

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class NoFileStorageConfigured(Exception):
    pass


class QuestionnaireWizard(WizardView):
    """
    Questionnaire Wizard view class Used for all questionnaires
    """

    storage_name = 'apps.questionnaire.storage.DatabaseStorage'
    condition_dict = {}
    # We need to init with one instance
    # is automatically overriden later on
    step_forms = {}

    # temporary form_list so the superclass does not raise an error
    form_list = []

    @classmethod
    def get_initkwargs(cls, form_list=None, initial_dict=None,
                       instance_dict=None, condition_dict=None,
                       *args, **kwargs):

        kwargs.update({
            'initial_dict': initial_dict or kwargs.pop(
                'initial_dict', getattr(cls, 'initial_dict', None)) or {},
            'instance_dict': instance_dict or kwargs.pop(
                'instance_dict', getattr(cls, 'instance_dict', None)) or {},
            'condition_dict': condition_dict or kwargs.pop(
                'condition_dict', getattr(cls, 'condition_dict', None)) or {}
        })

        kwargs['form_list'] = []

        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestionnaireWizard, self).dispatch(*args, **kwargs)

    def init_form_list(self, form_list):
        """
        Re-executes the below code after the form_list is updated
        with the forms based on the models coupled to the questionnaires
        for the questionnaire_request

        Args:
           -form_list: the list of forms

        Returns:
            The computed form list which is dict of forms with a\
            zero based counter
        """
        # As in the get_init_kwargs of the WizardView class
        computed_form_list = SortedDict()

        assert len(form_list) > 0, 'at least one form is needed'

        # walk through the passed form list
        for i, form in enumerate(form_list):
            if isinstance(form, (list, tuple)):
                # if the element is a tuple, add the tuple to the new created
                # sorted dictionary.
                computed_form_list[six.text_type(form[0])] = form[1]
            else:
                # if not, add the form with a zero based counter as unicode
                computed_form_list[six.text_type(i)] = form

        # walk through the new created list of forms
        for form in six.itervalues(computed_form_list):
            if issubclass(form, formsets.BaseFormSet):
                # if the element is based on BaseFormSet (FormSet/ModelFormSet)
                # we need to override the form variable.
                form = form.form
            # check if any form contains a FileField, if yes, we need a
            # file_storage added to the wizardview (by subclassing).
            for field in six.itervalues(form.base_fields):
                if (isinstance(field, forms.FileField) and
                        not hasattr(self, 'file_storage')):
                    raise NoFileStorageConfigured(
                        "You need to define 'file_storage' in your "
                        "wizard view in order to handle file uploads.")

        # build the kwargs for the wizardview instances
        return computed_form_list

    def strip_initial_data(self, step, posted_data):
        """
        Helper function for stripping posted data to
        be usable as initial_data

        Args:
            - step: the step key
            - posted_data: the posted_data in dict form

        Returns:
            The initial data based on the post_data
        """
        # If the value is not for a m2m field, strip the
        # [] array brackets.
        form = self.form_list[step]
        m2m_field_names = [field.name for field in
                           form.Meta.model._meta.many_to_many]

        prefix_str = '{0}-'.format(step)
        initial = {}
        for key in posted_data:
            value = posted_data[key]
            new_key = key
            if key.startswith(prefix_str):
                new_key = key[len(prefix_str):]
                initial.update({new_key: value})
            if new_key not in m2m_field_names:
                if type(value) == list and len(value) == 1:
                    initial.update({new_key: value[0]})

        return initial

    def get_form_initial(self, step):
        """
        Get the initial data to initialize the form with

        Args:
            - step: is the step key

        Returns:
            The initial data for a form based on the step key
        """
        unclean_data = self.storage.get_unclean_data(step)
        if unclean_data:
            # Strip/fix the unclean posted data to be used as initial data
            return self.strip_initial_data(step, unclean_data)

        return self.initial_dict.get(step, {})

    def get_prefix(self, *args, **kwargs):
        """
        The questionnaire_request_id is used as prefix
        for storing data in the storage instance

        .. note:: This is not really necessary since the storage instance
                  is also coupled to the questionnaire_request
        """
        return self.kwargs.get('questionnaire_request_id')

    def init_forms(self, request, *args, **kwargs):
        """
        Initialize the form_list by getting all forms for the models
        for each request_step coupled to the questionnaire_requests

        Args:
            - request: the request instance
        """
        patient_session_id = self.kwargs.get('patient_session_id')

        # TODO: raise custom error (session timeout)
        if patient_session_id not in self.request.session:
            raise Http404

        healthperson_ptr_id = self.request.session[patient_session_id][8:]
        self.patient = get_object_or_404(
            Patient, healthperson_ptr_id=healthperson_ptr_id)

        self.questionnaire_request = self.storage.questionnaire_request
        # added line for auditing
        self.questionnaire_request.changed_by_user = self.request.user

        self.questionnaire_all_steps =\
            self.questionnaire_request.requeststep_set.all().order_by(
                'step_nr')

        # list of all forms
        all_forms = []

        # list of form numbers per step
        self.step_forms = {}

        index = 0
        for questionnaire_step in self.questionnaire_all_steps:
            questionnaire_model_class = questionnaire_step.model_class
            current_step_forms = get_forms_for(questionnaire_model_class)
            all_forms = all_forms + current_step_forms

            self.step_forms.update(
                {questionnaire_step.model:
                 list(range(index, len(current_step_forms) + index))})
            index = index + len(current_step_forms)

        # SET the form_list
        self.form_list = self.init_form_list(all_forms)

    def get_form_list(self):
        """
        Override of the baseclass method
        to insert custom condition testing on the forms.

        Returns:
            A list of forms exluding the forms for which the condition returns
            False
        """
        if not hasattr(self, 'cached_form_list'):
            form_list = SortedDict()
            for form_key, form_class in six.iteritems(self.form_list):
                form_instance = self.get_form(form_key)
                condition = form_instance.condition(self)
                if condition:
                    form_list[form_key] = form_class

            self.cached_form_list = form_list
        return self.cached_form_list

    def post(self, request, *args, **kwargs):
        """
        Processes the post_data when a form is posted, is also called when
        the next or back button or save_and_exit is clicked. Allows saving
        partially filled (invalid) forms.

        Args:
            - request: the request instance

        Returns:
            The response of the post method of the superclass
        """
        self.init_forms(request, *args, **kwargs)

        save_and_exit = self.request.POST.get('save_and_exit', None)
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)

        if save_and_exit or wizard_goto_step:
            # Save changes in the current form when the 'back' button
            # or save & exit button has been pressed
            # get the form for the current step
            form = self.get_form(
                data=self.request.POST, files=self.request.FILES)
            # and try to validate
            if form.is_valid():
                # if the form is valid, store the cleaned data and files.
                self.storage.set_step_data(
                    self.steps.current,
                    self.process_step(form))
                self.storage.set_step_files(
                    self.steps.current,
                    self.process_step_files(form))
                self.storage.set_unclean_data(self.steps.current, None)
            else:
                # Save the unclean data
                # DateField and ChoiceOtherFields require
                # special treatment of the POST data.
                post_dict = MultiValueDict(self.request.POST)
                for l in form.fieldsets():
                    for field in l[1]:
                        field_name = '{0}-{1}'.format(form.prefix, field.name)
                        if ((isinstance(field.field, FormDateField) or
                             isinstance(field.field, ChoiceOtherField))):
                            field.field.fix_value_from_post(post_dict,
                                                            field_name)
                self.storage.set_step_data(self.steps.current, None)
                self.storage.set_step_files(self.steps.current, None)
                self.storage.set_unclean_data(self.steps.current, post_dict)

        if save_and_exit:
            # redirect to the homepage
            if not self.questionnaire_request.saved_finish_later:
                self.questionnaire_request.saved_finish_later = True
                self.questionnaire_request.save()
            return HttpResponseRedirect(reverse('index'))

        return super(QuestionnaireWizard, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        The get function either loads the first form or
        the form corresponding to the step querystring parameter

        Args:
            - request: the request instance

        Returns:
            The response of the render_goto_step function
        """
        self.init_forms(request, *args, **kwargs)
        # Don't ever reset the storage!
        # self.storage.reset()

        if 'step' in request.GET:
            # Check if the step is not higher than the last step
            # and is part of the possible forms.
            step = request.GET['step']
            last_step = len(self.form_list) - 1
            if int(step) > last_step:
                step = str(last_step)
            if int(step) < 0:
                step = '0'
            if step not in self.form_list:
                raise Http404
            self.storage.current_step = step
        else:
            # reset the current step to the first step.
            self.storage.current_step = self.steps.first

        return self.render_goto_step(self.storage.current_step)

    def get_form_kwargs(self, step=None):
        """
        Adds the patient as default kwargs

        Args:
            - step: the step key (default = None)

        Returns:
            A form kwargs dict.
        """
        return {'patient': self.patient}

    def process_step(self, form):
        """
        Processes a valid form step by returning the data
        and remove unclean_data if present. This function
        is called in the post method.

        Args:
            - form: the form to process

        Returns:
            The form step data for the given form
        """
        model_name = form.Meta.model._meta.object_name
        current_questionnaire_step =\
            self.questionnaire_request.requeststep_set.get(model=model_name)
        questionnaire_step = current_questionnaire_step.step_nr

        # save last filled_in_step and form_step
        if self.questionnaire_request.last_filled_in_step:
            if ((str(questionnaire_step) >
                 self.questionnaire_request.last_filled_in_step)):
                self.questionnaire_request.last_filled_in_step =\
                    questionnaire_step
        else:
            self.questionnaire_request.last_filled_in_step =\
                questionnaire_step

        if self.questionnaire_request.last_filled_in_form_step:
            if ((int(self.steps.current) >
                 int(self.questionnaire_request.last_filled_in_form_step))):
                self.questionnaire_request.last_filled_in_form_step =\
                    self.steps.current
        else:
            self.questionnaire_request.last_filled_in_form_step =\
                self.steps.current

        if not self.questionnaire_request.saved_finish_later:
            self.questionnaire_request.saved_finish_later = True

        self.questionnaire_request.save()

        # make sure the unclean_data is removed for this step
        self.storage.set_unclean_data(self.steps.current, None)

        return self.get_form_step_data(form)

    def get_template_names(self):
        """
        Returns:
            The default wizard template name
        """
        return 'questionnaire/fillin2.html'

    def get_cleaned_data_for_form_class(self, form_class):
        """
        Helper function for getting the cleaned_data for a form class

        Args:
            - form_class: the form_class to get the cleaned_data for

        Returns:
            The cleaned data for the form step or None
        """
        for index in self.form_list:
            if self.form_list[index] == form_class:
                return self.get_cleaned_data_for_step(index)
        return None

    def get_context_data(self, form, **kwargs):
        """
        Adds extra context data for rendering the template

        Args:
            - form: the form to include and get the context for

        Returns:
            A dict with the context to use for rendering the template
        """
        context = super(QuestionnaireWizard, self).get_context_data(
            form=form, **kwargs)

        # add all questionnaire step names, which are used for
        # displaying the menu(list) on the left
        questionnaire_steps = []
        for questionnaire_step in self.questionnaire_all_steps:
            questionnaire_steps.append(
                {'name':
                 questionnaire_step.model_class.display_name,
                 'first_step': self.step_forms[questionnaire_step.model][0]})
        questionnaire_steps.append({'name': 'Afsluiting'})

        # self.init_forms(self.request, None, **kwargs)
        current_form = self.form_list[self.steps.current]
        current_step_name = current_form.Meta.model.display_name
        model_name = current_form.Meta.model._meta.object_name
        current_questionnaire_steps = self.step_forms[model_name]

        # Check if there is a previous questionnaire
        startquestionnaire = None
        try:
            last_questionnaire_request = QuestionnaireRequest.objects.filter(
                patient=self.patient,
                urgent__isnull=True,
                finished_on__isnull=False).latest('finished_on')
            if last_questionnaire_request:
                # get the first == startquestionnaire
                startquestionnaire =\
                    self.questionnaire_request.requeststep_set.all().order_by(
                        'step_nr')[0]
        except QuestionnaireRequest.DoesNotExist:
            last_questionnaire_request = None

        first_step_data = {}
        # initial data of first_step
        for step in self.step_forms[self.questionnaire_all_steps[0].model]:
            data = self.storage.get_step_data(u'{0}'.format(step))
            if data:
                data = self.strip_initial_data(u'{0}'.format(step), data)
                first_step_data.update(data)

        # Remove wizard current_step
        if 'current_step' in first_step_data:
            del first_step_data['current_step']

        model_class = self.questionnaire_all_steps[0].model_class
        initial_data = model_class(**first_step_data)

        form_list = self.get_form_list()
        form_key_list = []
        for key in form_list:
            form_key_list.append(key)

        context.update({'patient': self.patient,
                        'questionnaire_request': self.questionnaire_request,
                        'questionnaire_steps': questionnaire_steps,
                        'current_questionnaire_steps':
                        current_questionnaire_steps,
                        'current_step_name': current_step_name,
                        'form_key_list': form_key_list,
                        'startquestionnaire': startquestionnaire,
                        'initial_data': initial_data})
        return context

    def done(self, form_list, **kwargs):
        """
        Save all gathered data and redirect to the finished page
        Called when the all forms are valid and the last form is posted.

        Args:
            - form_list: the list with all processed forms

        Returns:
            Redirect to 'finished url'
        """
        questionnaire_all_steps =\
            self.questionnaire_request.requeststep_set.all().order_by(
                'step_nr')

        for questionnaire_step in questionnaire_all_steps:
            questionnaire_model_class = questionnaire_step.model_class
            kwargs = {'request_step': questionnaire_step}

            # Collect clean_data excluding many_to_many fields
            for form in form_list:
                if ((form.Meta.model._meta.object_name ==
                     questionnaire_step.model)):
                    kwargs.update(form.cleaned_data)
                    # Remove m2m, will be picked up below
                    for field in questionnaire_model_class._meta.many_to_many:
                        if field.name in kwargs:
                            del kwargs[field.name]

            # Initialize the instance with kwargs and save
            questionnaire_instance = questionnaire_model_class(**kwargs)
            # added line for auditing
            questionnaire_instance.changed_by_user = self.request.user
            questionnaire_instance.save()

            # Save m2m data
            for form in form_list:
                if ((form.Meta.model._meta.object_name ==
                     questionnaire_step.model)):
                    cleaned_data = form.cleaned_data
                    for field in questionnaire_model_class._meta.many_to_many:
                        if field.name in cleaned_data:
                            object_manager = getattr(
                                questionnaire_instance, field.name)
                            for obj in cleaned_data[field.name]:
                                object_manager.add(obj)

        # Note: storage is made empty automatically
        self.questionnaire_request.finished_on = date.today()
        self.questionnaire_request.save()

        patient_session_id = self.kwargs.get('patient_session_id')
        url = reverse(
            'questionnaire_finish',
            args=[patient_session_id, self.questionnaire_request.id])

        return HttpResponseRedirect(url)

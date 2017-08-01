# -*- coding: utf-8 -*-
"""
Contains questionnaire tests. By default only tests the
wizard questionnaire processes only for one diagnose. But all other forms
are tested seperately.

:subtitle:`Class definitions:`
"""
import json
from apps.questionnaire.models import QuestionnaireRequest, get_model_class
from core.serializers import AllFieldsSerializer
from core.unittest.baseunittest import BaseUnitTest
from apps.questionnaire.forms import get_forms_for
from django.core.urlresolvers import reverse


class MockWizard:
    """
    Mock Wizard object with a method for
    getting the cleaned_data
    """
    cleaned_data = {}

    def get_cleaned_data_for_form_class(self, form_class):
        """
        Get the cleaned data for a form_class

        Args:
            The form_class, unused

        Returns:
            self.cleaned_data
        """
        return self.cleaned_data


class QuestionnaireTest(BaseUnitTest):
    """
    Provides tests for testing Questionnaires
    """
    fixtures = ['test_data/test_users.json', ]
    data = None
    wizard = MockWizard()
    posted_data = {}

    def questionnaire_post_form(self, res, url, status_code=200,
                                save_and_exit=False, previous_step=False):
        """
        Post a questionnaire form

        Args:
            - res: the response instance
            - url: the url to post to
            - status_code: the expected status_code (default=200)
            - save_and_exit: perform a save and exit the questionnaire
            - previouse_step: if True go one step back

        Returns:
            The response instance after posting
        """
        form = res.context_data['form']

        obj_deserialized = self.objects[form.Meta.model]
        if obj_deserialized.object._state.adding:
            obj_deserialized.save()
        obj = obj_deserialized.object

        form1 = form.__class__(instance=obj)

        post_data = self.get_post_data(form1, form.prefix + '-')

        if previous_step:
            # Remove one value, so form is not valid for testing
            # = saving unclean data
            del post_data[post_data.keys()[0]]

        current_step =\
            res.context_data['wizard'][
                'management_form'].initial['current_step']
        post_data.update(
            {res.context_data['wizard']['management_form'].prefix +
             '-current_step': current_step})

        if save_and_exit:
            post_data.update({'save_and_exit': 'save_and_exit'})
        elif previous_step:
            post_data.update(
                {'wizard_goto_step': res.context_data['wizard']['steps'].prev})

        # save posted data
        self.posted_data.update({current_step: post_data})

        res = self.post(url, post_data, check_status_code=False)

        if save_and_exit:
            self.assertEqual(res.status_code, 302)
        elif previous_step:
            old_step = current_step
            current_step =\
                res.context_data['wizard'][
                    'management_form'].initial['current_step']
            self.assertEqual(res.status_code, 200)
            self.assertEqual(int(current_step), int(old_step) - 1)
        else:

            if res.status_code == 200:
                current_step = res.context_data[
                    'wizard']['management_form'].initial['current_step']

                if res.context_data['form'].errors != {}:
                    import ipdb
                    ipdb.set_trace()

                self.assertEqual(res.context_data['form'].errors, {})
        return res

    def run_questionnaire(self, urgent=False):
        """
        Runs a complete set of questionnaires for an
        urgent or normal control

        Args:
            - urgent: run the urgent control
        """
        res = self.get('/')
        patient = res.context_data['patient']
        session_key = self.get_session_key(patient.health_person_id)

        url = '/patient/' + session_key + '/questionnaire/start_{0}/'

        if urgent:
            controle = 'urgent'
        else:
            controle = 'controle'

        res = self.get(url.format(controle), 302)
        url = res.url
        res = self.get(url)

        while not res.status_code == 302:
            res = self.questionnaire_post_form(res, url)

        # get finish page
        res = self.get(res.url)

    def get_questionnaire_fields_from_object(self, obj):
        """
        Gets the questionnaire fields from a given questionnaire instance

        Args:
            - obj: the Questionnaire instance

        Returns:
            - All fields from the obj
        """
        # Since Django serializer does not work with model inheritance
        serializer = AllFieldsSerializer()
        field_names = [x.name for x in obj._meta.get_fields()]
        # Remove #####_ptr fields to super models
        if obj._meta.parents != {}:
            for key in obj._meta.parents:
                field_names.remove(obj._meta.parents[key].name)

        serializer.serialize([obj], fields=field_names)
        fields = serializer.getvalue()[0]['fields']

        del fields['request_step']
        del fields['id']

        return fields

    def run_questionnaire_for_patient(self, email, urgent=False):
        """
        Runs a full control for a patient

        Args:
            - email: the email to use for login
            - urgent: if true run it for an urgent control
        """
        self.login(email)
        if not self.data:
            self.data = self.load_data('test_data/test_data.json')

        # Run through the questionnaire process
        self.run_questionnaire(urgent)

        # test if saved correctly in database
        questionnaire_request = QuestionnaireRequest.objects.latest('pk')

        for rq_step in questionnaire_request.requeststep_set.all().order_by(
                'step_nr'):
            saved_fields = self.get_questionnaire_fields_from_object(
                rq_step.questionnaire)
            obj = self.objects[rq_step.questionnaire.__class__].object
            test_fields = self.get_questionnaire_fields_from_object(obj)

            # Check if field is same stored as in the test dataset
            self.assertEqual(test_fields, saved_fields)

    def check_form(self, form_class):
        """
        Check some default form methods for a given form_class

        Args:
            - form_class: the form_class to check
        """
        # initialize without data
        form = form_class()
        obj_deserialized = self.objects[form.Meta.model]
        if obj_deserialized.object._state.adding:
            obj_deserialized.save()
        obj = obj_deserialized.object

        # initalize with data
        form1 = form.__class__(instance=obj)
        # Check if condition function works
        form1.condition(self.wizard)
        # Run clean method
        form1.cleaned_data = self.get_questionnaire_fields_from_object(obj)
        form1.clean()

    def check_other_forms(self):
        """
        Run over all other (untested) questionnaire forms by
        initializing, cleaning and checking the 'condition' function
        """
        self.wizard.cleaned_data.update(
            {'hasproblems': 'no',
             'has_stoma': 'yes'})

        if not self.data:
            self.data = self.load_data('test_data/test_data.json')

        questionnaire_models = ['QOLChronCUQuestionnaire',
                                'QOLQuestionnaire',
                                'IBDQuestionnaire']

        for questionnaire_model in questionnaire_models:
            questionnaire_model_class = get_model_class(questionnaire_model)
            form_classes = get_forms_for(questionnaire_model_class)

            for form_class in form_classes:
                self.check_form(form_class)

    def check_controle_process(self):
        """
        To speed up testing only do the whole control and urgent control
        for one patient. All other forms that are not hit by this test
        are tested in the 'check_other_forms' function

        Currently testes the following diagnoses:
            colitis_ulcerosa (= same as chron), intestinal_transplantation,
            rheumatoid_arthritis
        """
        to_test = [
            'frank@example.com',  # rheumatoid_arthritis
            'jeffrey@example.com',  # colitis_ulcerosa
            'hobart@example.com',  # intestinal_transplantation
        ]
        for email in to_test:
            self.run_questionnaire_for_patient(email)

        for email in to_test:
            self.run_questionnaire_for_patient(email, urgent=True)

    def check_controle_navigation(self, urgent):
        """
        Partially fill in control and check the navigation functionality +
        save partially filled in & return
        """
        self.login('frank@example.com')

        # Reset the posted_data store
        self.posted_data = {}

        if not self.data:
            self.data = self.load_data('test_data/test_data.json')

        res = self.get('/')
        patient = res.context_data['patient']

        session_key = self.get_session_key(patient.health_person_id)
        start_url = '/patient/' + session_key + '/questionnaire/start_{0}/'

        if urgent:
            controle = 'urgent'
        else:
            controle = 'controle'

        # create start_url
        start_url = start_url.format(controle)

        # Delete one via the view
        questionnaire = QuestionnaireRequest.objects.first()
        if questionnaire:
            self.post(
                reverse(
                    'questionnaire_request_remove',
                    args=[session_key, questionnaire.id]),
                {},
                status_code=200)

        # Delete all request for this test
        QuestionnaireRequest.objects.all().delete()

        res = self.get(start_url, 302)
        url = res.url
        res = self.get(url)

        # Post some forms
        for i in range(1, 3):
            res = self.questionnaire_post_form(res, url)

        # Go back one step
        res = self.questionnaire_post_form(res, url, previous_step=True)

        # Save and exit
        res = self.questionnaire_post_form(res, url, save_and_exit=True)

        # Check saved unclean data
        questionnaire = QuestionnaireRequest.objects.latest('pk')
        storage = questionnaire.wizarddatabasestorage_set.all()[0]
        data = json.loads(storage.data)

        # Loop through saved posted_data and compare to
        # stored json data (which is also posted_data)
        for key in self.posted_data:
            for item in self.posted_data[key]:
                if data['step_data'][key]:
                    data_item = data['step_data'][key][item]
                    test_item = self.posted_data[key][item]
                    self.assertIn(str(test_item), data_item)

        # Check unclean data is stored for step 2
        for key in data['unclean_data']:
            for item in data['unclean_data'][key]:
                data_item = data['unclean_data'][key][item]
                test_item = self.posted_data[key][item]
                self.assertIn(str(test_item), data_item)

        # relaunch the questionnaire
        res = self.get(start_url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('fill_in_url', res.context)

        # Link into current questionnaire form
        res = self.get(res.context['fill_in_url'])

        current_step =\
            res.context_data['wizard'][
                'management_form'].initial['current_step']

        # Check if we are in step 2
        self.assertEqual(current_step, '2')

        # Check if the initial data is set from the unclean_data
        prefix = res.context['form'].prefix
        for key in res.context_data['form'].initial:
            test_item = res.context_data['form'].initial[key]
            item = prefix + '_' + key
            if item in data['unclean_data'][prefix]:
                data_item = data['unclean_data'][prefix][item]
                self.assertIn(str(test_item), data_item)

        # delete the questionnaire
        res = self.post(start_url, {})

    def test_controles(self):
        """
        Questionnaire tests runner
        """
        self.check_controle_process()
        # self.check_other_forms()
        self.check_controle_navigation(urgent=False)
        self.check_controle_navigation(urgent=True)

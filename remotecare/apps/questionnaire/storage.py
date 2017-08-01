# -*- coding: utf-8 -*-
"""
This module contains a storage model definition used by
:class:`apps.questionnaire.wizards.QuestionnaireWizard` to temporarily
store all filled in information from the questionnaires.

:subtitle:`Class definitions:`
"""
import json
from formtools.wizard import storage
from django.utils.datastructures import MultiValueDict
from apps.questionnaire.models import WizardDatabaseStorage,\
    QuestionnaireRequest
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404


class DatabaseStorage(storage.BaseStorage):
    """
    Wizard database storage class
    stores the temporary data of a wizard in a
    database instead of the session or a cookie
    """
    # use the DjangoJSONEncoder for supporting date encoding.
    encoder = DjangoJSONEncoder(separators=(',', ':'))
    # key for storing unclean_data for a form
    unclean_data_key = 'unclean_data'

    def __init__(self, *args, **kwargs):
        """Init by loading the data or initializing the
           dictionairy"""
        # Questionnaire_request_id is first argument
        questionnaire_request_id = int(args[0])
        super(DatabaseStorage, self).__init__(*args, **kwargs)
        self.questionnaire_request = get_object_or_404(
            QuestionnaireRequest, id=questionnaire_request_id)
        self.data = self.load_data()
        if self.data is None:
            self.init_data()

    def init_data(self):
        """
        Override the method to
        append the unclean_data key
        """
        self.data = {
            self.step_key: None,
            self.step_data_key: {},
            self.step_files_key: {},
            self.extra_data_key: {},
            self.unclean_data_key: {},
        }

    def get_unclean_data(self, step):
        """
        Get the unclean data for a step

        Args:
            - step: the step key

        Returns:
            The values in dict format
        """
        # When reading the serialized data, upconvert it to a MultiValueDict,
        # some serializers (json) don't preserve the type of the object.
        values = self.data[self.unclean_data_key].get(step, None)
        if values is not None:
            values = MultiValueDict(values)
        return values

    def set_unclean_data(self, step, unclean_form_data):
        """
        Set the unclean data for a step

        Args:
            - step: The step key to set the unclean_data for
            - unclean_form_data: the unclean data from a form
        """
        if unclean_form_data:
            if isinstance(unclean_form_data, MultiValueDict):
                unclean_form_data = dict(unclean_form_data.lists())
            else:
                unclean_form_data = dict(unclean_form_data)
        else:
            unclean_form_data = {}

        # remove some unwanted values which are posted
        # automatically
        to_strip_list = ['csrfmiddlewaretoken',
                         'submit',
                         '{0}-current_step'.format(self.prefix),
                         'save_and_exit',
                         'wizard_goto_step']

        for to_strip in to_strip_list:
            if to_strip in unclean_form_data:
                del unclean_form_data[to_strip]

        self.data[self.unclean_data_key][step] = unclean_form_data

    def load_data(self):
        """
        Load the data from the database

        Returns:
            A dict with the loaded data
        """
        try:
            self.wizard_database_storage = WizardDatabaseStorage.objects.get(
                questionnaire_request=self.questionnaire_request)
        except WizardDatabaseStorage.DoesNotExist:
            self.wizard_database_storage = None
            return None

        return json.loads(self.wizard_database_storage.data,
                          cls=json.JSONDecoder)

    def update_response(self, response):
        """
        Stores the data, automatically called before
        the response is sent to the client

        Args:
            - response: the response instance
        """
        if not self.wizard_database_storage:
            self.wizard_database_storage, c =\
                WizardDatabaseStorage.objects.get_or_create(
                    questionnaire_request=self.questionnaire_request)
        self.wizard_database_storage.data = self.encoder.encode(self.data)
        self.wizard_database_storage.save()

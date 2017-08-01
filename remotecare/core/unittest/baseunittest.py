# -*- coding: utf-8 -*-
"""
Module providing a baseclass for unittests based on 'TestCase'
"""
import json
from django.conf import settings
from django.core import mail, serializers
from django.test import TestCase
from core.forms import DateField, ChoiceOtherField


class BaseUnitTest(TestCase):  # pragma: no cover
    """
    Base unit test based on TestCase
    includes functions for loading json data and
    automatically filling in forms by initializing forms
    with instances and retrieving the post_data from them.
    """
    data = {}
    objects = {}

    def reset_stores(self):
        """
        Reset/empty the mailbox and SMS store
        """
        mail.outbox = []
        settings.SMS_STORE = []

    @property
    def SMS_STORE(self):
        """
        Returns:
            The sms_store which is an array containing
            all catched SMS messages
        """
        return settings.SMS_STORE

    @property
    def mail_outbox(self):
        """
        Returns:
            The mail outbox which contains all catched
            outgoing e-mails
        """
        return mail.outbox

    def load_data(self, file_name, user_data=False):
        """
        Loads the data into self.object using file_name
        """
        # load json data
        with open(file_name, 'r') as f:
            data = json.load(f)

        objects = {}
        if not user_data:
            with open(file_name, 'r') as f:
                for obj in serializers.deserialize('json', f):
                    obj_class = obj.object.__class__
                    if obj_class not in objects:
                        objects.update({obj_class: obj})
                    else:
                        array = objects[obj_class]
                        if not isinstance(array, list):
                            array = [array]
                        array = array + [obj]
                        objects[obj_class] = array
        self.objects = objects

        unpacked_values = [(x['model'], x['fields']) for x in data]
        rt = {}
        for (model_name, fields) in unpacked_values:
            if model_name not in rt:
                rt.update({model_name: fields})
            else:
                array = rt[model_name]
                if not isinstance(array, list):
                    array = [array]

                array = array + [fields]
                rt[model_name] = array
        return rt

    def get(self, url, status_code=200, check_status_code=True):
        """
        Shortcut for self.client.get(url)
        Automatically checks for a proper status_code (200)
        """
        # Get an URL
        response = self.client.get(url)
        if check_status_code:
            self.assertEqual(response.status_code, status_code)
        return response

    def get_fields_of_form(self, form):
        """
        Returns:
            array of all the fields in the fieldset definition
            for form param
        """
        # Get the fields of a form
        fields = []
        for fieldset in form.fieldsets():
            fields += fieldset[1]
        return fields

    def get_post_data(self, form, prefix=''):
        """
        Returns:
            a dictionairy with post_data based on what is
            set as initial on the given form.
        """
        # Retrieve the post data based on a filled in form
        fields = self.get_fields_of_form(form)
        post_data = {}

        last_date_field_value = None

        for field in fields:
            if isinstance(field.field, DateField):
                date = field.value()
                if date:
                    post_data.update(
                        {prefix + field.html_name + '_year': date.year})
                    post_data.update(
                        {prefix + field.html_name + '_month': date.month})
                    post_data.update(
                        {prefix + field.html_name + '_day': date.day})
                    last_date_field_value = date
            elif isinstance(field.field, ChoiceOtherField):
                found = True
                try:
                    [x for (x, y) in field.field.choices].index(field.value())
                except ValueError:
                    found = False

                select_value = field.value()
                textarea_value = ''

                if not found:
                    select_value = 'other'
                    textarea_value = field.value()

                post_data.update(
                    {prefix + field.html_name + '_0': select_value})
                post_data.update(
                    {prefix + field.html_name + '_1': textarea_value})
            elif field.name == 'date_unknown':
                if not last_date_field_value:
                    post_data.update(
                        {prefix + field.html_name: field.value()})
            else:
                post_data.update(
                    {prefix + field.html_name: field.value()})
        return post_data

    def post_form(self, url, initial=None, instance=None, extra_data={},
                  check_status_code=True):
        """
            Automatic post a form by calling an url and getting the form
            from the returned response.context

            Args:
                - url: the url containing the form
                - initial: the initial values to set on the form
                - instance: the instance to set on the form.
                - extra_data: extra data to inlucde into the post_data
                - check_status_code: check the response.code? (default=302)

            Returns:
                the response object
        """
        res = self.get(url)
        form = res.context['form']

        if initial:
            form1 = form.__class__(initial=initial)
        else:
            form1 = form.__class__(instance=instance)

        prefix = ''
        if form.prefix:
            prefix = form.prefix + '-'

        post_data = self.get_post_data(form1, prefix)
        post_data.update(extra_data)

        return self.post(url, post_data, check_status_code=check_status_code)

    def get_session_key(self, value):
        """
           This method can be used to get the session_key for a
           healthperson.id

           Returns: The session key for the given value.
        """
        # Get the session_key of a healthperson
        value = 'storage_' + str(value)
        index = list(self.client.session.values()).index(value)
        key = list(self.client.session.keys())[index]
        return key

    def post(self, url, post_data, status_code=302, check_status_code=True):
        """
            Shortcut function for posting data

            Args:
                - url: the url to post to
                - post_data: the post_data to sent
                - status_code: the status_code to check for (default=302)
                - check_status_code: check the status_code? (default=true)

            Returns:
                the response object
        """
        # Post data
        response = self.client.post(url, post_data)
        if check_status_code:
            self.assertEqual(response.status_code, status_code)
        return response

    def get_model_instance_by_class(self, model_class, to_strip=None):
        """
            Shortcut function for getting a model instance from the
            loaded test data based on the model_class.

            Args:
                - model_class: the class of the model to search for
                - to_strip: optional fields that need to be stripped\
                            (currently not used)

            Returns:
                the deserialized instance from the test data
        """
        # Get a model instance from self.objects based on model_class
        deserialized_object = self.objects[model_class]
        instance = deserialized_object.object
        m2m_data = deserialized_object.m2m_data

        # fix m2m by overriding property on model class with a dict
        for item in m2m_data:
            to_set = []
            model = getattr(model_class, item).field.related.parent_model
            for pk in m2m_data[item]:
                to_set.append(model.objects.get(pk=int(pk)))
            to_set = {'all': to_set}
            setattr(model_class, item, to_set)
        return instance

    def login(self, email, password='remotecare', sms_code='1234',
              do_sms_code='0'):
        """
            Shortcut function for logging in a user


            Args:
                - email: the email address to use
                - password: the password to use (default=remotecare)
                - sms_code: the sms code to use (default=1234)
                - do_sms_code: 0 means do not use

            .. Note::
               In test modus the SMS_STORE is used to simulate
               the normal procedure of sms authentication.

            Returns:
                the reponse
        """
        # Do login
        self.reset_stores()
        self.get('/login/')
        res = self.post('/login/',
                        {'username': email,
                         'password': password,
                         'do_sms_code': do_sms_code})
        # if res.status_code == 200:
        #    import ipdb; ipdb.set_trace()

        if len(self.SMS_STORE) > 0:
            sms_code = self.SMS_STORE[0]['message']
        res = self.post(
            '/smscode/', {'sms_code': sms_code},
            check_status_code=False)

        res.get(res.url)
        return res

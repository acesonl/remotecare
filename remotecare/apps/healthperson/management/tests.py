# -*- coding: utf-8 -*-
"""
This module contains tests which can be performed by a manager.
Since the manager has access to all add/edit/remove user functionality
these functions are all tested here.

:subtitle:`Class definitions:`
"""
from datetime import date
from django.core.urlresolvers import reverse
from core.unittest.baseunittest import BaseUnitTest
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.healthperson.patient.models import Patient
from apps.healthperson.secretariat.models import Secretary
from apps.lists.models import Hospital


class ManagementTest(BaseUnitTest):
    """
    Provides the tests performed by a logged in manager
    """
    fixtures = ['test_data/test_users.json', ]

    def check_search(self, url, post_data, context_key, full_name):
        """
        Check the default search page for different search criteria

        Args:
            - url: the url to open
            - post_data: the data to post to that url
            - context_key: the key to look voor in the context after posting
            - full_name: the full_name of the user that should be found

        Returns:
            The response after posting the data
        """
        res = self.get(url)
        res = self.post(url, post_data, status_code=200)

        self.assertEqual(len(res.context[context_key]), 1)
        self.assertEquals(
            res.context[context_key][0].user.full_name,
            full_name)
        return res

    def check_personalia(self):
        """
        Checks the personalia view/edit pages of the manager
        """
        res = self.get('/')
        session_key = self.get_session_key(
            res.context_data['manager'].health_person_id)
        base_url = '/management/' + session_key + '/'
        res = self.get(base_url + 'view/personalia/')
        res = self.get(base_url + 'edit/personalia/')

        prefix = ''
        if res.context['form'].prefix:
            prefix = res.context['form'].prefix

        post_data = self.get_post_data(res.context['form'], prefix)

        if 'title' in post_data and post_data['title'] in (None,):
            del post_data['title']

        post_data.update({'change_password': 'yes',
                          'password': 'RemoTecare12',
                          'password2': 'RemoTecare12'})

        # Check with changing password
        res = self.post(
            base_url + 'edit/personalia/',
            post_data, check_status_code=False)

        post_data.update({'password': None,
                          'password2': None})
        del post_data['change_password']

        # Check without changing password
        res = self.post(base_url + 'edit/personalia/', post_data)

        # Check if login works with new password
        self.login('john@example.com', 'RemoTecare12')

    def check_healthperson_pages(self, base_url, view_edit_pages):
        """
        Check edit pages for different user types,
        try to post with default values that are retrieved with a 'get'
        request.

        Args:
            - base_url: the base_url to build up the url to call
            - view_edit_pages: a list of parts of urls to use to get\
                the view and post the edit page.
        """
        for page in view_edit_pages:
            self.get(base_url + '/view/' + page + '/')
            res = self.get(base_url + '/edit/' + page + '/')

            prefix = ''
            if res.context['form'].prefix:
                prefix = res.context['form'].prefix
            post_data = self.get_post_data(res.context['form'], prefix)

            if page == 'personalia':
                post_data.update(
                    {'change_password': 'yes',
                     'password': 'RemoTecare12',
                     'password2': 'RemoTecare12'})

            temp_post_data = {}

            for item in post_data:
                if post_data[item] is not None:
                    temp_post_data.update({item: post_data[item]})
            post_data = temp_post_data

            if 'photo_location' in post_data:
                del post_data['photo_location']

            res = self.post(
                base_url + '/edit/' + page + '/',
                post_data,
                check_status_code=False)

        res = self.get(base_url + '/remove/')

    def check_secretary_pages(self, secretary):
        """
        Check the pages accessible by a manager for a secretary

        Args:
            - secretary: the secretary to check the pages for
        """
        session_key = self.get_session_key(secretary.health_person_id)
        self.check_healthperson_pages(
            '/secretariat/' + session_key,
            ['personalia', ])

    def check_healthprofessional_pages(self, healthprofessional):
        """
        Check the pages accessible by a manager for a healthprofessional

        Args:
            - healthprofessional: the healthprofessional to check\
              the pages for
        """
        session_key = self.get_session_key(
            healthprofessional.health_person_id)
        self.check_healthperson_pages(
            '/healthprofessional/' + session_key,
            ['personalia', 'notification', 'out_of_office', 'photo'])

    def check_patient_pages(self, patient):
        """
        Check the pages accessible by a manager for a patient

        Args:
            - patient: the patient to check the pages for
        """
        session_key = self.get_session_key(patient.health_person_id)
        self.check_healthperson_pages(
            '/patient/' + session_key,
            ['personalia', 'control_frequency'])

    def add_new_patient(self):
        """
        Try adding a new patient
        """
        self.reset_stores()
        url = reverse('patient_add')

        self.get(url)

        initial = {
            'BSN': 'A1234567B',
            'local_hospital_number': 'A1234567B',
            'hospital': Hospital.objects.all()[0],
            'title': 'mr',
            'first_name': 'test',
            'last_name': 'Tester',
            'initials': 'T.A.',
            'prefix': 'van der',
            'gender': 'male',
            'date_of_birth': date(1975, 4, 12),
            'mobile_number': '0612345678',
            'mobile_number2': '0612345678',
            'email': 'test_tester@example.com',
            'email2': 'test_tester@example.com',
            'diagnose': 'chron',
            'current_practitioner': 2,
            'regular_control_frequency': '3_months',
            'blood_sample_frequency': '6_months',
            'always_clinic_visit': 'alwaysclinicvisit'}

        res = self.post_form(url, initial, check_status_code=False)
        res = self.get(res.url)

        # Check e-mail sent to test_tester@example.com
        # The link in the e-mail is checked in the reset
        # password procedure test
        self.assertEqual(len(self.mail_outbox), 1)
        self.assertEqual(self.mail_outbox[0].to, ['test_tester@example.com'])

        # We need to set the instance instead of the id
        initial['current_practitioner'] = HealthProfessional.objects.get(id=2)
        patient = res.context_data['patient']

        # Check if fields are saved correctly
        for key in initial:
            if hasattr(patient, key):
                self.assertEqual(getattr(patient, key), initial[key])
            if hasattr(patient.user, key):
                self.assertEqual(getattr(patient.user, key), initial[key])

    def add_new_healthprofessional(self):
        """
        Try adding a new healthprofessional
        """
        self.reset_stores()
        url = reverse('healthprofessional_add')

        res = self.get(url)

        initial = {
            'title': 'ms',
            'first_name': 'test1',
            'last_name': 'Tester1',
            'initials': 'T.A.1',
            'prefix': 'van',
            'gender': 'female',
            'date_of_birth': date(1980, 12, 31),
            'mobile_number': '0612345679',
            'mobile_number2': '0612345679',
            'email': 'test_tester1@example.com',
            'email2': 'test_tester1@example.com',
            'specialism': 'surgery',
            'telephone': '050-3049231',
            'function': 'specialist'}

        res = self.post_form(url, initial)
        res = self.get(res.url)

        # Check e-mail sent to test_tester@example.com
        # The link in the e-mail is checked in the reset
        # password procedure test
        self.assertEqual(len(self.mail_outbox), 1)
        self.assertEqual(self.mail_outbox[0].to, ['test_tester1@example.com'])

        healthprofessional = res.context_data['healthprofessional']

        # Check if fields are saved correctly
        for key in initial:
            if hasattr(healthprofessional, key):
                self.assertEqual(
                    getattr(healthprofessional, key),
                    initial[key])
            if hasattr(healthprofessional.user, key):
                self.assertEqual(
                    getattr(healthprofessional.user, key),
                    initial[key])

    def add_new_secretary(self):
        """
        Try adding a new secretary
        """
        self.reset_stores()
        url = reverse('secretariat_add')

        res = self.get(url)

        initial = {
            'title': 'ms',
            'first_name': 'test2',
            'last_name': 'Tester2',
            'initials': 'T.A.2',
            'prefix': '',
            'gender': 'female',
            'date_of_birth': date(1990, 1, 1),
            'mobile_number': '0612345672',
            'mobile_number2': '0612345672',
            'email': 'test_tester2@example.com',
            'email2': 'test_tester2@example.com',
            'specialism': 'orhopedie'}

        res = self.post_form(url, initial)
        res = self.get(res.url)

        # Check e-mail sent to test_tester@example.com
        # The link in the e-mail is checked in the reset
        # password procedure test
        self.assertEqual(len(self.mail_outbox), 1)
        self.assertEqual(self.mail_outbox[0].to, ['test_tester2@example.com'])

        secretary = res.context_data['secretary']

        # Check if fields are saved correctly
        for key in initial:
            if hasattr(secretary, key):
                self.assertEqual(
                    getattr(secretary, key),
                    initial[key])
            if hasattr(secretary.user, key):
                self.assertEqual(
                    getattr(secretary.user, key) if getattr(secretary.user, key) else '',
                    initial[key])

    def remove_healthprofessional(self, healthprofessional):
        """
        Remove an healthprofessional
        """
        session_key = self.get_session_key(healthprofessional.health_person_id)
        self.post(reverse('healthprofessional_remove',
                          args=[session_key]),
                  {})

        healthprofessional =\
            HealthProfessional.objects.get(pk=healthprofessional.id)

        self.assertEqual(healthprofessional.user.is_active, False)
        self.assertNotEqual(healthprofessional.user.deleted_on, None)

    def remove_patient(self, patient):
        """
        Remove a patient
        """
        session_key = self.get_session_key(patient.health_person_id)
        self.post(reverse('patient_remove',
                          args=[session_key]),
                  {})

        patient =\
            Patient.objects.get(pk=patient.id)

        self.assertEqual(patient.user.is_active, False)
        self.assertNotEqual(patient.user.deleted_on, None)

    def remove_secretary(self, secretary):
        """
        Remove a secretary
        """
        session_key = self.get_session_key(secretary.health_person_id)
        self.post(reverse('secretariat_remove',
                          args=[session_key]),
                  {})

        secretary =\
            Secretary.objects.get(pk=secretary.id)

        self.assertEqual(secretary.user.is_active, False)
        self.assertNotEqual(secretary.user.deleted_on, None)

    def test_management(self):
        """
        Manager checks runner, performs all check definitions.
        """
        self.login('john@example.com')

        # Check patient search
        post_data = {
            'last_name': 'davis', 'BSN': '1234567890',
            'local_hospital_number': '1234567890',
            'date_of_birth_day': 2, 'date_of_birth_month': 1,
            'date_of_birth_year': 1997}

        # Search patient
        res = self.check_search(
            '/patient/search/',
            post_data, 'patients', 'Frank Davis')

        # basic check of patient pages
        self.check_patient_pages(res.context['patients'][0])

        # Check healthprofessional search
        post_data = {
            'last_name': 'smith', 'first_name': 'gerald',
            'function': 'specialist', 'specialism': 'surgery'}

        # Search healthprofessional
        res = self.check_search(
            '/healthprofessional/search/',
            post_data, 'healthprofessionals', 'Gerald Smith')

        # Basic check of healthprofessional pages
        self.check_healthprofessional_pages(
            res.context['healthprofessionals'][0])

        # Check secretary search
        post_data = {'last_name': 'dunn', 'specialism': 'rheumatology'}

        # Search secretary
        res = self.check_search(
            '/secretariat/search/',
            post_data, 'secretariat', 'Jim Dunn')

        # Basic check of secretary pages
        self.check_secretary_pages(res.context['secretariat'][0])

        # Check own personalia view/edit pages
        self.check_personalia()

        # Check adding a new patient
        self.add_new_patient()

        # Check adding a new healthprofessional
        self.add_new_healthprofessional()

        # Check adding a new secretary
        self.add_new_secretary()

        # Check removing healthprofessional
        # DO THESE CHECKS AS LAST

        # Search & remove healthprofessional
        post_data = {
            'last_name': 'smith', 'first_name': 'gerald',
            'function': 'specialist', 'specialism': 'surgery'}
        res = self.check_search(
            '/healthprofessional/search/',
            post_data, 'healthprofessionals', 'Gerald Smith')
        self.remove_healthprofessional(res.context['healthprofessionals'][0])

        # Search & remove patient
        post_data = {
            'last_name': 'davis', 'BSN': '1234567890',
            'local_hospital_number': '1234567890',
            'date_of_birth_day': 2, 'date_of_birth_month': 1,
            'date_of_birth_year': 1997}
        res = self.check_search(
            '/patient/search/',
            post_data, 'patients', 'Frank Davis')
        self.remove_patient(res.context['patients'][0])

        # Search & remove secretary
        post_data = {'last_name': 'dunn', 'specialism': 'rheumatology'}
        res = self.check_search(
            '/secretariat/search/',
            post_data, 'secretariat', 'Jim Dunn')
        self.remove_secretary(res.context['secretariat'][0])

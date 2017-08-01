# -*- coding: utf-8 -*-
"""
Definitions for tests for secretary.
Currently only includes tests for checking the search page

:subtitle:`Class definitions:`
"""
from core.unittest.baseunittest import BaseUnitTest
from apps.healthperson.patient.models import Patient


class SecretaryTest(BaseUnitTest):
    """
    Test the search function on the homepage
    """
    fixtures = ['test_data/test_users.json']

    def check_search(self):
        """
        Check homepage search for patients
        """
        search_terms = ['Davis', '2-1-1997', '1234567894']
        for search_term in search_terms:
            res = self.post(
                '/search/',
                {'searchterm': search_term},
                check_status_code=False)
            self.assertEqual(len(res.context_data['patients']), 1)

    def test_secretary_functions(self):
        """
        Run the checks for a secretary

        .. Note:: testing adding/editing appointments is\
                  included into the appointments app
        """
        self.login('jim@example.com')

        # Make patient.user BSN unique
        user = Patient.objects.all()[0].user
        user.BSN = '1234567894'
        user.changed_by_user = user
        user.save()

        # Do checks
        self.check_search()

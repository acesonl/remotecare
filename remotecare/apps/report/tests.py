# -*- coding: utf-8 -*-
"""
Test the complete procedure of handling a filled in control by
a healthprofessional.

:subtitle:`Class definitions:`
"""
import cgi
from core.unittest.baseunittest import BaseUnitTest
from apps.report.forms import report_black_list
from apps.report.models import Report
from apps.rcmessages.models import RCMessage


class ReportTest(BaseUnitTest):
    '''
    Test the report functionality by adding
    a report & message for a controle
    and an urgent controle
    '''
    fixtures = ['test_data/test_users.json',
                'test_data/report_repost_data.json']

    def report_for_controle(self, questionnaire, urgent=False):
        '''
        Test runner which tries to create a report, message
        and finishes the handling of a control

        Args:
            - questionnaire: the questionnaire_request to use for testing
            - urgent: test the urgent control or default control procedure.
        '''
        report_count = Report.objects.count()
        message_count = RCMessage.objects.count()

        questionnaire_id = str(questionnaire.id)
        session_key = self.get_session_key(
            questionnaire.patient.health_person_id)

        url_base = '/patient/' + session_key +\
            '/report/' + questionnaire_id + '/'

        # check view pages for status_code == 200
        res = self.get(url_base + 'view_questionnaire/')
        for nr, questionnaire in enumerate(res.context_data['questionnaires']):
            res = self.get(
                url_base + 'view_questionnaire/?questionnaire=' + str(nr))

        # check passing wrong values does not give error
        res = self.get(
            url_base + 'view_questionnaire/?questionnaire=foo')

        res = self.get(url_base + 'view_report/')

        # Step 1: create report
        if not urgent:
            report_edit_url = 'edit_report/'
        else:
            report_edit_url = 'urgent_edit_report/'

        res = self.get(url_base + report_edit_url)
        report = res.context['form'].initial['report']

        # replace the mandatory items
        for item in report_black_list:
            report = report.replace(item, 'TestData')

        # need to escape e in patient
        report = cgi.escape(report).encode('ascii', 'xmlcharrefreplace')

        post_data = {'report': report}
        if not urgent:
            post_data.update({'sent_to_doctor': ''})

        res = self.post(url_base + report_edit_url, post_data)
        res = self.get(res.url)

        self.assertEquals(
                res.context_data['report'].report.replace('\n', ''),
                report.replace('\n', ''))

        # open edit again to see if edit view is working correctly
        self.get(url_base + report_edit_url)

        # Check docx and pdf exports
        self.get(url_base + 'docx_report/')
        self.get(url_base + 'pdf_report/')

        res = self.get(url_base + 'view_message/')

        # Step 2: create message
        res = self.get(url_base + 'edit_message/')
        internal_message = res.context['form'].initial['internal_message']

        # replace the mandatory items
        for item in report_black_list:
            internal_message = internal_message.replace(item, 'TestData')

        # need to escape e in patient
        internal_message = cgi.escape(internal_message).encode(
            'ascii', 'xmlcharrefreplace')

        res = self.post(url_base + 'edit_message/',
                        {'internal_message': internal_message})

        res = self.get(res.url)

        # check saved correctly
        self.assertEquals(
            res.context_data['rc_message'].internal_message.replace('\n', ''),
            internal_message.replace('\n', ''))

        # open edit view again to see if editing message works
        self.get(url_base + 'edit_message/')

        # Step 3: finish
        res = self.get(url_base + 'finish/')
        res = self.post(url_base + 'finish/', {})

        # Check saved
        self.assertEquals(Report.objects.count(), report_count + 1)
        self.assertEquals(RCMessage.objects.count(), message_count + 1)

    def test_report(self):
        '''
        Test a report for a normal control
        and a urgent control
        '''
        self.login('gerald@example.com')

        res = self.get('/')
        self.report_for_controle(res.context['controles'][0])
        self.report_for_controle(
            res.context['urgent_patient_controles'][0], True)

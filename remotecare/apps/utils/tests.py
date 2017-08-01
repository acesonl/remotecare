# -*- coding: utf-8 -*-
"""
This module contains tests for the export functionality
and the functions in utils that are not covered by other tests
in Remote Care.

:subtitle:`Class definitions:`
"""
import cStringIO
import pyPdf
from django.test import TestCase
from django.test import RequestFactory
from apps.utils.docxhelper import render_to_DocX
from apps.utils.pdf import render_to_PDF
from apps.account.models import User, EncryptionKey
from datetime import datetime
from docx import opendocx, getdocumenttext
from core.encryption.random import randomid


class Exports(TestCase):
    '''
    Test class for testing docX & PDF export
    '''
    def get_request(self):
        """
        Generate a fake request

        Returns:
            A fake request instance
        """
        request_factory = RequestFactory()
        request = request_factory.get('/')
        key = EncryptionKey(key=randomid())
        key.save()
        user = User()
        user.personal_encryption_key = key
        user.first_name = 'John'
        user.last_name = 'Walker'
        user.email = 'john@example.com'
        user.date_of_birth = datetime.now()
        user.disable_auditing = True
        user.save()
        request.user = user

        return request

    def get_source(self):
        """
        Get the HTML source to test

        Returns:
            The HTML source to test with
        """
        return '<html><body><p>Test paragraph</p><p>Test1<br/>' +\
               'Test2</br>&euml;&nbsp;<b>bold</b><i>italic</i>' +\
               '<u>underlined</u></p></body></html>'

    def test_docx(self):
        """
        Test the DocX export functionality
        """
        source = self.get_source()
        request = self.get_request()

        response = render_to_DocX(request, source)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/docx')

        # open file and checks contents
        resultFile = cStringIO.StringIO(response.content)
        document = opendocx(resultFile)
        paratextlist = getdocumenttext(document)

        # Make explicit unicode version
        newparatextlist = []
        for paratext in paratextlist:
            newparatextlist.append(paratext.encode("utf-8"))

        index1 = newparatextlist[0].index('Remote Care')
        newparatextlist[0] = newparatextlist[0][index1:]

        # Hardcoded test string
        to_test = [
            'Remote Care, Gebruiker: John Walker, \n        Test paragraph',
            'Test1\nTest2\n\xc3\xab bolditalicunderlined'
        ]

        # remove date so contents can be tested
        index1 = newparatextlist[0].index('Datum')
        index2 = newparatextlist[0].index('\n', index1)

        newparatextlist[0] =\
            newparatextlist[0][0:index1] + newparatextlist[0][index2:]

        self.assertEquals(to_test, newparatextlist)

    def test_pdf(self):
        """
        Test the PDF export functionality
        """
        source = self.get_source()
        request = self.get_request()

        response = render_to_PDF(request, source)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/pdf')

        resultFile = cStringIO.StringIO(response.content)
        pdf = pyPdf.PdfFileReader(resultFile)
        text = []
        for page in pdf.pages:
            text.append(page.extractText())

        # Hardcoded test string
        to_test = [
            u' Remote Care   Gebruiker: John Walker   \nDit document' +
            u' is strikt vertrouwelijk en mag niet door derden worden' +
            u' ingezien of worden verspreid.\nTest paragraph\nTest1\n' +
            u'Test2\n\xeb bolditalicunderlined\n'
        ]

        index1 = text[0].index('Datum')
        index2 = text[0].index('\n')

        text[0] = text[0][0:index1] + text[0][index2:]
        self.assertEquals(to_test, text)

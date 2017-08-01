# -*- coding: utf-8 -*-
"""
This module contains classes and functions for generating
DocX documents from HTML used for exporting reports.

:subtitle:`Function definitions:`
"""
from datetime import datetime
import cStringIO
from django.http import HttpResponse
from docx import paragraph, relationshiplist, nsprefixes, newdocument,\
    coreproperties, savedocx, contenttypes, appproperties, websettings,\
    wordrelationships
from HTMLParser import HTMLParser
from django.template import loader


class HTMLToDocXParser(HTMLParser):
    '''
    Class for parsing HTML to Docx
    '''

    # accepted styles
    styles = ('b', 'i', 'u')
    current_style = ''
    current_data = ''
    body = None
    current_paragraph = []

    def set_body(self, body):
        """
        Initalize the DocX document by setting the body

        Args:
            - body: the DocX body
        """
        self.body = body
        self.current_paragraph = []
        self.current_data = ''
        self.current_style = ''

    def handle_starttag(self, tag, attrs):
        """
        Handles a starttag in the HTML. Converts a predefined list of
        tags to the corresponding DocX definitions.

        Args:
            - tag: the name of the HTML tag
            - attr: optional attrs coupled to the HTML tag
        """
        if tag in self.styles and tag not in self.current_style:
            if self.current_data not in (None, ''):
                self.current_paragraph.append(
                    (self.current_data, str(self.current_style)))
                self.current_data = ''

            self.current_style = self.current_style + tag

        if tag == 'p' and self.current_paragraph != []:  # pragma: no cover
            self.current_paragraph.append(
                (self.current_data, str(self.current_style)))
            self.body.append(paragraph(self.current_paragraph))
            self.current_paragraph = []

    def handle_endtag(self, tag):
        """
        Handles a endtag in the HTML. Converts a predefined list of
        tags to the corresponding DocX definitions:

        Args:
            - tag: the name of the HTML tag
        """
        if tag == 'br':
            self.current_data = self.current_data + '\n'

        if tag == 'p':
            self.open_paragraph = False
            if self.current_paragraph != []:
                self.current_paragraph.append(
                    (self.current_data, str(self.current_style)))
                self.body.append(paragraph(self.current_paragraph))
                self.current_paragraph = []
            else:
                if self.current_data not in (None, ''):
                    self.current_paragraph.append(
                        (self.current_data, str(self.current_style)))
                    self.body.append(paragraph(self.current_paragraph))
                    self.current_paragraph = []
            self.current_data = ''

        if tag in self.styles and tag in self.current_style:
            self.current_paragraph.append(
                (self.current_data, str(self.current_style)))
            self.current_data = ''
            self.current_style = self.current_style.replace(tag, '')

    def handle_data(self, data):
        """
        Adds text to the DocX document

        Args:
            - data: the data/text to add to the document
        """
        self.current_data = self.current_data + data

    def handle_entityref(self, name):
        """
        Handle special HTML entities

        Args:
            - name: the name of the HTML entity
        """
        if name == 'nbsp':
            data = ' '
        else:
            data = self.unescape('&' + name + ';')
        self.current_data += data


def convertHtmlToDocX(sourceHtml):
    '''
    Wrapper function for converting HTML to DocX

    Args:
        - sourceHtml: the HTML to convert

    Returns:
        A response instance with the DocX document included
    '''
    resultFile = cStringIO.StringIO()
    relationships = relationshiplist()
    document = newdocument()
    body = document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]

    parser = HTMLToDocXParser()
    parser.set_body(body)
    parser.feed(sourceHtml)

    title = 'Remote care DocX export'
    subject = ''
    creator = 'Remote Care'
    keywords = ['']

    coreprops = coreproperties(title=title, subject=subject, creator=creator,
                               keywords=keywords)

    savedocx(
        document, coreprops,
        appproperties(), contenttypes(),
        websettings(),
        wordrelationships(relationships),
        resultFile
    )

    response = HttpResponse(
        resultFile.getvalue(),
        content_type='application/docx'
    )
    response['Content-Disposition'] =\
        'attachment; filename="remote_care_export.docx"'

    return response  # HttpResponse(sourceHtml)


def render_to_DocX(request, body):
    '''
    Shortcut function for rendering
    the HTML template and create DocX

    Args:
        - request: the initial request
        - body: the body with the text to be exported

    Returns:
        A response instance with the DocX document included
    '''
    template_name = 'utils/export/default_docx.html'
    template = loader.get_template(template_name)
    context = {
        'username': request.user.full_name,
        'date': datetime.today().strftime("%d %B %Y %H:%M:%S"),
        'body': body}

    return convertHtmlToDocX(template.render(context, request))

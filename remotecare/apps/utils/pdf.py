# -*- coding: utf-8 -*-
"""
This module contains the functions for converting HTML to PDF.

:subtitle:`Function definitions:`
"""
from datetime import datetime
import cStringIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template import loader


# Utility function
def convertHtmlToPdf(sourceHtml):
    """
    Converts the HTML to PDF

    Args:
        - sourceHtml: the HTML (string) to convert

    Returns:
        An HttpResponse instance with the PDF included or an HttpResponse\
        instance with the HTML included.
    """
    # open output file for writing (truncated binary)
    resultFile = cStringIO.StringIO()

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
        sourceHtml,                # the HTML to convert
        dest=resultFile)           # file handle to recieve result

    # return True on success and False on errors

    if not pisaStatus.err:
        return HttpResponse(
            resultFile.getvalue(),
            content_type='application/pdf'
        )
    else:  # pragma: no cover
        # if we are somehow unable to generate
        # the pdf: show the page in html instead.
        # that way, we can still print it out via the browser.
        return HttpResponse(sourceHtml)


def render_to_PDF(request, body):
    '''
    Shortcut for rendering the HTML template and create PDF

    Args:
        - request: the initial request
        - body: the body to include in the PDF in HTML format

    Returns:
        An HttpResponse instance with the PDF included or an HttpResponse\
        instance with the HTML included.
    '''
    template_name = 'utils/export/default_pdf.html'
    template = loader.get_template(template_name)
    context = {
        'username': request.user.full_name,
        'date': datetime.today().strftime("%d %B %Y %H:%M:%S"),
        'body': body}
    return convertHtmlToPdf(template.render(context, request))

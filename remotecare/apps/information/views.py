# -*- coding: utf-8 -*-
"""
Class based view definitions for showing information
and submitting feedback

:subtitle:`Class definitions:`
"""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from apps.information.forms import FeedBackAddEditForm
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

# White list the pages
TEMPLATES = {
    'security': 'information/security.html',
    'overview': 'information/overview.html',
    'behandeling': 'information/behandeling.html',
    'onstaan-en-werking': 'information/over_ziekte.html',
    'wetenschappelijk-nieuws': 'information/wetenschappelijknieuws.html',
    'diagnose-en-onderzoeken': 'information/diagnose.html',
    'e-consult': 'information/e-consult-demo.html',
    'faq': 'information/faq.html',
    'onderwerpen-lijst': 'information/onderwerpen_lijst.html',
    'over-remote-care': 'information/over_remote_care.html',
    'zoeken': 'information/zoeken.html'}


class BaseInformationPageView(TemplateView):
    '''
    Basic view for information based template views
    accepts a list of templates and picks the correct
    template based on the page parameter
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.page = kwargs.get('page', None)
        if self.page not in self.template_list:
            raise Http404
        self.template_name = self.template_list[self.page]
        return super(BaseInformationPageView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            BaseInformationPageView,
            self).get_context_data(
            **kwargs)
        context.update({'submenu': self.page})
        return context


class InformationPageView(BaseInformationPageView):
    '''
    Information page view class, used for displaying
    all kinds of information in Remote Care
    '''
    template_list = TEMPLATES


class AboutSecurityView(TemplateView):
    '''
    Shows a page with information about security
    '''
    # No login required
    template_name = 'information/over_beveiliging.html'

    def get_context_data(self, **kwargs):
        context = super(AboutSecurityView, self).get_context_data(**kwargs)
        context.update({'submenu': 'over_beveiliging'})
        return context


class InformationFeedBack(FormView):
    '''
    Feedback form class, e-mails feedback to info@example.com
    '''
    template_name = 'information/feedback.html'
    form_class = FeedBackAddEditForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(InformationFeedBack, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InformationFeedBack, self).get_context_data(**kwargs)
        context.update({'submenu': 'feedback'})
        return context

    def send_feedback_email(self, email_content):
        """
        Sent a feedback email to info@example.com by default
        """
        subject, from_email, to =\
            'Remote Care - feedback', 'remotecare@example.com', 'info@example.com'

        # this strips the html, so people will have the text as well.
        text_content = strip_tags(email_content)

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(email_content, "text/html")
        msg.send()

    def form_valid(self, form):
        """
        Sent feedback and redirect user
        """
        self.success_url = reverse('information_feedback_sent')
        email_content = '{0}<br/>User-id:{1}'.format(
            form.cleaned_data['feedback'],
            self.request.user.id)
        self.send_feedback_email(email_content)
        return super(InformationFeedBack, self).form_valid(form)


class InformationFeedbackSentView(TemplateView):

    '''
    Shows a feedback has been succesfully sent page
    '''
    template_name = 'information/feedback_sent.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(
            InformationFeedbackSentView,
            self).dispatch(
            *args,
            **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            InformationFeedbackSentView,
            self).get_context_data(
            **kwargs)
        context.update({'submenu': 'feedback'})
        return context

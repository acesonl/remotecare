# -*- coding: utf-8 -*-
"""
This module contains all views used by a manager.

:subtitle:`Class definitions:`
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from apps.healthperson.management.forms import ProfileEditForm
from django.utils.translation import ugettext_lazy as _
from apps.healthperson.utils import is_allowed_manager, login_url

from apps.healthperson.healthprofessional.models import HealthProfessional,\
    SPECIALISM_CHOICES
from apps.healthperson.secretariat.models import Secretary
from apps.account.models import User

from core.encryption.hash import create_hmac
from django.conf import settings

from apps.base.views import BaseIndexTemplateView
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator
from core.views import FormView


class ManagerBaseView(View):
    """
    Base class for manager views, automatically
    add manager to view
    """
    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.set_manager()
        return super(ManagerBaseView, self).dispatch(*args, **kwargs)

    def set_manager(self):
        """Add the manager to the view"""
        self.manager = self.request.user.healthperson

    def get_context_data(self, **kwargs):
        context = super(ManagerBaseView, self).get_context_data(**kwargs)
        context.update({'manager': self.manager})
        return context


class ManagerIndexView(ManagerBaseView, BaseIndexTemplateView):
    """Manager homepage view"""
    template_name = 'management/index.html'


class ManagerPersonaliaView(ManagerBaseView, TemplateView):
    """Manager personalia view"""
    template_name = 'management/personalia_view.html'


class SearchView(ManagerBaseView, TemplateView):
    """Manager search view for in the homepage"""
    template_name = 'management/search.html'

    def dispatch(self, *args, **kwargs):
        self.healthpersons = []
        self.no_search_term = False
        return super(SearchView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'searchterm' in request.POST:
            searchterm = request.POST['searchterm']
            if searchterm not in (None, ''):
                # Search through healthprofessionals & secretariat
                healthpersons = []
                hospital = self.request.user.hospital

                is_specialism = False
                for l in SPECIALISM_CHOICES:
                    if searchterm.lower() in l[1].lower():
                        is_specialism = True
                        searchterm = l[0]
                        break

                if is_specialism:
                    healthprofessionals = HealthProfessional.objects.filter(
                        specialism=searchterm,
                        user__hospital=hospital)
                    secretariat = Secretary.objects.filter(
                        specialism=searchterm,
                        user__hospital=hospital)
                    healthpersons += (healthprofessionals + secretariat)

                else:
                    hmac_last_name = create_hmac(
                        settings.SURNAME_SEARCH_KEY,
                        searchterm.lower())
                    users = User.objects.filter(
                        hmac_last_name=hmac_last_name,
                        deleted_on__isnull=True,
                        hospital=hospital)
                    healthpersons = [user.healthperson for user in users]
                self.healthpersons = healthpersons
            else:
                self.no_search_term = True

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({'healthpersons': self.healthpersons,
                        'no_search_term': self.no_search_term})
        return context


class ManagerPersonaliaEdit(ManagerBaseView, FormView):
    """Manager personalia edit view"""
    form_class = ProfileEditForm
    template_name = 'management/edit_view.html'

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'manager_view_personalia',
            args=[self.kwargs.get('manager_session_id')])
        return super(ManagerPersonaliaEdit, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ManagerPersonaliaEdit, self).get_form_kwargs()
        kwargs.update({'instance': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ManagerPersonaliaEdit, self).get_context_data(**kwargs)
        context.update({'section': _('Personalia & Account'),
                        'cancel_url': self.success_url})
        return context

    def form_valid(self, form):
        # Set on person self
        user = form.save(commit=False)

        # Change password
        if form.cleaned_data['change_password'] == 'yes':
            user.set_password(form.cleaned_data['password'])

        # save user
        user.save()
        return super(ManagerPersonaliaEdit, self).form_valid(form)

# -*- coding: utf-8 -*-
"""
A secretary can add/edit/remove patients and make appointments.
This module contains the views needed to perform those functions.

:subtitle:`Class definitions:`
"""
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from apps.utils.utils import sent_password_change_request
from django.utils.translation import ugettext_lazy as _
from apps.healthperson.secretariat.models import Secretary
from apps.healthperson.secretariat.forms import SecretarySearchForm,\
    SecretaryAddForm, SecretaryEditForm
from apps.questionnaire.models import QuestionnaireRequest

from django.contrib.auth.models import Group
from core.encryption.random import randomkey
from dateutil import parser
from django.db.models import Q
from apps.account.models import User
from apps.healthperson.utils import is_allowed_secretary, is_allowed_manager,\
    is_allowed_manager_and_secretary, login_url
from apps.rcmessages.views import get_all_messages_for_secretary
from apps.base.views import BaseIndexTemplateView
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.views import BaseAddView


class SecretaryBaseView(View):
    """Base view which adds the secretary by using the secretary_session_id
       or logged in user"""

    def dispatch(self, *args, **kwargs):
        """Add secretary to the view class"""
        if 'secretary_session_id' in kwargs:
            secretary_session_id = kwargs.get('secretary_session_id')
            if secretary_session_id not in self.request.session:
                raise Http404
            healthperson_ptr_id =\
                self.request.session[secretary_session_id][8:]

            try:
                self.secretary = Secretary.objects.select_related(
                    'user__personal_encryption_key').get(
                    healthperson_ptr_id=healthperson_ptr_id)
            except Secretary.DoesNotExist:
                raise Http404
        else:
            # set secretary to self.
            self.secretary = self.request.user.healthperson
        return super(SecretaryBaseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Base context, include the secretary by default"""
        context = super(SecretaryBaseView, self).get_context_data(**kwargs)
        context.update({'secretary': self.secretary})
        return context


class SecretaryIndexView(BaseIndexTemplateView, SecretaryBaseView):
    """Class based view for secretary homepage"""
    template_name = 'secretariat/index.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_secretary, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(SecretaryIndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SecretaryIndexView, self).get_context_data(**kwargs)

        messages = get_all_messages_for_secretary(self.secretary)
        if len(messages) > 0:
            message = messages[0]
        else:
            message = None

        context.update({'message': message})
        context.update({'secretary': self.secretary})
        # list of questionnaire_request to handle the appointment part for.
        # urgent always on top
        urgent_patient_controles = QuestionnaireRequest.objects.filter(
            urgent=True,
            finished_on__isnull=False,
            appointment_added_on__isnull=True,
            appointment_needed=True).order_by('finished_on')

        controles = QuestionnaireRequest.objects.filter(
            urgent=False,
            finished_on__isnull=False,
            handled_on__isnull=False,
            appointment_added_on__isnull=True,
            appointment_needed=True).order_by('finished_on')

        # combine lists.
        context.update(
            {'controle_list': list(urgent_patient_controles) + list(controles)}
        )

        return context


class SecretariatSearchView(FormView):
    """
    Search secretary view page
    used by manager
    """
    form_class = SecretarySearchForm
    template_name = 'secretariat/search.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.has_searched = False
        self.secretariat = None
        return super(SecretariatSearchView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SecretariatSearchView, self).get_context_data(**kwargs)
        context.update({'secretariat': self.secretariat,
                        'has_searched': self.has_searched})
        return context

    def get_initial(self):
        """
        Get initial data, used for showing the old results and
        form data when the user uses the back button to return to the form
        """
        if (('last_search' in self.request.session and
             'back' in self.request.GET)):
            return self.request.session['last_search']
        return None

    def get(self, request, *args, **kwargs):
        """Re-execute the search if the user has used the back button"""
        if 'last_search' in request.session and 'back' in request.GET:
            form_class = self.get_form_class()
            form = form_class(request.session['last_search'])
            if form.is_valid():
                self.form_valid(form)
        return super(SecretariatSearchView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Perform the search action, search for a secretary"""
        self.has_searched = True
        filter_valid = False
        secretariat = []
        # Build up search filter for persons
        hospital = self.request.user.hospital

        user_filter = Q(groups__name='secretariat') &\
            Q(hospital=hospital) & Q(deleted_on__isnull=True)

        if form.cleaned_data['last_name'] not in ('', None):
            user_filter = user_filter & Q(
                hmac_last_name=form.cleaned_data['last_name'])
            filter_valid = True

        if form.cleaned_data['specialism'] not in ('', None):
            filter_valid = True
            specialism = form.cleaned_data['specialism']
            user_filter = user_filter &\
                Q(healthperson__secretary__specialism=specialism)

        # Execute filter
        users = User.objects.filter(user_filter)

        # Execute filter or by default just take all secretariat
        if filter_valid:
            if self.request.POST:
                self.request.session['last_search'] = self.request.POST
            secretariat = [user.healthperson for user in users]

        self.secretariat = secretariat

        return super(SecretariatSearchView, self).get(
            self.request, *self.args, **self.kwargs)


class SearchView(TemplateView):
    """
    Generic search page as available in the homepage
    can be used by a secretary or manager (second is not used)
    """
    template_name = 'secretariat/search_index.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager_and_secretary, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.patients = []
        self.no_search_term = False
        return super(SearchView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Search for patients"""
        if 'searchterm' in request.POST:
            patients = []
            searchterm = request.POST['searchterm']
            if searchterm not in (None, ''):
                # Build up search filter for persons

                hospital = request.user.hospital

                user_filter = Q(groups__name='patients') &\
                    Q(hospital=hospital) & Q(deleted_on__isnull=True)

                user_filter2 = Q(hmac_last_name=searchterm)
                user_filter2 = user_filter2 | Q(
                    hmac_local_hospital_number=searchterm)
                user_filter2 = user_filter2 | Q(
                    hmac_BSN=searchterm)

                # try parsing the filled in searchterm to a date,
                # if failed don't include it.
                try:
                    test_date = parser.parse(searchterm, dayfirst=True)
                except (ValueError, TypeError):
                    test_date = None

                if test_date:
                    user_filter2 = user_filter2 | Q(date_of_birth=test_date)

                user_filter = user_filter & user_filter2

                # Execute filter
                users = User.objects.filter(user_filter)
                patients = [user.healthperson for user in users]
            else:
                self.no_search_term = True
            self.patients = patients
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update(
            {'patients': self.patients, 'no_search_term': self.no_search_term}
        )
        return context


class SecretariatAddView(BaseAddView):
    """
    Class based view for adding a new secretary
    used by a manager
    """
    form_class = SecretaryAddForm
    template_name = 'secretariat/add.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.succes_url = reverse('index')
        return super(SecretariatAddView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = self.get_user_for_form(form)

        # add to secretariat group
        user.groups = [Group.objects.get(name='secretariat')]

        secretary = Secretary()
        secretary.specialism = form.cleaned_data['specialism']
        secretary.changed_by_user = self.request.user
        secretary.save()

        user.healthperson = secretary
        user.save()

        sent_password_change_request(user, self.url_prefix, False, True)

        secretary_session_id = randomkey()
        self.request.session[secretary_session_id] =\
            'storage_{0}'.format(secretary.health_person_id)
        self.success_url = reverse(
            'secretariat_view_personalia',
            args=(secretary_session_id,))

        return super(SecretariatAddView, self).form_valid(form)


class SecretariatPersonaliaView(SecretaryBaseView, TemplateView):
    """
    Class based view for showing secretary personalia
    used by the manager and secretary
    """
    template_name = 'secretariat/personalia_view.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager_and_secretary, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(SecretariatPersonaliaView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context =\
            super(SecretariatPersonaliaView, self).get_context_data(**kwargs)
        context.update({'submenu': 'personalia'})
        return context


class SecretariatPersonaliaEdit(SecretaryBaseView, FormView):
    """
    Class based view for editing secretary personalia
    used by a manager and secretary
    """
    template_name = 'secretariat/edit_view.html'
    form_class = SecretaryEditForm

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager_and_secretary, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'secretariat_view_personalia',
            args=[self.kwargs.get('secretary_session_id')]
        )
        return super(SecretariatPersonaliaEdit, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SecretariatPersonaliaEdit, self).get_form_kwargs()
        kwargs.update({'instance': self.secretary.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context =\
            super(SecretariatPersonaliaEdit, self).get_context_data(**kwargs)
        context.update({'section': _('Personalia & Account'),
                        'cancel_url': self.success_url})
        return context

    def form_valid(self, form):
        """Save the person and secretary information"""
        user = form.save(commit=False)

        # Change password
        if form.cleaned_data['change_password'] == 'yes':
            user.set_password(form.cleaned_data['password'])

        # save user
        user.save()

        self.secretary.specialism = form.cleaned_data['specialism']
        self.secretary.save()

        return super(SecretariatPersonaliaEdit, self).form_valid(form)


class SecretariatRemove(SecretaryBaseView, TemplateView):
    """
    Remove a secretary, sets the user deleted_on date and is_active
    to False
    """
    template_name = 'secretariat/remove_confirmation.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.cancel_url = reverse('secretariat_search')
        return super(SecretariatRemove, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Remove the secretary by setting the user to inactive"""
        user = self.secretary.user
        user.set_unusable_password()
        user.is_active = False
        user.deleted_on = date.today()
        user.changed_by_user = self.request.user
        user.save()
        return HttpResponseRedirect(self.cancel_url)

    def get_context_data(self, **kwargs):
        context = super(SecretariatRemove, self).get_context_data(**kwargs)
        context.update({'cancel_url': self.cancel_url})
        return context

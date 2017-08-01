"""
This module contains all the views which are used
by the manager to add/edit healthprofessionals and the
views used by the healthprofessional itselves.

:subtitle:`Class definitions:`
"""
import StringIO
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from apps.utils.utils import sent_password_change_request

from apps.healthperson.healthprofessional.forms import\
    HealthProfessionalAddForm, HealthProfessionalSearchForm,\
    HealthProfessionalEditForm, HealthProfessionalPhotoForm,\
    HealthProfessionalNotificationEditForm,\
    HealthProfessionalOutOfOfficeEditForm
from apps.account.forms import SetPasswordForm
from apps.healthperson.healthprofessional.models import HealthProfessional

from apps.questionnaire.models import QuestionnaireRequest

from django.utils.translation import ugettext as _
from PIL import Image
from django.contrib.auth.models import Group
from apps.account.models import User
from core.encryption.random import randomkey
from django.db.models import Q
from dateutil import parser
from apps.healthperson.utils import is_allowed_healthprofessional,\
    is_allowed_manager, is_allowed_manager_and_healthprofessional, login_url

from apps.rcmessages.views import get_all_messages_for_healthprofessional
from django.core.files.uploadedfile import InMemoryUploadedFile


from apps.base.views import BaseIndexTemplateView
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from core.views import FormView
from apps.healthperson.views import BaseAddView
from django.http import Http404

PHOTO_WIDTH = 133
PHOTO_HEIGHT = 165


class HealthProfessionalBaseView(View):
    """
    Base view which adds the healthprofessional by
    using the healthprofessional_session_id
    or logged in user
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Adds healthprofessional to the view class"""
        if 'healthprofessional_session_id' in kwargs:
            healthprofessional_session_id = kwargs.get(
                'healthprofessional_session_id')
            if healthprofessional_session_id not in self.request.session:
                raise Http404
            healthperson_ptr_id =\
                self.request.session[healthprofessional_session_id][8:]

            try:
                self.healthprofessional =\
                    HealthProfessional.objects.select_related(
                        'user__personal_encryption_key').get(
                        healthperson_ptr_id=healthperson_ptr_id)
            except HealthProfessional.DoesNotExist:
                raise Http404

        else:
            # set healthprofessional to self.
            self.healthprofessional = self.request.user.healthperson
        return super(
            HealthProfessionalBaseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Base context, include the healthprofessional by default"""
        context = super(HealthProfessionalBaseView,
                        self).get_context_data(**kwargs)
        context.update({'healthprofessional': self.healthprofessional})
        if hasattr(self, 'submenu'):
            context.update({'submenu': self.submenu})
        return context


class HealthProfessionalIndexView(BaseIndexTemplateView,
                                  HealthProfessionalBaseView):
    """
    This view shows the homepage of the healthprofessional
    """
    template_name = 'healthprofessional/index.html'

    def get_controles_for_healthprofessional(self, healthprofessional):
        """
        Adds controles and urgent_patient_controles to the view so
        they can be shown in the overview.

        Args:
            - healthprofessional: The healthprofessional to get all\
              all controles for
        """
        # Get the controles (appointment_healthprofessional =
        # self or controle_healthprofessional=self))
        controle_filter_base = (Q(
            practitioner=healthprofessional) |
            Q(appointment__appointment_healthprofessional=healthprofessional))
        controle_filter_base = controle_filter_base & Q(
            finished_on__isnull=False)

        # Re-add controles after handling but still appointment_needed with:
        # | (Q(appointment_needed = True) &
        # Q(appointment_added_on__isnull = True))
        extra_filter_base = Q(handled_on__isnull=True)

        # Show (urgent) controles which are finished & (not handled)
        # For re-adding controles with (handled & no appointment)
        # see comments above...
        controle_filter = controle_filter_base & (extra_filter_base)
        # urgent_controle_filter = Q(urgent=True) & controle_filter_base & (
        #    extra_filter_base)

        controles = QuestionnaireRequest.objects.filter(
            controle_filter).order_by('-finished_on')

        self.urgent_patient_controles = []
        self.controles = []

        for controle in controles:
            if controle.urgent:
                self.urgent_patient_controles.append(controle)
            else:
                self.controles.append(controle)

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalIndexView,
                        self).get_context_data(**kwargs)
        self.get_controles_for_healthprofessional(self.healthprofessional)
        controles = list(self.controles)
        urgent_patient_controles = list(self.urgent_patient_controles)

        # Add controles from healthprofessionals for which
        # the logged-in healthprofessional is the replacement.
        for hp_to_replace in self.healthprofessional.replacement_set.all():
            if ((hp_to_replace.out_of_office_start <= date.today() and
                 hp_to_replace.out_of_office_end >= date.today())):
                [extra_controles, extra_urgent_patient_controles] =\
                    self.get_controles_for_healthprofessional(hp_to_replace)

                for extra_controle in extra_controles:
                    if extra_controle not in controles:
                        controles.append(extra_controle)
                temp_controles = extra_urgent_patient_controles
                for extra_urgent_patient_controle in temp_controles:
                    if ((extra_urgent_patient_controle not in
                         urgent_patient_controles)):
                        urgent_patient_controles.append(
                            extra_urgent_patient_controle)

        try:
            message = get_all_messages_for_healthprofessional(
                self.healthprofessional)[0]
        except IndexError:
            message = None

        context.update({'message': message,
                        'controles': controles,
                        'urgent_patient_controles': urgent_patient_controles,
                        'healthprofessional': self.healthprofessional})
        return context


class SearchView(TemplateView):
    """Generic search page as available in the homepage"""
    template_name = 'healthprofessional/search_index.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        """Init default values to be used in the context"""
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
                    hmac_first_name=searchterm)
                user_filter2 = user_filter2 | Q(
                    hmac_BSN=searchterm)

                # try parsing the filled in searchterm to a date,
                # if failed don't include it.
                try:
                    date = parser.parse(searchterm, dayfirst=True)
                except (ValueError, TypeError):
                    date = None

                if date:
                    user_filter2 = user_filter2 | Q(date_of_birth=date)

                user_filter = user_filter & user_filter2

                # Execute filter
                users = User.objects.filter(user_filter)
                patients = [user.healthperson for user in users]
            else:
                self.no_search_term = True
            self.patients = patients
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Return the found patients in a context"""
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({'patients': self.patients,
                        'no_search_term': self.no_search_term})
        return context


class HealthProfessionalCropPhoto(HealthProfessionalBaseView, TemplateView):
    """
    View allows to crop the photo of the healthprofessional, if necessary.
    """
    template_name = 'healthprofessional/photo_crop.html'
    submenu = 'photo'

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(HealthProfessionalCropPhoto,
                     self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.healthprofessional.photo_location.open('r')
        image_file = self.healthprofessional.photo_location._file
        image = Image.open(image_file.file)

        x_offset = int(request.POST['x1'])
        y_offset = int(request.POST['y1'])

        # crop image...
        image = image.crop(
            (x_offset, y_offset,
             x_offset + PHOTO_WIDTH, y_offset + PHOTO_HEIGHT))

        # Save in memory temporarily to change photo name
        image_io = StringIO.StringIO()
        image.save(image_io, 'PNG', quality=100)
        image_file = InMemoryUploadedFile(
            image_io, None,
            self.healthprofessional.photo_location.name,
            'image/png', image_io.len, None)

        # Remove old file, save new file & update field
        self.healthprofessional.photo_location.delete()
        self.healthprofessional.photo_location.save(
            User.objects.make_random_password(length=10) + '.png', image_file)
        image_file = None
        image = None
        image_io = None
        return HttpResponseRedirect(reverse(
            'healthprofessional_view_photo',
            args=(self.kwargs.get('healthprofessional_session_id'),)))


class HealthProfessionalEditPhoto(HealthProfessionalBaseView, FormView):
    """
    Add/edit or remove the photo of an healthprofessional
    """
    template_name = 'healthprofessional/edit_view.html'
    form_class = HealthProfessionalPhotoForm

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.photo_error = None
        self.success_url = reverse(
            'healthprofessional_view_photo',
            args=(self.kwargs.get('healthprofessional_session_id'),))
        return super(HealthProfessionalEditPhoto,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(HealthProfessionalEditPhoto, self).get_form_kwargs()
        kwargs.update({'instance': self.healthprofessional})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalEditPhoto,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.success_url, 'upload_photo': True,
                        'section': _('Behandelaar pasfoto')})
        return context

    def resize_photo(self, image):
        x_ratio = float(image.size[0]) / PHOTO_WIDTH
        y_ratio = float(image.size[1]) / PHOTO_HEIGHT

        if y_ratio > x_ratio:
            new_y = int(float(image.size[1]) / x_ratio)
            new_x = PHOTO_WIDTH
        else:
            new_y = PHOTO_HEIGHT
            new_x = int(float(image.size[0]) / y_ratio)

        image = image.resize((new_x, new_y))
        return image

    def form_valid(self, form):
        healthprofessional = form.save(commit=False)
        photo_error = None
        # check size and if to large resize
        image_file = healthprofessional.photo_location._file

        if image_file:
            image = Image.open(image_file.file)

            if image.size[0] < PHOTO_WIDTH or image.size[1] < PHOTO_HEIGHT:
                photo_error = _('Pasfoto is te klein, minimaal: ') +\
                    str(PHOTO_WIDTH) + 'x' + str(PHOTO_HEIGHT) + 'px'

            if not photo_error:
                if ((image.size[0] != PHOTO_WIDTH and
                     image.size[1] != PHOTO_HEIGHT)):

                    image = self.resize_photo(image)
                    image_file = StringIO.StringIO()
                    image.save(image_file, 'PNG', quality=100)

                    healthprofessional.photo_location._file.file = image_file
                    healthprofessional.photo_location.name =\
                        User.objects.make_random_password(length=10) + '.png'
                    healthprofessional.save()

                    if ((image.size[0] != PHOTO_WIDTH or
                         image.size[1] != PHOTO_HEIGHT)):

                        # still not perfect.. need to crop
                        crop_url = reverse(
                            'healthprofessional_crop_photo',
                            args=(self.kwargs.get(
                                'healthprofessional_session_id'),))
                        return HttpResponseRedirect(crop_url)
                    else:
                        return super(HealthProfessionalEditPhoto,
                                     self).form_valid(form)
                else:
                    image_file = StringIO.StringIO()
                    image.save(image_file, 'PNG', quality=100)
                    healthprofessional.photo_location._file.file = image_file
                    healthprofessional.photo_location.name =\
                        User.objects.make_random_password(length=10) + '.png'
                    healthprofessional.save()
                    return super(HealthProfessionalEditPhoto,
                                 self).form_valid(form)
            else:
                form.errors['photo_location'] = photo_error
                return self.form_invalid(form)
        else:
            # done nothing or remove..
            healthprofessional.save()
            return super(HealthProfessionalEditPhoto, self).form_valid(form)


class HealthProfessionalPhotoView(HealthProfessionalBaseView, TemplateView):
    """
    Show photo of healthprofessional
    """
    template_name = 'healthprofessional/photo_view.html'
    submenu = 'photo'

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(HealthProfessionalPhotoView,
                     self).dispatch(*args, **kwargs)


class HealthProfessionalNotificationView(HealthProfessionalBaseView,
                                         TemplateView):
    """
    Show notification settings
    """
    template_name = 'healthprofessional/notification_view.html'
    submenu = 'notification'

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(HealthProfessionalNotificationView,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalNotificationView,
                        self).get_context_data(**kwargs)
        return context


class HealthProfessionalOutOfOfficeView(HealthProfessionalBaseView,
                                        TemplateView):
    """
    Show out of office settings
    """
    template_name = 'healthprofessional/out_of_office_view.html'
    submenu = 'out_of_office'

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(HealthProfessionalOutOfOfficeView,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalOutOfOfficeView,
                        self).get_context_data(**kwargs)
        return context


class HealthProfessionalOutOfOfficeEdit(HealthProfessionalBaseView,
                                        FormView):
    """
    Edit the out of office settings for an healthprofessional.

    These settings are used to configure an out of office period
    with a replacement.
    """
    template_name = 'healthprofessional/edit_view.html'
    form_class = HealthProfessionalOutOfOfficeEditForm

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'healthprofessional_view_out_of_office',
            args=(self.kwargs.get('healthprofessional_session_id'),))
        return super(HealthProfessionalOutOfOfficeEdit,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(HealthProfessionalOutOfOfficeEdit,
                       self).get_form_kwargs()
        kwargs.update({'instance': self.healthprofessional})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalOutOfOfficeEdit,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.success_url,
                        'section': _('Afwezigheid')})
        return context

    def form_valid(self, form):
        healthprofessional = form.save(commit=False)
        healthprofessional.save()
        return super(HealthProfessionalOutOfOfficeEdit,
                     self).form_valid(form)


class HealthProfessionalNotificationEdit(HealthProfessionalBaseView, FormView):
    """
    Edit the notification settings for an healthprofessional.

    These settings are used for sending notifications of unhandeld
    (urgent) controls.
    """
    template_name = 'healthprofessional/edit_view.html'
    form_class = HealthProfessionalNotificationEditForm

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'healthprofessional_view_notification',
            args=(self.kwargs.get('healthprofessional_session_id'),))
        return super(HealthProfessionalNotificationEdit,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(HealthProfessionalNotificationEdit,
                       self).get_form_kwargs()
        kwargs.update({'instance': self.healthprofessional})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalNotificationEdit,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.success_url,
                        'section': _('Notificatie instellingen')})
        return context

    def form_valid(self, form):
        healthprofessional = form.save(commit=False)
        healthprofessional.save()

        return super(HealthProfessionalNotificationEdit, self).form_valid(form)


class HealthProfessionalPersonaliaView(HealthProfessionalBaseView,
                                       TemplateView):
    """
    Shows the personalia of an healhtprofessional which is the information
    stored in the coupled :class:`apps.account.models.User` instance.
    """
    template_name = 'healthprofessional/personalia_view.html'
    submenu = 'personalia'

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(HealthProfessionalPersonaliaView,
                     self).dispatch(*args, **kwargs)


class HealthProfessionalSetPassword(HealthProfessionalBaseView, FormView):
    """
    Displays a form to set a password. Used to initialize password for an healthprofessional
    """
    template_name = 'healthprofessional/edit_view.html'
    form_class = SetPasswordForm

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = self.request.session.get('next_url', None)
        return super(HealthProfessionalSetPassword,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(
            HealthProfessionalSetPassword, self).get_form_kwargs()
        kwargs.update({'user': self.healthprofessional.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalSetPassword,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.success_url,
                        'section': _('Zet wachtwoord'),
                        'extra_info': _('U heeft nog geen wachtwoord ingesteld voor RemoteCare. ' +\
                            'Geef deze hieronder op om (ook) direct in RemoteCare te kunnen inloggen.')})
        return context

    def form_valid(self, form):
        # Change password (optional)
        user = self.healthprofessional.user
        user.set_password(form.cleaned_data['password'])

        # save user
        user.save()

        return super(HealthProfessionalSetPassword, self).form_valid(form)


class HealthProfessionalPersonaliaEdit(HealthProfessionalBaseView, FormView):
    """
    Edit the personalia of an healhtprofessional which is the information
    stored in the coupled :class:`apps.account.models.User` instance.
    """
    template_name = 'healthprofessional/edit_view.html'
    form_class = HealthProfessionalEditForm

    @method_decorator(user_passes_test(
        is_allowed_manager_and_healthprofessional, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse(
            'healthprofessional_view_personalia',
            args=(self.kwargs.get('healthprofessional_session_id'),))
        return super(HealthProfessionalPersonaliaEdit,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(
            HealthProfessionalPersonaliaEdit, self).get_form_kwargs()
        kwargs.update({'instance': self.healthprofessional.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalPersonaliaEdit,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.success_url,
                        'section': _('Personalia & Account')})
        return context

    def form_valid(self, form):
        user = form.save(commit=False)

        # Change password (optional)
        if form.cleaned_data['change_password'] == 'yes':
            user.set_password(form.cleaned_data['password'])

        # save user
        user.save()

        self.healthprofessional.function = form.cleaned_data['function']
        self.healthprofessional.specialism = form.cleaned_data['specialism']
        self.healthprofessional.telephone = form.cleaned_data['telephone']

        self.healthprofessional.save()
        return super(HealthProfessionalPersonaliaEdit, self).form_valid(form)


class HealthProfessionalSearchView(FormView):
    """
    Search for an healthprofessional as a manager
    """
    template_name = 'healthprofessional/search.html'
    form_class = HealthProfessionalSearchForm

    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_allowed_manager,
                                       login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.has_searched = False
        self.healthprofessionals = None
        return super(HealthProfessionalSearchView,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add the search results to the context"""
        context = super(HealthProfessionalSearchView,
                        self).get_context_data(**kwargs)
        context.update({'healthprofessionals': self.healthprofessionals,
                        'has_searched': self.has_searched})
        return context

    def get_initial(self):
        """
        Get initial data, used for showing the old results
        and form data when
        the user uses the back button to return to the form
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
        return super(HealthProfessionalSearchView,
                     self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Perform the search action, search for a healthprofessional"""
        self.has_searched = True
        filter_valid = False
        healthprofessionals = None

        # Build up search filter for persons
        hospital = self.request.user.hospital
        user_filter = Q(groups__name='healthprofessionals') &\
            Q(hospital=hospital) & Q(deleted_on__isnull=True)

        if form.cleaned_data['last_name'] not in ('', None):
            user_filter = user_filter & Q(
                hmac_last_name=form.cleaned_data['last_name'])
            filter_valid = True

        if form.cleaned_data['first_name'] not in ('', None):
            user_filter = user_filter & Q(
                hmac_first_name=form.cleaned_data['first_name'])
            filter_valid = True

        if form.cleaned_data['function'] not in ('', None):
            function = form.cleaned_data['function']
            user_filter = user_filter &\
                Q(healthperson__healthprofessional__function=function)
            filter_valid = True

        if form.cleaned_data['specialism'] not in ('', None):
            specialism = form.cleaned_data['specialism']
            user_filter = user_filter &\
                Q(healthperson__healthprofessional__specialism=specialism)
            filter_valid = True

        if filter_valid:
            # Execute filter
            users = User.objects.filter(user_filter)

            if self.request.POST:
                self.request.session['last_search'] = self.request.POST

            healthprofessionals = []
            for user in users:
                healthprofessionals.append(user.healthperson)

        self.healthprofessionals = healthprofessionals

        return super(HealthProfessionalSearchView,
                     self).get(self.request, *self.args, **self.kwargs)


class HealthProfessionalAddView(BaseAddView):
    """
    Class based view for adding a new healthprofessional
    """
    template_name = 'healthprofessional/add.html'
    form_class = HealthProfessionalAddForm

    @method_decorator(login_required)
    @method_decorator(user_passes_test(
        is_allowed_manager, login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.succes_url = reverse('index')
        return super(HealthProfessionalAddView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = self.get_user_for_form(form)

        healthprofessional = HealthProfessional()
        healthprofessional.function = form.cleaned_data['function']
        healthprofessional.specialism = form.cleaned_data['specialism']
        healthprofessional.telephone = form.cleaned_data['telephone']

        # add to healthprofessionals group
        user.groups = [Group.objects.get(name='healthprofessionals')]
        healthprofessional.changed_by_user = self.request.user
        healthprofessional.save()

        user.healthperson = healthprofessional
        user.save()

        sent_password_change_request(user, self.url_prefix, False, True)

        healthprofessional_session_id = randomkey()
        self.request.session[healthprofessional_session_id] =\
            'storage_{0}'.format(healthprofessional.health_person_id)
        self.success_url = reverse('healthprofessional_view_personalia',
                                   args=(healthprofessional_session_id,))
        return super(HealthProfessionalAddView, self).form_valid(form)


class HealthProfessionalRemove(HealthProfessionalBaseView, TemplateView):
    """
    Remove the healthprofessional by setting the deleted_on attribute
    on the coupled :class:`apps.account.models.User` instance.
    """
    template_name = 'healthprofessional/remove_confirmation.html'

    @method_decorator(user_passes_test(is_allowed_manager,
                                       login_url=login_url))
    def dispatch(self, *args, **kwargs):
        self.cancel_url = reverse('healthprofessional_search')
        return super(HealthProfessionalRemove, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Remove the healthprofessional by setting the user to inactive
        """
        user = self.healthprofessional.user
        user.deleted_on = date.today()
        user.set_unusable_password()
        user.is_active = False
        user.changed_by_user = self.request.user
        user.save()
        return HttpResponseRedirect(self.cancel_url)

    def get_context_data(self, **kwargs):
        context = super(HealthProfessionalRemove,
                        self).get_context_data(**kwargs)
        context.update({'cancel_url': self.cancel_url})
        return context

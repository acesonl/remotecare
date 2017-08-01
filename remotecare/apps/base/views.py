from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from apps.account.forms import AgreeWithRulesForm
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView


class IndexView(View):
    '''
    Class based index view, used as entry point
    in the main url.py to case switches based on the
    group of the logged in user
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_view(self, request):
        from apps.healthperson.management.views import ManagerIndexView
        from apps.healthperson.healthprofessional.views import\
            HealthProfessionalIndexView
        from apps.healthperson.secretariat.views import SecretaryIndexView
        from apps.healthperson.patient.views import PatientIndexView

        if request.user.in_group('managers'):
            return ManagerIndexView.as_view()
        elif request.user.in_group('secretariat'):
            return SecretaryIndexView.as_view()
        elif request.user.in_group('healthprofessionals'):
            return HealthProfessionalIndexView.as_view()

        return PatientIndexView.as_view()

    def get(self, request, *args, **kwargs):
        view = self.get_view(request)
        return view(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):  # pragma: no cover
        view = self.get_view(request)
        return view(self.request, *args, **kwargs)


class BaseIndexView(View):
    '''
    Base class based view for all index views
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BaseIndexView, self).dispatch(*args, **kwargs)


class BaseIndexTemplateView(TemplateView, BaseIndexView):
    '''
    Class based template view used as base class for all
    healthperson specific class based index views
    '''
    pass


class SearchView(View):
    '''
    Class based main search view, like the index view
    case switches between users based on group
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SearchView, self).dispatch(*args, **kwargs)

    def get_view(self, request):
        from apps.healthperson.management.views import\
            SearchView as ManagerSearchView
        from apps.healthperson.healthprofessional.views import\
            SearchView as HealthProfessionalSearchView
        from apps.healthperson.secretariat.views import\
            SearchView as SecretarySearchView
        from apps.healthperson.patient.views import\
            SearchView as PatientSearchView

        if request.user.groups.filter(name='managers').exists():
            return ManagerSearchView.as_view()
        elif request.user.groups.filter(name='healthprofessionals').exists():
            return HealthProfessionalSearchView.as_view()
        elif request.user.groups.filter(name='secretariat').exists():
            return SecretarySearchView.as_view()
        return PatientSearchView.as_view()

    def get(self, request, *args, **kwargs):
        view = self.get_view(request)
        return view(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = self.get_view(request)
        return view(self.request, *args, **kwargs)


# TODO: Use this view for acceptation of rules
class AgreeWithRulesView(FormView):  # pragma: no cover
    '''
    Class based view that can be used
    for accepting the rules for proper usage
    '''
    form_class = AgreeWithRulesForm
    template_name = 'agree_with_rules.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('index', args=[])
        return super(AgreeWithRulesView, self).dispatch(*args, **kwargs)

    def get_form_instance(self):
        """Include the user instance"""
        return self.request.user

    def form_valid(self, form):
        # print form
        # user = form.save(commit=False)
        # print user
        return super(AgreeWithRulesView, self).get(
            self.request, *self.args, **self.kwargs)

from datetime import datetime, timedelta
from django.conf import settings
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.sites.requests import RequestSite


from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from core.views import FormView
from core.encryption.hash import create_hmac
from apps.account.models import User, LoginAttempt
from apps.authentication.forms import RCAuthenticationForm, SMSCodeForm,\
    ForgotPasswordForm, ForgotPasswordValidateForm, ResetPasswordForm
from apps.utils.utils import sent_password_change_request,\
    sent_password_change_sms, change_password, get_password_change_request,\
    create_login_sms_code

# FORGOT password procedure


# Step 1: forgot password form asking for the e-mail address
class ForgotPassword(FormView):
    '''
    Forgot password view, asks for e-mail address
    to sent e-mail with password-reset instructions.
    '''
    template_name = 'registration/password_reset_form.html'
    form_class = ForgotPasswordForm

    @method_decorator(sensitive_post_parameters('email'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('email_sent')
        return super(ForgotPassword,
                     self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        # Check if the email exists..
        user = User.objects.filter(hmac_email=form.cleaned_data['email'])
        if len(user) == 1:
            user = user[0]
            # check if request e-mail is sent and still valid,
            # else sent new one.
            # (Can only be one request, by design)

            # Use utils to sent password change request
            rq = RequestSite(self.request)
            url_prefix = 'http'
            if self.request.is_secure():
                url_prefix += 's'
            url_prefix += '://' + rq.domain
            user.changed_by_user = user
            sent_password_change_request(user, url_prefix)

            # redirect
            return super(ForgotPassword, self).form_valid(form)

        elif len(user) > 1:
            # Should never occur by design, but just in case raise exception
            raise Exception('Meerdere users gevonden voor' + str(user.email))
        else:
            # Not found
            errors = form._errors.setdefault('email', ErrorList())
            errors.append(_('E-mail adres is onbekend of' +
                            'het versturen is niet gelukt.'))
        return self.form_invalid(form)


# Step 2: Show 'email has been sent' page
class EmailSentView(TemplateView):
    '''
    Class based view which shows an information page
    after the password request e-mail is sent.
    '''
    template_name = 'registration/email_sent.html'

    def get_context_data(self, **kwargs):
        context = super(EmailSentView, self).get_context_data(**kwargs)
        context.update({'menu_item': 'users'})
        return context


# Step 3: Page available via link in the e-mail
# Shows a form which request the e-mail
# address again and the date-of-birth
class RequestSMSCodeView(FormView):
    '''
    Request a sms code for setting a new password by filling in
    e-mail address and date-of-birth
    '''
    template_name = 'registration/request_sms_code_form.html'
    form_class = ForgotPasswordValidateForm

    @method_decorator(sensitive_post_parameters('email', 'date_of_birth'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.email_key = None
        self.error = False
        self.error_message = None
        if 'key' in self.request.GET:
            self.email_key = self.request.GET['key']
        else:
            self.error = True

        if not get_password_change_request(self.email_key) or self.error:
            self.error_message = _('De link in de e-mail is' +
                                   ' incorrect of is verlopen.')
            self.template_name =\
                'registration/password_change_request_invalid.html'
        self.success_url = reverse('reset_password') +\
            '?key=' + self.email_key
        return super(RequestSMSCodeView,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Return the found patients in a context"""
        context = super(RequestSMSCodeView,
                        self).get_context_data(**kwargs)
        context.update({'key': self.email_key,
                        'step': 'controle',
                        'error_message': self.error_message})
        return context

    def form_valid(self, form):
        # Sent the password change sms
        if ((sent_password_change_sms(self.email_key,
             form.cleaned_data['email'], form.cleaned_data['date_of_birth']))):
            # redirect to change page
            return super(RequestSMSCodeView, self).form_valid(form)
        else:
            errors = form._errors.setdefault("date_of_birth", ErrorList())
            errors.append(_("E-mail adres of geboortedatum incorrect."))
        return self.form_invalid(form)


# Step 4: reset the password...
class ResetPassword(FormView):
    '''
    Reset password view, uses a request param 'key'
    to get the password_change_request and asks for
    verification by SMS
    '''
    template_name = 'registration/request_sms_code_form.html'
    form_class = ResetPasswordForm

    @method_decorator(sensitive_post_parameters('sms_code', 'password'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.email_key = None
        self.error = False
        self.error_message = None
        if 'key' in self.request.GET:
            self.email_key = self.request.GET['key']
        else:
            self.error = True

        password_change_request = get_password_change_request(self.email_key)
        if not password_change_request:
            self.error = True
        else:
            if not password_change_request.hmac_sms_code:
                self.error = True

        if self.error:
            self.error_message = _('De link in de e-mail is' +
                                   ' incorrect of is verlopen.')
            self.template_name =\
                'registration/password_change_request_invalid.html'
        self.success_url = settings.LOGIN_REDIRECT_URL
        return super(ResetPassword,
                     self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Return the found patients in a context"""
        context = super(ResetPassword,
                        self).get_context_data(**kwargs)
        context.update({'key': self.email_key,
                        'step': 'password',
                        'error_message': self.error_message})
        return context

    def get_form_kwargs(self):
        kwargs = super(ResetPassword, self).get_form_kwargs()
        password_change_request =\
            get_password_change_request(self.email_key)
        if password_change_request:
            kwargs.update({'user': password_change_request.user})
        return kwargs

    def form_valid(self, form):
        # Sent the password change sms

        # first get the user
        password_change_request =\
            get_password_change_request(self.email_key)
        user = password_change_request.user

        # Check if the password can be changed, auto-deletes the
        # password_change_request
        if ((change_password(self.email_key, form.cleaned_data['password'],
             form.cleaned_data['sms_code']))):
            # Do login, use same procedure as login page...
            auth_form = RCAuthenticationForm(
                data={'username': user.email,
                      'password': form.cleaned_data['password']})

            if auth_form.is_valid():
                # Okay, security check complete. Log the user in.
                # Do really login
                auth_login(self.request, auth_form.get_user())

                if self.request.session.test_cookie_worked():
                    self.request.session.delete_test_cookie()

                # Login to settings.LOGIN_REDIRECT_URL
                return super(ResetPassword, self).form_valid(form)

            else:
                # Redirect to login page..
                return HttpResponseRedirect(reverse('login'))
        else:
            errors = form._errors.setdefault("sms_code", ErrorList())
            errors.append(_("De smscode is onjuist."))
        return self.form_invalid(form)


# Login page
class LoginView(FormView):
    '''
    Django view for login. All login attempts are stored.

    To disable possible brute force attempts:
    After 10 unsuccesfull attempts (within a session) the
    session is blocked for 5 minutes
    After 30 unsuccesfull attempts for one account in 30 minutes,
    the account is blocked for 30 minutes.

    The first rule only works in the session, if the session key is
    removed the user can continue
    to try to login.
    The second rule is server-side and is removed after 30 minutes.
    '''
    form_class = RCAuthenticationForm
    template_name = 'registration/login.html'

    # Block login settings
    block_login_max_attempts = 10
    block_login_time = 5  # minutes
    block_time = block_login_time

    # block account settings
    block_account_max_attempts = 30
    block_account_time = 30  # minutes
    block_account_max_time = block_account_time

    date_time_format = '%Y-%m-%d %H:%M:%S'

    @method_decorator(sensitive_post_parameters('email', 'password'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('smscode')
        if 'blocked' in self.request.session:
            self.template_name = 'registration/blocked.html'
        return super(LoginView,
                     self).dispatch(*args, **kwargs)

    @property
    def attempts(self):
        return self.request.session.get('attempts', 0)

    @attempts.setter
    def attempts(self, value):  # lint:ok
        self.request.session['attempts'] = value

    def add_login_attempt(self, succesfull, email):
        extra_info = self.request.META.get('OS', '')
        extra_info += '#' + self.request.META.get('QTJAVA', '')
        login_attempt = LoginAttempt(
            username_hash=create_hmac(settings.EMAIL_SEARCH_KEY, email.lower()),
            succesfull=succesfull,
            ipaddress=self.request.META.get('REMOTE_ADDR', None),
            useragent=self.request.META.get('HTTP_USER_AGENT', None),
            extra_info=extra_info,
            session_id=self.request.session.session_key)
        login_attempt.save()

    def get_context_data(self, **kwargs):
        context = super(LoginView,
                        self).get_context_data(**kwargs)
        context.update({'account_block_time': self.block_account_time,
                        'account_block_nr': self.block_account_max_attempts,
                        'account_block_nr_time': self.block_account_time,
                        'block_time': self.block_time,
                        'block_nr': self.block_login_max_attempts,
                        'step': 'password'})
        return context

    def account_block_check(self, user, username):
        # Block the user account if more attempts than
        # block_account_max_attempts, free again after block_account_max_time
        hmac_email = create_hmac(settings.EMAIL_SEARCH_KEY, username.lower())
        time_to_check =\
            datetime.now() - timedelta(minutes=self.block_account_max_time)

        nr_attempts = LoginAttempt.objects.filter(
            username_hash=hmac_email,
            date__gte=time_to_check,
            succesfull=False).count()

        if user.account_blocked:
            # Check if can be freed again from blocking..
            # Should be zero attempts during last
            # {{ block_account_max_time }} minutes
            if nr_attempts == 0:
                user.account_blocked = False
                user.save()
                self.attempts = 0
        else:
            if nr_attempts >= self.block_account_max_attempts:
                user.account_blocked = True
                user.save()
            else:
                # only store invalid login attempts of
                # valid user e-mail addresses
                self.add_login_attempt(False, username)

    def session_block_check(self):
        # Block via session if more attempts than
        # block_login_max_attempts,free again after block_login_time
        if 'blocked' in self.request.session:
            # blocked via session
            if 'blocked_until' in self.request.session:
                blocked_until = datetime.strptime(
                    self.request.session['blocked_until'],
                    self.date_time_format)
                if blocked_until <= datetime.now():
                    del self.request.session['blocked_until']
                    self.attempts = 0
                    del self.request.session['blocked']
        else:
            # Short block via session
            if self.attempts > (self.block_login_max_attempts - 2):
                block_datetime =\
                    datetime.now() +\
                    timedelta(minutes=self.block_login_time)
                self.request.session['blocked_until'] =\
                    block_datetime.strftime(self.date_time_format)
                self.request.session['blocked'] = True

    def form_invalid(self, form):
        if 'username' in self.request.POST:
            username = self.request.POST['username'].lower()
        else:
            username = None

        if username in (None, ''):
            return super(LoginView, self).form_invalid(form)
        else:
            hmac_email = create_hmac(settings.EMAIL_SEARCH_KEY, username.lower())
            try:
                user = User.objects.get(hmac_email=hmac_email)
            except User.DoesNotExist:
                user = None

        account_blocked = False
        if user:
            # Check if to block the user account
            self.account_block_check(user, username)
            account_blocked = user.account_blocked

        if not account_blocked and 'username' in self.request.POST:
            # Check if to block via session
            self.session_block_check()
            self.attempts += 1

        if account_blocked:
            self.template_name = 'registration/account_blocked.html'
        elif 'blocked' in self.request.session:
            self.template_name = 'registration/blocked.html'

        return super(LoginView, self).form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()

        # set user & backend for sms authentication.
        self.request.session['user_id'] = user.id
        self.request.session['backend'] = user.backend

        self.add_login_attempt(True, self.request.POST['username'].lower())

        create_login_sms_code(user)

        return super(LoginView, self).form_valid(form)


class SMScodeView(FormView):
    '''
    View for verification of SMS code during login
    '''
    template_name = 'registration/login.html'
    form_class = SMSCodeForm

    @method_decorator(sensitive_post_parameters('sms_code'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse('index')
        if 'backend' not in self.request.session:
            return HttpResponseRedirect(reverse('login'))
        return super(SMScodeView,
                     self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SMScodeView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(SMScodeView, self).form_valid(form)


class LogoutView(TemplateView):
    '''
    Logout view
    '''
    template_name = 'registration/logged_out.html'

    def dispatch(self, *args, **kwargs):
        auth_logout(self.request)
        return super(LogoutView,
                     self).dispatch(*args, **kwargs)

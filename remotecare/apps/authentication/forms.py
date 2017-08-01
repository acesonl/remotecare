from django.contrib.auth.forms import AuthenticationForm
from django import forms
from core.forms import BaseForm, FormDateField
from django.utils.translation import ugettext_lazy as _
from datetime import date
from apps.authentication.password_check import clean_data_password
from apps.utils.utils import check_login_sms_code
from django.forms.utils import ErrorList


class RCAuthenticationForm(AuthenticationForm, BaseForm):
    '''
    Basic authentication form
    '''

    def __init__(self, *args, **kwargs):
        super(RCAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': _(
            'E-mail'), 'class': 'inputtext', 'maxlength': 128,
            'autofocus': 'autofocus'})
        self.fields['password'].widget.attrs.update(
            {'placeholder': _('Wachtwoord'),
             'class': 'inputtext'})


class ResetPasswordForm(BaseForm):
    '''
    Reset password form
    '''
    sms_code = forms.CharField(
        max_length=128,
        label=_('SMS-code'),
        required=True)
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord'))
    password2 = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord (herhaal)'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update(
            {'placeholder': _('Wachtwoord')})
        self.fields['password2'].widget.attrs.update(
            {'placeholder': _('Wachtwoord (herhaal)')})

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()

        if 'password' in cleaned_data and 'password2' in cleaned_data:
            error = False
            if ((not error and cleaned_data['password'] !=
                 cleaned_data['password2'])):
                self.errors['password2'] = ErrorList(
                    [_('Het wachtwoord is niet gelijk.')])
                error = True

            # Elaborate check on password.
            if not error:
                clean_data_password(self)

        return cleaned_data


class ForgotPasswordForm(BaseForm):
    '''
    Form for filling in e-mail address.
    '''
    email = forms.EmailField(required=True, label=_('E-mail'))


class SMSCodeForm(BaseForm):
    '''
    Class based form for loggin in the user based
    on a SMS code
    '''
    sms_code = forms.CharField(
        max_length=128,
        label=_('SMS-code'),
        required=True)

    def __init__(self, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = kwargs.pop('request')
        self.user_cache = None
        super(SMSCodeForm, self).__init__(*args, **kwargs)
        self.fields['sms_code'].widget.attrs.update({'autofocus': 'autofocus'})

        self.error_messages = {}
        self.error_messages['sms_code'] = _('SMS code is ongeldig')
        self.error_messages['inactive'] = _('Gebruiker is niet actief')

    def clean(self):
        sms_code = self.cleaned_data.get('sms_code')

        if sms_code:
            self.user_cache = check_login_sms_code(sms_code)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['sms_code'],
                    code='invalid_login',
                    params={'username': 'sms_code'},
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )

            self.user_cache.backend = self.request.session['backend']

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class ForgotPasswordValidateForm(BaseForm):
    '''
    Forgot password validate form for filling in e-mail address & date of birth
    '''
    email = forms.EmailField(
        required=True,
        label=_('E-mail'))
    date_of_birth = FormDateField(
        required=True,
        years=list(range(date.today().year - 100, date.today().year + 1)),
        allow_future_date=False,
        label=_('Geboortedatum'))

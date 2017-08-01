# -*- coding: utf-8 -*-
"""
The forms in this module can be used as a profile editing form
baseclass for easy including e-mail and mobile number validation.

:subtitle:`Class definitions:`
"""
from django import forms
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.authentication.password_check import clean_data_password,\
    clean_data_mobile_number
from apps.account.models import User
from core.forms import BaseModelForm, BaseForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

NONE_YES_NO_CHOICES = (
    ('', ('---------')),
    ('yes', ('Ja')),
    ('no', ('Nee')),
)


class BaseProfileEditForm(BaseModelForm):
    """
    Base class profile-editing-form including
    (repeat) validators for mobile number and e-mail and
    clean method including validation logic.

    ..  note::

        Does not include a fieldsets definition in the meta
        class, this needs to be set in the form that uses
        this class as baseclass.
    """
    # Repeat validators
    mobile_number2 = forms.CharField(
        max_length=128,
        label=_('Mobiel telefoonnummer (herhaal)'),
        required=True)
    email2 = forms.CharField(
        max_length=128,
        label=_('E-mail (herhaal)'),
        required=True)

    def __init__(self, *args, **kwargs):
        """
        Set the user instance to self.user and init
        the repeat validators with the data from the instance if present
        """
        instance = kwargs.get('instance', None)

        # Instance is always an User instance,
        self.user = instance
        super(BaseProfileEditForm, self).__init__(*args, **kwargs)

        # Only set if there is an instance, this class is also used for
        # adding new users
        if instance:
            self.fields['mobile_number2'].initial = instance.mobile_number
            self.fields['email2'].initial = instance.email

    def clean(self):
        cleaned_data = super(BaseProfileEditForm, self).clean()

        # Check if mobile numbers are same
        if (('mobile_number' in cleaned_data and
             'mobile_number2' in cleaned_data)):
            error = False
            if ((cleaned_data['mobile_number'] !=
                 cleaned_data['mobile_number2'])):
                self.errors['mobile_number2'] = ErrorList(
                    [_('Het mobiele nummer is niet gelijk.')])
                error = True

            if not error:
                clean_data_mobile_number(self)

        # Check if e-mail addresses are same
        if (('email' in cleaned_data and
             'email2' in cleaned_data)):
            error = False
            if ((cleaned_data['email'] !=
                 cleaned_data['email2'])):
                self.errors['email2'] = ErrorList(
                    [_('Het e-mail adres is niet gelijk.')])
                error = True

            # Always store lower case..
            cleaned_data['email'] =\
                cleaned_data['email'].lower()

            # Check if e-mail address is currently not in use
            if not error:
                try:
                    temp_user = User.objects.get(
                        hmac_email=str(cleaned_data['email']))
                    if self.instance and temp_user:
                        if self.instance != temp_user:
                            self.errors['email'] = ErrorList(
                                [_('E-mail adres is al in gebruik.')])
                except User.DoesNotExist:
                    error = None

            # Validate the e-mail address
            try:
                validate_email(cleaned_data['email'])
            except ValidationError:
                self.errors['email'] = ErrorList(
                    [_('Invalide e-mail adres')])
        return cleaned_data

    class Meta:
        model = User
        exclude = ('account_blocked', 'personal_encryption_key',
                   'password', 'deleted_on', 'last_login', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser', 'healthperson',
                   'hmac_first_name', 'hmac_last_name', 'hmac_email',
                   'hmac_local_hospital_number', 'hmac_BSN')


class SetPasswordForm(BaseForm):
    """
    This form class let's users set
    their password after logging in automatically via
    the API. (Used by Healthprofessionals)
    """
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord'),
        required=True)

    # repeat validator
    password2 = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord (herhaal)'),
        required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget.attrs.update(
            {'placeholder': _('Wachtwoord')})
        self.fields['password2'].widget.attrs.update(
            {'placeholder': _('Wachtwoord (herhaal)')})

    def clean(self):
        cleaned_data = super(SetPasswordForm, self).clean()

        error = True

        # Check passwords are same if change_password == yes
        if 'password' in cleaned_data and 'password2' in cleaned_data:
            error = False
            if cleaned_data['password'] in ('', None):
                self.errors['password'] = ErrorList(
                    [_('Dit veld is verplicht.')])
                error = True
            if cleaned_data['password2'] in ('', None):
                self.errors['password2'] = ErrorList(
                    [_('Dit veld is verplicht.')])
                error = True

            if ((not error and cleaned_data['password'] !=
                 cleaned_data['password2'])):
                self.errors['password2'] = ErrorList(
                    [_('Het wachtwoord is niet gelijk.')])
                error = True

        # Extended checks on password via clean_data_password,
        # see function in apps.authentication.password_check.py
        if not error:
            clean_data_password(self)

        return cleaned_data


class BasePasswordProfileEditForm(BaseProfileEditForm):
    """
    This form class is an extension of the BaseProfileEditForm
    which provides change password options
    """
    change_password = forms.TypedChoiceField(
        choices=NONE_YES_NO_CHOICES,
        label=_('Verander wachtwoord?'),
        required=False)
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord'),
        required=False)

    # repeat validator
    password2 = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput,
        label=_('Wachtwoord (herhaal)'),
        required=False)

    def __init__(self, *args, **kwargs):
        super(BasePasswordProfileEditForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget.attrs.update(
            {'placeholder': _('Wachtwoord')})
        self.fields['password2'].widget.attrs.update(
            {'placeholder': _('Wachtwoord (herhaal)')})

        self.fields['change_password'].widget.attrs.update(
            {'class': 'choice_display',
             'choices': '''[{'yes': ['change_password']}]'''})

    def clean(self):
        cleaned_data = super(BasePasswordProfileEditForm, self).clean()

        # Check passwords are same if change_password == yes
        if (('change_password' in cleaned_data and
             cleaned_data['change_password'] == 'yes')):
            if 'password' in cleaned_data and 'password2' in cleaned_data:
                error = False
                if cleaned_data['password'] in ('', None):
                    self.errors['password'] = ErrorList(
                        [_('Dit veld is verplicht.')])
                    error = True
                if cleaned_data['password2'] in ('', None):
                    self.errors['password2'] = ErrorList(
                        [_('Dit veld is verplicht.')])
                    error = True

                if ((not error and cleaned_data['password'] !=
                     cleaned_data['password2'])):
                    self.errors['password2'] = ErrorList(
                        [_('Het wachtwoord is niet gelijk.')])
                    error = True

            # Extended checks on password via clean_data_password,
            # see function in apps.authentication.password_check.py
            if not error:
                clean_data_password(self)

        return cleaned_data

    class Meta(BaseProfileEditForm.Meta):
        model = User
        exclude = BaseProfileEditForm.Meta.exclude


# TODO: To be included in a later stage
class AgreeWithRulesForm(forms.Form):  # pragma: no cover
    """
    Form which shows an 'agree with the rules' select box
    which can be used for accepting the rules for using the
    application.
    """
    agree_with_rules = forms.NullBooleanField(
        required=True,
        widget=forms.Select(choices=NONE_YES_NO_CHOICES),
        label=_('I do agree with the rules'))

    def __init__(self, *args, **kwargs):
        super(AgreeWithRulesForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AgreeWithRulesForm, self).clean()
        if 'agree_with_rules' in cleaned_data:
            if cleaned_data['agree_with_rules'] is not True:
                self.errors['agree_with_rules'] = ErrorList(
                    [_('Toegang is alleen mogelijk indien u' +
                        ' akkoord gaat met de regels.')])
                del cleaned_data['agree_with_rules']
        return cleaned_data

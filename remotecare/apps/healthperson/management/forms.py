# -*- coding: utf-8 -*-
"""
This module only contains a form for changing the
profile information of the manager itselves.

:subtitle:`Class definitions:`
"""
from apps.account.forms import BasePasswordProfileEditForm


class ProfileEditForm(BasePasswordProfileEditForm):
    '''
    Edit manager profile (personalia) form
    '''
    class Meta(BasePasswordProfileEditForm.Meta):
        exclude = BasePasswordProfileEditForm.Meta.exclude + (
            'BSN', 'local_hospital_number',
            'hospital',)
        fieldsets = (
            (None, {'fields': ('title', 'first_name', 'initials',
                               'prefix', 'last_name', 'gender',
                               'date_of_birth')}),
            (None, {'fields': ('mobile_number', 'mobile_number2',
                               'email', 'email2',
                               'change_password')}),
            ('change_password', {'fields': ('password', 'password2')}),
        )

# -*- coding: utf-8 -*-
"""
This module contains extra custom filters functions
for Django templates.

:subtitle:`Function definitions:`
"""

from django import template
from core.encryption.symmetric import decrypt as symmetric_decrypt
from core.encryption.random import randomkey

register = template.Library()


@register.filter(name='default')
def default(value, arg):
    '''
    Function which overrides the default template tag.
    (Since the original tag would display zero as -)
    '''
    if value != 0:
        return value or arg
    else:
        return value


@register.filter(name='comma')
def comma(value):
    '''
    Function which overrides the default template tag.
    (Since the original tag would display zero as -)
    '''
    if value:
        return str(value).replace('.', ',')

    return value


@register.filter(name='decrypt')
def decrypt(value, arg='None'):
    '''
    Try to decrypt the value with use of the personal key.
    '''
    if 'personal_encryption_key' in arg.session:
        decrypt_key = arg.session['personal_encryption_key']
        return symmetric_decrypt(str(value), decrypt_key)
    return '*********'


@register.filter(name='classname')
def classname(value, arg='None'):
    '''
    Get the class_name of the value (=class instance)
    '''
    if value:
        return value.__class__.__name__
    return ''


@register.filter(name='moduleclassname')
def moduleclassname(value, arg='None'):
    '''
    Get the moduleclassname of the value (=class instance)
    '''
    if value:
        return '{0}:{1}'.format(value.__class__.__module__,
                                value.__class__.__name__)
    return ''


@register.filter(name='checkgroup')
def checkgroup(value, arg='None'):
    '''
    Check which group the value (=user) is in.
    '''
    if value:
        return value.in_group(arg)
    return False


@register.filter(name='get_random_session_key')
def get_random_session_key(value, request=None):
    '''
    Store a value in the session with a random key
    used for hiding the id's of all healthpersons.
    '''
    session_key = None

    value = 'storage_' + str(value)

    if value not in list(request.session.values()):
        # add
        session_key = randomkey()

        # make sure it is unique
        while session_key in request.session:
            session_key = randomkey()

        request.session[session_key] = value
    else:
        # find the key
        for key1, value1 in list(request.session.items()):
            if value1 == value:
                session_key = key1
                break
    # return the key
    return session_key


@register.filter(name='get_field')
def get_field(value, field=None):
    if not hasattr(value, 'get_field'):
        return None
    return value.get_field(field)


@register.filter(name='get_question_nr')
def get_question_nr(value, field=None):
    '''
    Get the question number of a question...
    #Note it would be a speed improvement to move
    this as a attribute on the fields in the forms.
    '''
    number = ''
    fieldset_counter = 0
    field_counter = 0
    for fieldset in value.fieldsets():

        if not fieldset[0]:
            fieldset_counter = fieldset_counter + 1
            old_field_counter = None
        else:
            if fieldset_counter != 0:
                old_field_counter = field_counter
                field_counter = 0
            else:
                old_field_counter = 0

        for field_set_field in fieldset[1]:
            field_counter = field_counter + 1
            if field_set_field.name == field.name:
                if fieldset[0] and fieldset_counter != 0:

                    if hasattr(value, 'field_nrs'):
                        number = str(old_field_counter) + '.' +\
                            str(value.field_nrs[field_set_field.name])
                    else:
                        number = str(old_field_counter) + '.' +\
                            str(field_counter)
                else:
                    if hasattr(value, 'field_nrs'):
                        number = str(value.field_nrs[field_set_field.name])
                    else:
                        number = str(field_counter)

        if old_field_counter:
            field_counter = old_field_counter

    return number

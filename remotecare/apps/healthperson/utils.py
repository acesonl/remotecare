# -*- coding: utf-8 -*-
"""
This util module provides help functions
for checking if an user is in the appropiate
group.

:subtitle:`Function definitions:`
"""
login_url = '/login/?next=/'


# Helper function for checking group access
def is_allowed(user, white_list=[]):
    """
    Checks if the user's group is in provided list with
    white listed groups.

    Args:
        - user: the user instance to check
        - while_list: a list with group names the user should be in.
    Returns:
        True is the user is in provided group white_list
    """
    if user and hasattr(user, 'default_group'):
        return user.default_group in white_list
    return False


def is_allowed_patient(user):
    """
    Shortcut for checking if the user
    is a patient
    """
    return is_allowed(user, ['patients'])


def is_allowed_secretary(user):
    """
    Shortcut for checking if the user
    is a secretary
    """
    return is_allowed(user, ['secretariat'])


def is_allowed_manager(user):
    """
    Shortcut for checking if the user
    is a manager
    """
    return is_allowed(user, ['managers'])


def is_allowed_manager_and_secretary(user):
    """
    Shortcut for checking if the user
    is a manager or secretary
    """
    return is_allowed(user, ['managers', 'secretariat'])


def is_allowed_manager_and_healthprofessional(user):
    """
    Shortcut for checking if the user
    is a manager or healthprofessional
    """
    return is_allowed(user, ['managers', 'healthprofessionals'])


def is_allowed_healthprofessional(user):
    """
    Shortcut for checking if the user
    is an healthprofessional
    """
    return is_allowed(user, ['healthprofessionals'])


def is_allowed_patient_admins(user):
    """
    Shortcut for checking if the user
    is a manager, secretary or healthprofessional
    """
    return is_allowed(user, ['secretariat', 'healthprofessionals', 'managers'])

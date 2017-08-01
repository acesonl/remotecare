# -*- coding: utf-8 -*-
"""
This module contains the manager model definition.
The manager is coupled to a :class:`apps.account.models.User`
instance via the :class:`apps.healthperson.models.HealthPerson` baseclass.

Inheritance-diagram:

.. inheritance-diagram::\
    apps.healthperson.management.models.Manager

:subtitle:`Class definitions:`
"""
from django.utils.translation import ugettext as _
from apps.healthperson.models import HealthPerson


class Manager(HealthPerson):
    '''
    Stores the manager with no extra information.
    '''
    @property
    def name(self):
        return _('Manager')
